# zeus/core/voice_ws.py — Phaos WebSocket + HTTP publish for voice visualization
from __future__ import annotations

import asyncio
import os

from fastapi import APIRouter, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from zeus.voice.state import VoiceStatePublishBody, voice_state_message

router = APIRouter(tags=["phaos"])


class PublishAck(BaseModel):
    ok: bool = True


def _check_publish_secret(x_secret: str | None) -> None:
    expected = os.getenv("ZEUS_VOICE_STATE_SECRET")
    if not expected:
        return
    if x_secret != expected:
        raise HTTPException(status_code=401, detail="invalid or missing voice state secret")


@router.post("/voice-state/publish", response_model=PublishAck)
async def publish_voice_state(
    body: VoiceStatePublishBody,
    request: Request,
    x_zeus_voice_state_secret: str | None = Header(default=None, alias="X-Zeus-Voice-State-Secret"),
) -> PublishAck:
    """
    Push a voice-state event into the hub (used by host-native Orpheus).

    When ZEUS_VOICE_STATE_SECRET is set, callers must send X-Zeus-Voice-State-Secret.
    """
    _check_publish_secret(x_zeus_voice_state_secret)
    hub = request.app.state.voice_hub
    msg = voice_state_message(
        body.state,
        audio_level=body.audio_level,
        metadata=body.metadata,
        timestamp_ms=body.timestamp_ms,
    )
    await hub.publish(msg)
    return PublishAck()


@router.websocket("/ws/voice-state")
async def websocket_voice_state(websocket: WebSocket) -> None:
    await websocket.accept()
    hub = websocket.app.state.voice_hub
    q = await hub.subscribe()
    try:
        await websocket.send_json(hub.last_message)
        while True:
            recv_task = asyncio.create_task(websocket.receive_text())
            queue_task = asyncio.create_task(q.get())
            done, pending = await asyncio.wait(
                {recv_task, queue_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for t in pending:
                t.cancel()
            if queue_task in done:
                recv_task.cancel()
                try:
                    await recv_task
                except asyncio.CancelledError:
                    pass
                except WebSocketDisconnect:
                    raise
                msg = queue_task.result()
                await websocket.send_json(msg)
            else:
                queue_task.cancel()
                try:
                    await recv_task
                except WebSocketDisconnect:
                    raise
    except WebSocketDisconnect:
        pass
    finally:
        await hub.unsubscribe(q)
