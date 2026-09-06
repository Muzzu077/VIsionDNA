"""
WebSocket connection manager with channel-based broadcast support.
"""

import asyncio
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from fastapi import WebSocket

from app.core.logging import get_logger

logger = get_logger(__name__)


class Channel(str, Enum):
    LIVE = "live"
    ALERTS = "alerts"
    DIGITAL_TWIN = "digital-twin"


class EventType(str, Enum):
    PERSON_DETECTED = "person_detected"
    PERSON_UPDATED = "person_updated"
    ACTIVITY_CHANGED = "activity_changed"
    RISK_UPDATED = "risk_updated"
    PREDICTION_GENERATED = "prediction_generated"
    ALERT_CREATED = "alert_created"
    CAMERA_STATUS_CHANGED = "camera_status_changed"


class ConnectionManager:
    """Manages WebSocket connections across multiple channels."""

    def __init__(self) -> None:
        # channel -> set of (connection_id, websocket)
        self._channels: Dict[Channel, Dict[str, WebSocket]] = {
            ch: {} for ch in Channel
        }
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, channel: Channel) -> str:
        """Accept a WebSocket connection and register it on a channel."""
        await websocket.accept()
        connection_id = str(uuid4())
        async with self._lock:
            self._channels[channel][connection_id] = websocket
        logger.info(
            "ws_connect",
            channel=channel.value,
            connection_id=connection_id,
            total=len(self._channels[channel]),
        )
        return connection_id

    async def disconnect(self, connection_id: str, channel: Channel) -> None:
        """Remove a connection from a channel."""
        async with self._lock:
            self._channels[channel].pop(connection_id, None)
        logger.info(
            "ws_disconnect",
            channel=channel.value,
            connection_id=connection_id,
            remaining=len(self._channels[channel]),
        )

    async def broadcast(
        self,
        channel: Channel,
        event_type: EventType,
        data: Dict[str, Any],
    ) -> None:
        """Send a message to all connections on a channel."""
        message = self._build_message(event_type, data)
        payload = json.dumps(message, default=str)

        async with self._lock:
            connections = dict(self._channels[channel])

        stale: List[str] = []
        for conn_id, ws in connections.items():
            try:
                await ws.send_text(payload)
            except Exception:
                stale.append(conn_id)

        # Clean up broken connections
        if stale:
            async with self._lock:
                for conn_id in stale:
                    self._channels[channel].pop(conn_id, None)

    async def send_to(
        self,
        connection_id: str,
        channel: Channel,
        event_type: EventType,
        data: Dict[str, Any],
    ) -> bool:
        """Send a message to a specific connection. Returns False if not found."""
        async with self._lock:
            ws = self._channels[channel].get(connection_id)
        if ws is None:
            return False

        message = self._build_message(event_type, data)
        try:
            await ws.send_text(json.dumps(message, default=str))
            return True
        except Exception:
            async with self._lock:
                self._channels[channel].pop(connection_id, None)
            return False

    def get_connection_count(self, channel: Optional[Channel] = None) -> int:
        """Return the number of active connections, optionally filtered by channel."""
        if channel is not None:
            return len(self._channels[channel])
        return sum(len(conns) for conns in self._channels.values())

    def get_all_channels_info(self) -> Dict[str, int]:
        """Return connection counts per channel."""
        return {ch.value: len(conns) for ch, conns in self._channels.items()}

    @staticmethod
    def _build_message(event_type: EventType, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "event_id": str(uuid4()),
            "event_type": event_type.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }


# Global singleton
manager = ConnectionManager()
