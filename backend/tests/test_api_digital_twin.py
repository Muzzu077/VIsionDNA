"""
Tests for Digital Twin state API routes.
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Person, PersonStatus, DigitalTwinState


@pytest.mark.asyncio
async def test_digital_twin_endpoints(client: AsyncClient, admin_user: dict, sample_environment: dict, db_session: AsyncSession):
    # Create test person
    person = Person(
        tracking_id="P001",
        environment_id=sample_environment.id,
        status=PersonStatus.ACTIVE,
    )
    db_session.add(person)
    await db_session.commit()
    await db_session.refresh(person)

    # Add digital twin state
    twin_state = DigitalTwinState(
        person_id=person.id,
        current_activity="walking",
        position_x=450.0,
        position_y=280.0,
        posture="upright",
        movement_speed=1.45,
        zone="Main Sector",
        risk_score=35.0,
        risk_level="MEDIUM",
        state_json={"details": "Approaching north boundary"},
    )
    db_session.add(twin_state)
    await db_session.commit()

    # 1. List Digital Twins
    resp = await client.get("/api/digital-twins", headers=admin_user["headers"])
    assert resp.status_code == 200
    twins = resp.json()
    assert len(twins) >= 1
    assert any(t["person_id"] == str(person.id) for t in twins)

    # 2. Get Person Twin History
    person_resp = await client.get(f"/api/digital-twins/{person.id}", headers=admin_user["headers"])
    assert person_resp.status_code == 200
    p_twins = person_resp.json()
    assert len(p_twins) >= 1
    assert p_twins[0]["current_activity"] == "walking"
    assert p_twins[0]["risk_level"] == "MEDIUM"
