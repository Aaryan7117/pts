"""
Integration tests for MediKiosk FastAPI REST Endpoints.
Verifies all public routes used by Web Kiosk, Mobile App (BYOD), and Doctor Dashboard.
"""

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


@pytest.fixture(scope="module")
def client():
    """TestClient fixture with FastAPI lifespan management (triggers init_db)."""
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    """Verify /api/health returns healthy status and endpoint inventory."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["sih_problem_id"] == "SIH26047"
    assert "llm_providers" in data
    assert "endpoints" in data


def test_encounter_bootstrap_and_queue(client):
    """Verify encounter creation and subsequent queue token tracking."""
    # 1. Bootstrap new encounter
    bootstrap_payload = {
        "device_id": "test-kiosk-unit-01",
        "intake_mode": "KIOSK",
        "preferred_language": "hi",
        "patient_name": "Ramesh Kumar",
        "patient_age": 52,
        "patient_gender": "male",
        "department": "Kayachikitsa"
    }
    res = client.post("/api/encounters/bootstrap", json=bootstrap_payload)
    assert res.status_code == 200
    b_data = res.json()
    assert "encounter_id" in b_data
    assert "token_number" in b_data
    encounter_id = b_data["encounter_id"]
    token_number = b_data["token_number"]

    # 2. Check queue status with the generated token
    q_res = client.get(f"/api/queue/status/{token_number}")
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["token"] == token_number
    assert "patients_ahead" in q_data
    assert "status" in q_data


def test_call_session_start(client):
    """Verify voice call session start, opening prompt, and synthesized audio generation."""
    # 1. First bootstrap an encounter
    bootstrap_res = client.post("/api/encounters/bootstrap", json={
        "device_id": "mobile-app-client-01",
        "intake_mode": "MOBILE_APP",
        "preferred_language": "hi"
    })
    encounter_id = bootstrap_res.json()["encounter_id"]

    # 2. Start call session
    session_res = client.post("/api/call/session/start", json={
        "encounter_id": encounter_id,
        "language": "hi"
    })
    assert session_res.status_code == 200
    session_data = session_res.json()
    assert session_data["status"] == "CALL_ACTIVE"
    assert len(session_data["opening_text"]) > 0
    # Audio base64 must be populated (pyttsx3 or Sarvam or silence fallback)
    assert len(session_data["opening_audio_base64"]) > 0


def test_call_session_text_turn_and_end(client):
    """Verify touchscreen keyboard text turn and ending session."""
    # 1. Bootstrap encounter
    bootstrap_res = client.post("/api/encounters/bootstrap", json={
        "device_id": "kiosk-unit-02",
        "device_channel": "kiosk",
        "language": "hi"
    })
    assert bootstrap_res.status_code == 200
    encounter_id = bootstrap_res.json()["encounter_id"]

    # 2. Start call session
    session_res = client.post("/api/call/session/start", json={
        "encounter_id": encounter_id,
        "language": "hi"
    })
    assert session_res.status_code == 200
    session_id = session_res.json()["session_id"]

    # 3. Submit text turn (keyboard typing)
    turn_res = client.post("/api/call/text-turn", data={
        "session_id": session_id,
        "text": "मुझे 3 दिन से तेज सिरदर्द और बुखार है"
    })
    assert turn_res.status_code == 200
    turn_data = turn_res.json()
    assert turn_data["turn_index"] == 1
    assert "patient_transcript" in turn_data
    assert "extracted_facts" in turn_data

    # 4. End session
    end_res = client.post("/api/call/session/end", json={
        "session_id": session_id
    })
    assert end_res.status_code == 200
    end_data = end_res.json()
    assert end_data["status"] == "COMPLETED"
    assert "assigned_token" in end_data


def test_doctor_auth_and_queue(client):
    """Verify Doctor PIN authentication gate and doctor OPD queue view."""
    # Invalid PIN returns 401
    bad_auth = client.post("/api/doctor/auth", json={"pin": "wrong_pin"})
    assert bad_auth.status_code == 401

    # Valid PIN (1234 default) returns 200 with authenticated flag
    good_auth = client.post("/api/doctor/auth", json={"pin": "1234"})
    assert good_auth.status_code == 200
    auth_data = good_auth.json()
    assert auth_data["authenticated"] is True

    # Query doctor queue
    queue_res = client.get("/api/doctor/queue")
    assert queue_res.status_code == 200
    queue_data = queue_res.json()
    assert "queue" in queue_data
    assert "total_waiting" in queue_data
    assert isinstance(queue_data["queue"], list)


def test_document_upload_pipeline(client):
    """Verify document upload, image storage, and extraction pipeline."""
    # 1. Bootstrap encounter
    bootstrap_res = client.post("/api/encounters/bootstrap", json={
        "device_id": "scanner-kiosk-01",
        "intake_mode": "KIOSK"
    })
    encounter_id = bootstrap_res.json()["encounter_id"]

    # 2. Generate a minimal in-memory test prescription image
    img = Image.new("RGB", (400, 200), color=(255, 255, 255))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)

    # 3. Upload prescription
    upload_res = client.post(
        "/api/documents/upload",
        data={
            "encounter_id": encounter_id
        },
        files={
            "document": ("test_prescription.jpg", img_byte_arr.getvalue(), "image/jpeg")
        }
    )
    assert upload_res.status_code == 200
    up_data = upload_res.json()
    assert "document_id" in up_data
    assert "extracted_medications" in up_data
    assert "ocr_status" in up_data
