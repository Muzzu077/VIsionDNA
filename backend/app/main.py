"""
VisionDNA FastAPI application entry point.
"""

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    activities,
    alerts,
    analytics,
    auth,
    cameras,
    digital_twin,
    persons,
    predictions,
    risks,
    system,
    zones,
)
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.init_db import init_db
from app.services.ai_service import ai_service
from app.websocket.manager import Channel, manager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    setup_logging()
    logger.info(
        "application_startup",
        app=settings.APP_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        demo_mode=settings.DEMO_MODE,
    )

    # Ensure storage directories exist
    os.makedirs(settings.VIDEO_STORAGE_PATH, exist_ok=True)
    os.makedirs(settings.MODEL_PATH, exist_ok=True)

    # Initialize Database and Seed Data
    try:
        await init_db()
    except Exception as exc:
        logger.error("database_init_error", error=str(exc))

    # Demo Mode is an explicitly labelled deterministic scenario. It does not
    # represent camera-derived observations or trained-model predictions.
    demo_task = None
    if settings.DEMO_MODE:
        demo_task = asyncio.create_task(ai_service.start_default_demo())

    yield

    if demo_task is not None:
        ai_service.stop_stream("demo-camera")
        demo_task.cancel()
    logger.info("application_shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-based visual digital twin system for real-time activity recognition, "
    "risk assessment, and predictive safety analytics.",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ───────────────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/api")
app.include_router(cameras.router, prefix="/api")
app.include_router(persons.router, prefix="/api")
app.include_router(activities.router, prefix="/api")
app.include_router(risks.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(digital_twin.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(system.router, prefix="/api")

# ── Static files (if directory exists) ────────────────────────────────────────

_static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")


# ── Health check at root ──────────────────────────────────────────────────────


@app.get("/", tags=["root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
    }


# ── WebSocket endpoints ──────────────────────────────────────────────────────


@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    """Real-time live feed events (person detection, activity, etc.)."""
    conn_id = await manager.connect(websocket, Channel.LIVE)
    try:
        while True:
            # Keep connection alive; clients can send pings or commands
            data = await websocket.receive_text()
            # Echo back as acknowledgement
            await websocket.send_text(f'{{"ack": true, "received": {data}}}')
    except WebSocketDisconnect:
        await manager.disconnect(conn_id, Channel.LIVE)


@app.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """Real-time alert notifications."""
    conn_id = await manager.connect(websocket, Channel.ALERTS)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f'{{"ack": true, "received": {data}}}')
    except WebSocketDisconnect:
        await manager.disconnect(conn_id, Channel.ALERTS)


@app.websocket("/ws/digital-twin")
async def websocket_twin_endpoint(websocket: WebSocket):
    """Real-time digital twin state updates."""
    conn_id = await manager.connect(websocket, Channel.DIGITAL_TWIN)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f'{{"ack": true, "received": {data}}}')
    except WebSocketDisconnect:
        await manager.disconnect(conn_id, Channel.DIGITAL_TWIN)
