import asyncio
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.routing.location_resolver import LocationResolver, CLINIC_REGISTRY


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ============================================================
#  WATERFALL RESOLVER UNIT TESTS
# ============================================================

def test_waterfall_step1_registered_patient():
    """Step 1: Registered ABDM citizen phone number resolves to designated clinic."""
    async def _run():
        from app.database import init_db
        db = await init_db()
        return await LocationResolver.resolve(
            caller_phone="9876543210",
            db=db
        )
    res = asyncio.run(_run())
    assert res.waterfall_step == 1
    assert res.resolution_type == "ABDM_REGISTERED_PATIENT"
    assert res.confidence == 1.0
    assert res.clinic.clinic_id == "AIIA_DELHI"
    assert res.patient_name is not None
    assert "ABDM" in res.rationale


def test_waterfall_step2_dialed_did():
    """Step 2: Unregistered caller dialing Chennai or Jaipur regional helpline DID."""
    # Dialing Chennai DID (044-22237254)
    res_chennai = asyncio.run(LocationResolver.resolve(
        caller_phone="8888899999",  # Unregistered dummy number
        dialed_number="04422237254"
    ))
    assert res_chennai.waterfall_step == 2
    assert res_chennai.resolution_type == "REGIONAL_HELPLINE_DID"
    assert res_chennai.clinic.clinic_id == "NIS_CHENNAI"
    assert "Chennai" in res_chennai.clinic.district

    # Dialing Jaipur DID (0141-2635816)
    res_jaipur = asyncio.run(LocationResolver.resolve(
        caller_phone="8888899999",
        dialed_number="01412635816"
    ))
    assert res_jaipur.waterfall_step == 2
    assert res_jaipur.clinic.clinic_id == "NIA_JAIPUR"
    assert res_jaipur.clinic.state == "Rajasthan"


def test_waterfall_step3_dot_telecom_circle():
    """Step 3: Unregistered caller with no DID resolves via DoT 4-digit mobile series."""
    # Delhi NCR series (9810xxxxxx)
    res_delhi = asyncio.run(LocationResolver.resolve(caller_phone="+91-98101-23456"))
    assert res_delhi.waterfall_step == 3
    assert res_delhi.resolution_type == "DOT_TELECOM_CIRCLE_SERIES"
    assert res_delhi.clinic.clinic_id == "AIIA_DELHI"
    assert res_delhi.clinic.telecom_circle == "Delhi NCR"

    # Tamil Nadu series (9443xxxxxx)
    res_tn = asyncio.run(LocationResolver.resolve(caller_phone="9443198765"))
    assert res_tn.waterfall_step == 3
    assert res_tn.clinic.clinic_id == "NIS_CHENNAI"
    assert res_tn.clinic.state == "Tamil Nadu"

    # Karnataka series (9845xxxxxx)
    res_ka = asyncio.run(LocationResolver.resolve(caller_phone="9845012345"))
    assert res_ka.waterfall_step == 3
    assert res_ka.clinic.clinic_id == "NIUM_BENGALURU"
    assert res_ka.clinic.state == "Karnataka"

    # Maharashtra series (9820xxxxxx)
    res_mh = asyncio.run(LocationResolver.resolve(caller_phone="9820054321"))
    assert res_mh.waterfall_step == 3
    assert res_mh.clinic.clinic_id == "RAV_MUMBAI"
    assert res_mh.clinic.state == "Maharashtra"


def test_waterfall_step4_apex_fallback():
    """Step 4: Unknown / non-geographic mobile series falls back to AIIA Apex Hub."""
    res_fallback = asyncio.run(LocationResolver.resolve(caller_phone="1000000000"))
    assert res_fallback.waterfall_step == 4
    assert res_fallback.resolution_type == "NATIONAL_APEX_FALLBACK"
    assert res_fallback.clinic.clinic_id == "AIIA_DELHI"
    assert res_fallback.clinic.is_apex_hub is True
    assert res_fallback.confidence == 0.70


# ============================================================
#  FASTAPI ENDPOINT INTEGRATION TESTS
# ============================================================

def test_diagnostic_resolve_location_api(client):
    """Verify public testing endpoint /api/ivr/resolve-location."""
    # Test Tamil Nadu series
    r = client.get("/api/ivr/resolve-location?caller_phone=9443123456")
    assert r.status_code == 200
    data = r.json()
    assert data["waterfall_step"] == 3
    assert data["clinic"]["clinic_id"] == "NIS_CHENNAI"

    # Test Dialed DID override
    r2 = client.get("/api/ivr/resolve-location?caller_phone=9443123456&dialed_number=01412635816")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["waterfall_step"] == 2
    assert data2["clinic"]["clinic_id"] == "NIA_JAIPUR"


def test_exotel_incoming_call_and_turn_lifecycle(client):
    """
    End-to-End IVR Lifecycle:
    1. Incoming call webhook from Exotel -> assigns clinic & token.
    2. Patient speech turn -> extracts facts.
    3. Call end -> locks encounter, sets severity, and sends simulated SMS.
    """
    # 1. Incoming Call Webhook
    incoming_payload = {
        "From": "9810123456",
        "To": "01126950401",
        "language": "hi"
    }
    r1 = client.post("/api/ivr/exotel/incoming-call", json=incoming_payload)
    assert r1.status_code == 200
    call_data = r1.json()

    assert call_data["status"] == "CONNECTED"
    assert "IVR-" in call_data["token_number"]
    assert call_data["assigned_clinic"]["clinic_id"] == "AIIA_DELHI"
    assert "नमस्ते" in call_data["exotel_say"]

    session_id = call_data["session_id"]
    encounter_id = call_data["encounter_id"]

    # 2. Patient Speech Turn (Chief Complaint)
    turn_payload = {
        "session_id": session_id,
        "caller_phone": "9810123456",
        "speech_text": "मुझे तीन दिन से तेज बुखार, बदन दर्द और सूखी खांसी है",
        "turn_index": 0
    }
    r2 = client.post("/api/ivr/exotel/speech-turn", json=turn_payload)
    assert r2.status_code == 200
    turn_data = r2.json()
    assert turn_data["patient_transcript"] == turn_payload["speech_text"]
    assert turn_data["extracted_facts_count"] >= 1

    # 3. Conclude Call
    end_payload = {
        "session_id": session_id,
        "encounter_id": encounter_id
    }
    r3 = client.post("/api/ivr/exotel/end-call", json=end_payload)
    assert r3.status_code == 200
    end_data = r3.json()

    assert end_data["token_number"] == call_data["token_number"]
    assert end_data["sms_dispatched"] is True
    assert "मेडीकिओस्क टोकन संख्या" in end_data["sms_text"]
    assert end_data["severity_badge"] in ("GREEN", "YELLOW", "RED")
