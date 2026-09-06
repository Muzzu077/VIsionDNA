"""
Tests for Zone API routes.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_zone_crud_lifecycle(client: AsyncClient, admin_user: dict, sample_environment: dict):
    env_id = str(sample_environment.id)

    # 1. Create Zone
    payload = {
        "environment_id": env_id,
        "name": "High Voltage Enclosure",
        "zone_type": "RESTRICTED",
        "polygon": [
            {"x": 600.0, "y": 100.0},
            {"x": 800.0, "y": 100.0},
            {"x": 800.0, "y": 300.0},
            {"x": 600.0, "y": 300.0},
        ],
        "color": "#ef4444",
        "risk_level": 85,
    }
    create_resp = await client.post("/api/zones", headers=admin_user["headers"], json=payload)
    assert create_resp.status_code == 201
    zone_data = create_resp.json()
    zone_id = zone_data["id"]
    assert zone_data["name"] == "High Voltage Enclosure"
    assert zone_data["zone_type"] == "RESTRICTED"

    # 2. Get Zone
    get_resp = await client.get(f"/api/zones/{zone_id}", headers=admin_user["headers"])
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == zone_id

    # 3. List Zones
    list_resp = await client.get(f"/api/zones?environment_id={env_id}", headers=admin_user["headers"])
    assert list_resp.status_code == 200
    assert any(z["id"] == zone_id for z in list_resp.json())

    # 4. Update Zone
    update_resp = await client.put(
        f"/api/zones/{zone_id}",
        headers=admin_user["headers"],
        json={"risk_level": 90, "name": "High Voltage Enclosure - Critical"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["risk_level"] == 90

    # 5. Delete Zone
    del_resp = await client.delete(f"/api/zones/{zone_id}", headers=admin_user["headers"])
    assert del_resp.status_code == 204
