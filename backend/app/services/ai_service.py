import asyncio
from app.ai.simulation import SimulationEngine
from app.schemas.schemas import DigitalTwinStateBase
from app.websocket.manager import manager as connection_manager
from app.websocket.manager import Channel, EventType
from typing import Optional

class AIService:
    def __init__(self, fps: float = 2.0):
        self.fps = fps
        self.sleep_time = 1.0 / self.fps
        self._running_streams = {}

    def is_stream_running(self, camera_id: str) -> bool:
        return self._running_streams.get(camera_id, False)

    def stop_stream(self, camera_id: str):
        if camera_id in self._running_streams:
            self._running_streams[camera_id] = False

    async def start_demo_stream(self, camera_id: str):
        """
        Runs the simulation loop, maps to schema, and broadcasts via websockets.
        """
        if self.is_stream_running(camera_id):
            return

        self._running_streams[camera_id] = True
        simulation_engine = SimulationEngine()

        try:
            while self._running_streams.get(camera_id, False):
                # 1. Get pipeline output from mock SimulationEngine
                state_dict = simulation_engine.generate_frame_state(camera_id)

                # 2. Map to DigitalTwinState Pydantic model
                # Assuming state_dict matches the schema structurally or we extract fields
                # we'll extract relevant fields for the twin broadcast
                
                twin_state = DigitalTwinStateBase(
                    current_activity=state_dict.get("activity"),
                    position_x=float(state_dict.get("x_pos", 0)),
                    position_y=float(state_dict.get("y_pos", 0)),
                    movement_speed=float(state_dict.get("velocity", 0)),
                    risk_score=float(state_dict.get("risk_score", 0)),
                    risk_level=state_dict.get("risk_level", "LOW"),
                    state_json=state_dict  # embed full raw state for advanced clients
                )

                # 3. Broadcast to websockets via ConnectionManager
                live_payload = {
                    "camera_id": camera_id,
                    "state": state_dict
                }
                await connection_manager.broadcast(Channel.LIVE, EventType.PERSON_UPDATED, live_payload)
                
                twin_payload = {
                    "camera_id": camera_id,
                    "twin_state": twin_state.model_dump()
                }
                await connection_manager.broadcast(Channel.DIGITAL_TWIN, EventType.PERSON_UPDATED, twin_payload)

                # 4. If unexpected / alert conditions are met, broadcast to alerts
                # E.g. risk level is HIGH or active alert in state
                if state_dict.get("alert_triggered"):
                    alert_payload = {
                        "camera_id": camera_id,
                        "message": f"Alert triggered for camera {camera_id}: {state_dict.get('prediction', 'Unknown')}",
                        "risk_score": state_dict.get("risk_score")
                    }
                    await connection_manager.broadcast(Channel.ALERTS, EventType.ALERT_CREATED, alert_payload)

                # 5. Respect FPS configuration
                await asyncio.sleep(self.sleep_time)

        finally:
            self._running_streams.pop(camera_id, None)

    async def start_default_demo(self) -> None:
        """Start the built-in demonstration camera once for all connected clients."""
        await self.start_demo_stream("demo-camera")

ai_service = AIService(fps=2.0)
