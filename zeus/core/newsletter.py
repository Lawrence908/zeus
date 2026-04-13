"""zeus/core/newsletter.py — Newsletter digest API router.

Endpoints:
  POST /api/newsletter/digest      — Generate summary + TTS audio from recent newsletters
  POST /api/newsletter/digest-text — Generate digest from pasted text
  GET  /api/newsletter/digests     — List past digest entries
  GET  /api/newsletter/advice      — List all per-category advice documents
  GET  /api/newsletter/advice/{category} — Get single category advice document
  GET  /api/newsletter/audio/{filename}  — Serve generated audio files
  GET  /newsletters                — Web UI page
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from zeus.core.query import _run_llm, _run_llm_stream

# In-process lock for manifest read-modify-write cycles
_manifest_lock = threading.Lock()

logger = logging.getLogger("zeus.newsletter")

router = APIRouter(tags=["newsletter"])

_AUDIO_DIR = Path(os.getenv("NEWSLETTER_AUDIO_DIR", "zeus/data/audio"))
_MANIFEST_DIR = Path("zeus/data/newsletters")
_MANIFEST_PATH = _MANIFEST_DIR / "manifest.json"
_ADVICE_DIR = _MANIFEST_DIR / "advice"
_STATIC_DIR = Path(__file__).resolve().parent / "static"

# Filename validation: alphanumeric, underscores, hyphens, dots only
_SAFE_FILENAME_RE = re.compile(r"^[a-zA-Z0-9_\-]+\.wav$")

_SUMMARIZE_SYSTEM_PROMPT = """\
You are a newsletter summarizer for a personal AI assistant. \
Distill the key information from the provided newsletter(s) into:
- 5-8 bullet points (one-liners, plain English, no markdown formatting)
- 1-2 pieces of actionable advice for the reader

Keep it concise and voice-friendly (suitable for text-to-speech).
Do not include URLs in bullet points.

Return your response as valid JSON with this exact structure:
{"summary": "A 2-3 sentence overview", "bullets": ["point 1", "point 2", ...], "advice": "Your actionable advice"}
"""

_ADVICE_SYNTHESIS_PROMPT = """\
You maintain a running advice document for a personal AI assistant user. \
You will receive the current advice document (which may be empty for a new category) \
and new advice from a recent newsletter digest.

Your job is to produce an updated advice document that:
- Integrates the new advice with existing advice, removing duplicates
- Keeps advice actionable and specific, not generic
- Groups related advice together under short headings if there are multiple topics
- Removes advice that has been superseded by newer, more relevant guidance
- Stays concise: aim for 5-15 bullet points total, organized by topic
- Uses plain language, no markdown formatting beyond simple headings and bullets

Return your response as valid JSON with this exact structure:
{"advice": "The full updated advice document as a single string with newlines", "updated_at": "reason for changes in this update"}
"""


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class DigestRequest(BaseModel):
    newsletter_type: str = "all"
    num_recent: int = Field(default=1, ge=1, le=10)


class DigestEntry(BaseModel):
    id: str
    newsletter_type: str
    date: str
    summary: str
    bullets: list[str]
    advice: str
    audio_file: str | None = None
    audio_url: str | None = None
    generated_at: str


class DigestResponse(BaseModel):
    digest: DigestEntry
    newsletters_used: int


class QuickDigestRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=100_000)


class AdviceDocument(BaseModel):
    category: str
    advice: str
    updated_at: str
    update_count: int = 0


class AdviceListResponse(BaseModel):
    documents: list[AdviceDocument]


class DigestsListResponse(BaseModel):
    digests: list[DigestEntry]


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------

def _ensure_dirs() -> None:
    _AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    _MANIFEST_DIR.mkdir(parents=True, exist_ok=True)


def _load_manifest() -> dict:
    if not _MANIFEST_PATH.exists():
        return {"digests": []}
    try:
        return json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.warning("corrupt manifest, resetting")
        return {"digests": []}


def _save_manifest(manifest: dict) -> None:
    _ensure_dirs()
    tmp = _MANIFEST_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    tmp.replace(_MANIFEST_PATH)


def _append_digest(manifest: dict, entry: dict) -> dict:
    manifest.setdefault("digests", []).insert(0, entry)
    # Keep last 50 digests
    manifest["digests"] = manifest["digests"][:50]
    return manifest


# ---------------------------------------------------------------------------
# Per-category advice documents
# ---------------------------------------------------------------------------

_SAFE_CATEGORY_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")


def _advice_path(category: str) -> Path:
    return _ADVICE_DIR / f"{category}.json"


def _load_advice(category: str) -> dict:
    path = _advice_path(category)
    if not path.exists():
        return {"category": category, "advice": "", "updated_at": "", "update_count": 0}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.warning("corrupt advice file for %s, resetting", category)
        return {"category": category, "advice": "", "updated_at": "", "update_count": 0}


def _save_advice(doc: dict) -> None:
    _ADVICE_DIR.mkdir(parents=True, exist_ok=True)
    path = _advice_path(doc["category"])
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    tmp.replace(path)


def _load_all_advice() -> list[dict]:
    if not _ADVICE_DIR.exists():
        return []
    docs = []
    for path in sorted(_ADVICE_DIR.glob("*.json")):
        try:
            docs.append(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return docs


async def _synthesize_advice(category: str, new_advice: str) -> dict:
    """Merge new digest advice into the running advice document for a category."""
    existing = _load_advice(category)
    current_advice = existing.get("advice", "")

    if not new_advice.strip():
        return existing

    user_prompt = (
        f"Category: {category}\n\n"
        f"Current advice document:\n{current_advice or '(empty, this is the first digest for this category)'}\n\n"
        f"New advice from latest digest:\n{new_advice}"
    )

    chunks: list[str] = []
    async for chunk in _run_llm_stream(
        system=_ADVICE_SYNTHESIS_PROMPT,
        user_prompt=user_prompt,
        max_tokens=1024,
    ):
        chunks.append(chunk)
    raw = "".join(chunks)

    try:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
        else:
            parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Advice synthesis response was not valid JSON, appending raw")
        parsed = {"advice": f"{current_advice}\n\n{new_advice}".strip(), "updated_at": "append fallback"}

    now_iso = datetime.now(timezone.utc).isoformat()
    doc = {
        "category": category,
        "advice": str(parsed.get("advice", "")),
        "updated_at": now_iso,
        "update_count": existing.get("update_count", 0) + 1,
    }

    with _manifest_lock:
        _save_advice(doc)

    logger.info("updated advice for %s (update #%d): %s", category, doc["update_count"], parsed.get("updated_at", ""))
    return doc


# ---------------------------------------------------------------------------
# LLM summarization
# ---------------------------------------------------------------------------

async def _summarize_newsletters(texts: list[str]) -> dict:
    """Call Zeus LLM to summarize newsletter text(s) into structured JSON."""
    combined = "\n\n---\n\n".join(texts)
    # Truncate if extremely long (keep ~4k words for context)
    words = combined.split()
    if len(words) > 4000:
        combined = " ".join(words[:4000]) + "\n\n[truncated]"

    chunks: list[str] = []
    async for chunk in _run_llm_stream(
        system=_SUMMARIZE_SYSTEM_PROMPT,
        user_prompt=f"Summarize the following newsletter(s):\n\n{combined}",
        max_tokens=1024,
    ):
        chunks.append(chunk)
    raw = "".join(chunks)

    # Parse JSON from LLM response
    try:
        # Try to extract JSON from response (LLM may wrap in markdown code block)
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
        else:
            parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("LLM response was not valid JSON, using raw text")
        parsed = {
            "summary": raw[:500],
            "bullets": [line.strip("- ").strip() for line in raw.split("\n") if line.strip().startswith("-")][:8],
            "advice": "",
        }

    return {
        "summary": str(parsed.get("summary", "")),
        "bullets": [str(b) for b in parsed.get("bullets", [])],
        "advice": str(parsed.get("advice", "")),
    }


# ---------------------------------------------------------------------------
# TTS audio generation
# ---------------------------------------------------------------------------

async def _generate_audio(summary_dict: dict) -> str | None:
    """Generate TTS audio from summary. Returns filename or None if unavailable."""
    try:
        from zeus.voice.tts import VoiceboxTTS
    except ImportError:
        logger.info("VoiceboxTTS not available, skipping audio")
        return None

    voicebox_url = os.getenv("VOICEBOX_URL", "").strip()
    voice_id = os.getenv("ORPHEUS_VOICE_ID", "").strip()
    if not voicebox_url:
        logger.info("VOICEBOX_URL not set, skipping audio generation")
        return None

    # Build podcast script from summary
    bullets_text = ". ".join(summary_dict["bullets"])
    script = (
        f"Here's your newsletter digest. {summary_dict['summary']} "
        f"Key highlights: {bullets_text}. "
    )
    if summary_dict.get("advice"):
        script += f"My advice: {summary_dict['advice']}"

    try:
        tts = VoiceboxTTS(url=voicebox_url, voice_id=voice_id)
        audio_bytes = await tts.synthesize(script)
    except Exception as exc:
        logger.warning("TTS synthesis failed: %s", exc)
        return None

    _ensure_dirs()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:8]
    filename = f"newsletter_{ts}_{short_id}.wav"
    filepath = _AUDIO_DIR / filename
    filepath.write_bytes(audio_bytes)
    logger.info("saved audio: %s (%d bytes)", filepath, len(audio_bytes))
    return filename


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@router.post("/api/newsletter/digest", response_model=DigestResponse)
async def generate_newsletter_digest(body: DigestRequest) -> DigestResponse:
    """Fetch recent newsletters, summarize via LLM, optionally generate TTS audio."""
    from zeus.ingest.sources.newsletter import NewsletterSource

    try:
        config = NewsletterSource.from_env(since_days=14)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    source = NewsletterSource(config=config)
    try:
        newsletters = await asyncio.to_thread(
            source.fetch_newsletters_raw,
            newsletter_type=body.newsletter_type,
            num_recent=body.num_recent,
        )
    except Exception as exc:
        logger.error("IMAP fetch failed: %s", exc)
        raise HTTPException(
            status_code=502, detail=f"Newsletter fetch failed: {exc}"
        )

    if not newsletters:
        raise HTTPException(
            status_code=404,
            detail=f"No newsletters found for type={body.newsletter_type!r}",
        )

    # Summarize
    texts = [
        f"[{nl.newsletter_type.upper()}] {nl.subject}\n{nl.body}"
        for nl in newsletters
    ]
    summary_dict = await _summarize_newsletters(texts)

    # Generate audio (best-effort)
    audio_file = await _generate_audio(summary_dict)

    # Build digest entry
    now_iso = datetime.now(timezone.utc).isoformat()
    entry = DigestEntry(
        id=str(uuid.uuid4()),
        newsletter_type=body.newsletter_type,
        date=newsletters[0].date_iso or now_iso,
        summary=summary_dict["summary"],
        bullets=summary_dict["bullets"],
        advice=summary_dict["advice"],
        audio_file=audio_file,
        audio_url=f"/api/newsletter/audio/{audio_file}" if audio_file else None,
        generated_at=now_iso,
    )

    # Save to manifest (locked to prevent concurrent corruption)
    with _manifest_lock:
        manifest = _load_manifest()
        _append_digest(manifest, entry.model_dump())
        _save_manifest(manifest)

    # Synthesize advice into the running category document
    if summary_dict["advice"]:
        await _synthesize_advice(body.newsletter_type, summary_dict["advice"])

    return DigestResponse(digest=entry, newsletters_used=len(newsletters))


@router.post("/api/newsletter/digest-text", response_model=DigestResponse)
async def generate_digest_from_text(body: QuickDigestRequest) -> DigestResponse:
    """Summarize pasted text through the newsletter digest pipeline."""
    summary_dict = await _summarize_newsletters([body.text])

    audio_file = await _generate_audio(summary_dict)

    now_iso = datetime.now(timezone.utc).isoformat()
    entry = DigestEntry(
        id=str(uuid.uuid4()),
        newsletter_type="quick",
        date=now_iso,
        summary=summary_dict["summary"],
        bullets=summary_dict["bullets"],
        advice=summary_dict["advice"],
        audio_file=audio_file,
        audio_url=f"/api/newsletter/audio/{audio_file}" if audio_file else None,
        generated_at=now_iso,
    )

    with _manifest_lock:
        manifest = _load_manifest()
        _append_digest(manifest, entry.model_dump())
        _save_manifest(manifest)

    # Synthesize advice into the "quick" category document
    if summary_dict["advice"]:
        await _synthesize_advice("quick", summary_dict["advice"])

    return DigestResponse(digest=entry, newsletters_used=1)


@router.get("/api/newsletter/digests", response_model=DigestsListResponse)
async def list_digests(limit: int = 10) -> DigestsListResponse:
    """List past newsletter digests."""
    manifest = _load_manifest()
    digests = manifest.get("digests", [])[:max(1, min(limit, 50))]
    return DigestsListResponse(
        digests=[DigestEntry(**d) for d in digests],
    )


@router.get("/api/newsletter/advice", response_model=AdviceListResponse)
async def list_advice_documents() -> AdviceListResponse:
    """List all per-category advice documents."""
    docs = _load_all_advice()
    return AdviceListResponse(
        documents=[AdviceDocument(**d) for d in docs if d.get("advice")],
    )


@router.get("/api/newsletter/advice/{category}", response_model=AdviceDocument)
async def get_advice_document(category: str) -> AdviceDocument:
    """Get the running advice document for a specific category."""
    if not _SAFE_CATEGORY_RE.match(category):
        raise HTTPException(status_code=400, detail="Invalid category name")
    doc = _load_advice(category)
    if not doc.get("advice"):
        raise HTTPException(status_code=404, detail=f"No advice document for category {category!r}")
    return AdviceDocument(**doc)


@router.get("/api/newsletter/audio/{filename}")
async def get_newsletter_audio(filename: str) -> FileResponse:
    """Serve a generated newsletter audio file."""
    if not _SAFE_FILENAME_RE.match(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    filepath = _AUDIO_DIR / filename
    if not filepath.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(str(filepath), media_type="audio/wav")


@router.get("/api/newsletter/sources")
async def list_newsletter_sources() -> dict:
    """Return configured newsletter source types for UI population."""
    from zeus.ingest.sources.newsletter import NewsletterSource

    try:
        config = NewsletterSource.from_env()
        return {
            "sources": [
                {"type": ntype, "email": email}
                for ntype, email in config.sources.items()
            ]
        }
    except ValueError:
        return {"sources": []}


@router.get("/newsletters", include_in_schema=False)
async def newsletters_page() -> FileResponse:
    """Serve the newsletter digest web UI."""
    html_path = _STATIC_DIR / "newsletters.html"
    if not html_path.is_file():
        raise HTTPException(status_code=503, detail="Newsletter UI not found")
    return FileResponse(str(html_path), media_type="text/html")
