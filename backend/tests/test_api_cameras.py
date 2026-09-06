"""
Tests for Camera API routes.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_camera_crud_lifecycle(client: AsyncClient, admin_user: dict, sample_environment: dict):
    env_id = str(sample_environment.id)

    # 1. Create Camera
    create_payload = {
        "environment_id": env_id,
        "name": "Lab Entry Camera",
        "source_type": "WEBCAM",
        "source_url": "0",
        "fps": 30.0,
        "resolution_width": 1920,
        "resolution_height": 1080,
    }
    create_resp = await client.post("/api/cameras", headers=admin_user["headers"], json=create_payload)
    assert create_resp.status_code == 201
    cam_data = create_resp.json()
    cam_id = cam_data["id"]
    assert cam_data["name"] == "Lab Entry Camera"

    # 2. Get Camera by ID
    get_resp = await client.get(f"/api/cameras/{cam_id}", headers=admin_user["headers"])
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == cam_id

    # 3. List Cameras
    list_resp = await client.get(f"/api/cameras?environment_id={env_id}", headers=admin_user["headers"])
    assert list_resp.status_code == 200
    assert any(c["id"] == cam_id for c in list_resp.json())

    # 4. Update Camera
    update_payload = {"name": "Lab Entry Camera - Updated", "fps": 25.0}
    update_resp = await client.put(f"/api/cameras/{cam_id}", headers=admin_user["headers"], json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Lab Entry Camera - Updated"
    assert update_resp.json()["fps"] == 25.0

    # 5. Test Camera Start/Stop
    start_resp = await client.post(f"/api/cameras/{cam_id}/start", headers=admin_user["headers"])
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] in ["started", "already running"]

    stop_resp = await client.post(f"/api/cameras/{cam_id}/stop", headers=admin_user["headers"])
    assert stop_resp.status_code == 200
    assert stop_resp.json()["status"] == "stopped"

    # 6. Delete Camera
    del_resp = await client.delete(f"/api/cameras/{cam_id}", headers=admin_user["headers"])
    assert del_resp.status_code == 204
