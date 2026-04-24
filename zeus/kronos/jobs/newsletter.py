# zeus/kronos/jobs/newsletter.py — Kronos built-in for the morning digest.
#
# Replaces the unbuilt LAB-343 KAIROS observer plan: Kronos owns the schedule,
# this module just wraps the existing zeus.core.newsletter helpers so the
# digest pipeline (IMAP fetch → LLM summarize → TTS audio → manifest write →
# per-category advice synthesis) runs on a cron tick.
#
# The manual POST /api/newsletter/digest route stays as-is for UI triggers;
# the two code paths share helpers so both write to the same manifest.
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException

from zeus.core.newsletter import (
    DigestEntry,
    _append_digest,
    _generate_audio,
    _load_manifest,
    _manifest_lock,
    _save_manifest,
    _summarize_newsletters,
    _synthesize_advice,
)

logger = logging.getLogger("zeus.kronos.newsletter")


async def run_morning_digest(params: dict[str, Any]) -> dict[str, Any]:
    """
    Generate the morning newsletter digest and persist it to the manifest.

    Params:
      newsletter_type: "all" or a specific type key (default "all")
      num_recent:      1..10 newsletters to summarize (default 3)
    """
    newsletter_type = str(params.get("newsletter_type") or "all")
    num_recent = int(params.get("num_recent") or 3)
    num_recent = max(1, min(num_recent, 10))

    from zeus.ingest.sources.newsletter import NewsletterSource

    try:
        config = NewsletterSource.from_env(since_days=14)
    except ValueError as exc:
        raise RuntimeError(f"newsletter config missing: {exc}") from exc

    source = NewsletterSource(config=config)
    try:
        newsletters = await asyncio.to_thread(
            source.fetch_newsletters_raw,
            newsletter_type=newsletter_type,
            num_recent=num_recent,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise RuntimeError(f"IMAP fetch failed: {exc}") from exc

    if not newsletters:
        # Not a hard error for a cron — record a no-op summary and return.
        logger.info("kronos:newsletter no newsletters found for type=%s", newsletter_type)
        return {
            "status": "empty",
            "newsletter_type": newsletter_type,
            "newsletters_used": 0,
        }

    texts = [
        f"[{nl.newsletter_type.upper()}] {nl.subject}\n{nl.body}"
        for nl in newsletters
    ]
    summary_dict = await _summarize_newsletters(texts)
    audio_file = await _generate_audio(summary_dict)

    now_iso = datetime.now(timezone.utc).isoformat()
    entry = DigestEntry(
        id=str(uuid.uuid4()),
        newsletter_type=newsletter_type,
        date=newsletters[0].date_iso or now_iso,
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

    if summary_dict["advice"]:
        await _synthesize_advice(newsletter_type, summary_dict["advice"])

    return {
        "status": "ok",
        "newsletter_type": newsletter_type,
        "newsletters_used": len(newsletters),
        "digest_id": entry.id,
        "audio_url": entry.audio_url,
        "summary": entry.summary,
    }
