"""
Tests for Risk Events and Alerts API routes.
"""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Person, PersonStatus, RiskEvent, RiskSeverity, RiskEventStatus, Alert, AlertSeverity


@pytest.mark.asyncio
async def test_risk_and_alert_lifecycle(
    client: AsyncClient, admin_user: dict, sample_environment: dict, db_session: AsyncSession
):
    person = Person(
        tracking_id="P002",
        environment_id=sample_environment.id,
        status=PersonStatus.ACTIVE,
    )
    db_session.add(person)
    await db_session.commit()
    await db_session.refresh(person)

    # 1. Create Risk Event
    risk = RiskEvent(
        person_id=person.id,
        risk_type="restricted_zone_entry",
        risk_score=85.0,
        severity=RiskSeverity.CRITICAL,
        confidence=0.92,
        explanation="Person P002 entered Restricted Area",
        contributing_factors=[{"type": "Zone", "score": 20.0}],
        status=RiskEventStatus.DETECTED,
    )
    db_session.add(risk)
    await db_session.commit()
    await db_session.refresh(risk)

    # 2. List Risks
    list_resp = await client.get("/api/risks", headers=admin_user["headers"])
    assert list_resp.status_code == 200
    risks = list_resp.json()
    assert any(r["id"] == str(risk.id) for r in risks)

    # 3. Get Single Risk
    get_resp = await client.get(f"/api/risks/{risk.id}", headers=admin_user["headers"])
    assert get_resp.status_code == 200
    assert get_resp.json()["risk_type"] == "restricted_zone_entry"

    # 4. Acknowledge Risk
    ack_resp = await client.put(f"/api/risks/{risk.id}/acknowledge", headers=admin_user["headers"])
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "ACKNOWLEDGED"

    # 5. Create Alert linked to Risk
    alert = Alert(
        risk_event_id=risk.id,
        severity=AlertSeverity.CRITICAL,
        title="Unauthorized Restricted Zone Access",
        message="Immediate operator attention required at Sector 1",
        recommended_action="Dispatch security to Sector 1",
        acknowledged=False,
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)

    # 6. List Alerts
    alerts_resp = await client.get("/api/alerts", headers=admin_user["headers"])
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert any(a["id"] == str(alert.id) for a in alerts)

    # 7. Acknowledge Alert
    ack_alert_resp = await client.put(f"/api/alerts/{alert.id}/acknowledge", headers=admin_user["headers"])
    assert ack_alert_resp.status_code == 200
    assert ack_alert_resp.json()["acknowledged"] is True
