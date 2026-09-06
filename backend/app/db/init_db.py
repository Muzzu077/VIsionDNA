"""
Database initialization and seeding for VisionDNA.
"""

import uuid
from sqlalchemy import select
from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import hash_password
from app.db.base import Base
from app.db.database import engine, async_session_factory
from app.models.models import (
    User,
    UserRole,
    Environment,
    Camera,
    CameraSourceType,
    CameraStatus,
    Zone,
    ZoneType,
    MonitoredObject,
    ModelVersion,
)

logger = get_logger(__name__)


async def init_db() -> None:
    """Create all tables and seed initial data if needed."""
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # Check if users exist
        res = await session.execute(select(User).limit(1))
        if res.scalar_one_or_none() is None:
            logger.info("Seeding initial database data...")

            # 1. Users
            admin_user = User(
                name="VisionDNA Administrator",
                email="admin@visiondna.com",
                password_hash=hash_password("admin"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            operator_user = User(
                name="VisionDNA Operator",
                email="operator@visiondna.com",
                password_hash=hash_password("operator"),
                role=UserRole.OPERATOR,
                is_active=True,
            )
            viewer_user = User(
                name="VisionDNA Viewer",
                email="viewer@visiondna.com",
                password_hash=hash_password("viewer"),
                role=UserRole.VIEWER,
                is_active=True,
            )
            session.add_all([admin_user, operator_user, viewer_user])
            await session.flush()

            # 2. Environment
            env = Environment(
                name="Facility Alpha - Sector 1",
                description="Primary Industrial Monitoring Facility with Laboratory & Loading Dock",
                location="Building 4, Sector 1",
                configuration={"grid_width": 1000, "grid_height": 700, "coordinate_system": "2D_PIXELS"},
            )
            session.add(env)
            await session.flush()

            # 3. Cameras
            cam1 = Camera(
                environment_id=env.id,
                name="Main Hall - Entrance",
                source_type=CameraSourceType.WEBCAM,
                source_url="0",
                status=CameraStatus.ONLINE,
                fps=30.0,
                resolution_width=1920,
                resolution_height=1080,
                is_active=True,
            )
            cam2 = Camera(
                environment_id=env.id,
                name="Restricted Laboratory & Server Room",
                source_type=CameraSourceType.RTSP,
                source_url="rtsp://192.168.1.101:554/live",
                status=CameraStatus.ONLINE,
                fps=30.0,
                resolution_width=1920,
                resolution_height=1080,
                is_active=True,
            )
            cam3 = Camera(
                environment_id=env.id,
                name="Warehouse Loading Bay",
                source_type=CameraSourceType.HTTP,
                source_url="http://192.168.1.102/video",
                status=CameraStatus.OFFLINE,
                fps=15.0,
                resolution_width=1280,
                resolution_height=720,
                is_active=True,
            )
            session.add_all([cam1, cam2, cam3])

            # 4. Zones
            zone_safe = Zone(
                environment_id=env.id,
                name="Main Sector / Safe Lobby",
                zone_type=ZoneType.SAFE,
                polygon=[
                    {"x": 100.0, "y": 100.0},
                    {"x": 500.0, "y": 100.0},
                    {"x": 500.0, "y": 600.0},
                    {"x": 100.0, "y": 600.0},
                ],
                color="#22c55e",
                risk_level=0,
                is_active=True,
            )
            zone_restricted = Zone(
                environment_id=env.id,
                name="Restricted Area",
                zone_type=ZoneType.RESTRICTED,
                polygon=[
                    {"x": 590.0, "y": 55.0},
                    {"x": 770.0, "y": 55.0},
                    {"x": 770.0, "y": 205.0},
                    {"x": 590.0, "y": 205.0},
                ],
                color="#ef4444",
                risk_level=80,
                is_active=True,
            )
            session.add_all([zone_safe, zone_restricted])

            # 5. Monitored Objects
            obj1 = MonitoredObject(
                environment_id=env.id,
                name="High Voltage Panel",
                object_type="ELECTRICAL",
                position_x=720.0,
                position_y=120.0,
                risk_radius=60.0,
                metadata_={"hazard_level": "HIGH", "safe_distance_m": 2.0},
            )
            obj2 = MonitoredObject(
                environment_id=env.id,
                name="Hazardous Material Storage",
                object_type="HAZARDOUS",
                position_x=640.0,
                position_y=160.0,
                risk_radius=50.0,
                metadata_={"hazard_level": "CRITICAL", "ppe_required": True},
            )
            session.add_all([obj1, obj2])

            # 6. Model Versions
            models = [
                ModelVersion(
                    name="YOLOv8-HumanDetector",
                    version="v8.4.123",
                    model_type="OBJECT_DETECTION",
                    path="yolov8n.pt",
                    metrics={"mAP50": 0.892, "inference_ms": 12.4},
                    is_active=True,
                ),
                ModelVersion(
                    name="MediaPipe-Pose33",
                    version="v1.0.1",
                    model_type="POSE_ESTIMATION",
                    path="builtin",
                    metrics={"keypoint_precision": 0.941, "inference_ms": 15.1},
                    is_active=True,
                ),
                ModelVersion(
                    name="Heuristic-Temporal-Activity-Recognizer",
                    version="v1.0.0",
                    model_type="ACTIVITY_RECOGNITION",
                    path="builtin",
                    metrics={"accuracy": 0.912, "f1_score": 0.908},
                    is_active=True,
                ),
                ModelVersion(
                    name="Rule-Anomaly-Detector",
                    version="v1.0.0",
                    model_type="ANOMALY_DETECTION",
                    path="builtin",
                    metrics={"precision": 0.935, "false_alarm_rate": 0.042},
                    is_active=True,
                ),
                ModelVersion(
                    name="Multi-Factor-Risk-Engine",
                    version="v1.0.0",
                    model_type="RISK_SCORING",
                    path="builtin",
                    metrics={"roc_auc": 0.948, "latency_ms": 2.1},
                    is_active=True,
                ),
                ModelVersion(
                    name="Trajectory-Horizon-Predictor",
                    version="v1.0.0",
                    model_type="RISK_PREDICTION",
                    path="builtin",
                    metrics={"horizon_10s_accuracy": 0.884, "horizon_30s_accuracy": 0.762},
                    is_active=True,
                ),
            ]
            session.add_all(models)

            await session.commit()
            logger.info("Database seeding completed successfully.")
