#!/usr/bin/env python3
"""
Phase 2 Vertical Slice End-to-End Verification Test
Tests:
  1. Bootstrap Mobile BYOD encounter (B1, B4)
  2. Record digital consent (B7)
  3. Start 1-Tap AI Call session (B3)
  4. Multi-turn conversational voice loop (SOCRATES)
  5. End call session and verify queue token generation
  6. Rehydrate full clinical state (B6)
  7. Verify Doctor Queue displays the patient (Ticket T-022)
  8. Verify Doctor Patient Detail View (evidence drilldown & clinical facts)
"""

import sys
import json
import httpx

BASE_URL = "http://localhost:8000"

def log(step: str, status: str, detail: str = ""):
    icon = "PASS" if status == "OK" else "FAIL"
    print(f"[{icon}] {step}: {detail}")

def run_tests():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    print("\n--- PHASE 2: VOICE INTAKE VERTICAL SLICE VERIFICATION ---\n")

    # Step 1: Health Check
    try:
        r = client.get("/api/health")
        assert r.status_code == 200, f"Status {r.status_code}"
        log("1. Health Check", "OK", f"Providers: {r.json().get('providers')}")
    except Exception as e:
        log("1. Health Check", "FAIL", str(e))
        return False

    # Step 2: Bootstrap Mobile BYOD Encounter
    try:
        r = client.post("/api/encounters/bootstrap", json={
            "channel": "mobile_byod",
            "device_channel": "mobile_byod",
            "patient_id": "P-VERT-TEST",
            "language": "hi"
        }, headers={"Idempotency-Key": "vert-boot-001"})
        assert r.status_code == 200, f"Status {r.status_code}"
        data = r.json()
        encounter_id = data["encounter_id"]
        bearer_token = data.get("bearer_token")
        token_number = data.get("token_number")
        assert encounter_id, "Missing encounter_id"
        assert bearer_token, "Missing bearer_token"
        log("2. Mobile Bootstrap", "OK", f"Encounter: {encounter_id} | Token: {token_number}")
    except Exception as e:
        log("2. Mobile Bootstrap", "FAIL", str(e))
        return False

    auth_headers = {"Authorization": f"Bearer {bearer_token}"}

    # Step 3: Record Digital Consent (B7)
    try:
        r = client.post(f"/api/encounters/{encounter_id}/consent", json={
            "consent_type": "voice_intake_telehealth",
            "granted": True,
            "language": "hi"
        }, headers={"Idempotency-Key": "vert-consent-001", **auth_headers})
        assert r.status_code == 200, f"Status {r.status_code}"
        log("3. Digital Consent (B7)", "OK", f"Consent logged for {encounter_id}")
    except Exception as e:
        log("3. Digital Consent (B7)", "FAIL", str(e))
        return False

    # Step 4: Start 1-Tap AI Call Session (B3)
    try:
        r = client.post("/api/call/session/start", json={
            "encounter_id": encounter_id,
            "language": "hi"
        }, headers=auth_headers)
        assert r.status_code == 200, f"Status {r.status_code}"
        data = r.json()
        session_id = data["session_id"]
        opening_audio = data.get("opening_audio_url")
        log("4. Start AI Call", "OK", f"Session: {session_id} | Audio URL: {opening_audio}")
    except Exception as e:
        log("4. Start AI Call", "FAIL", str(e))
        return False

    # Step 5: Multi-Turn SOCRATES Intake (Turn 1)
    try:
        r = client.post("/api/call/text-turn", data={
            "session_id": session_id,
            "text": "मुझे पिछले २ दिनों से तेज़ सिरदर्द और हल्का बुखार है"
        })
        assert r.status_code == 200, f"Status {r.status_code}"
        data = r.json()
        facts = data.get("extracted_facts", [])
        next_q = data.get("next_question_text")
        next_audio = data.get("next_question_audio_url")
        log("5. Turn 1 (Chief Complaint)", "OK", f"Facts captured: {len(facts)} | Next Q: {next_q[:40]}... | Audio: {next_audio}")
    except Exception as e:
        log("5. Turn 1 (Chief Complaint)", "FAIL", str(e))
        return False

    # Step 6: Multi-Turn SOCRATES Intake (Turn 2: Severity & Character)
    try:
        r = client.post("/api/call/text-turn", data={
            "session_id": session_id,
            "text": "दर्द 10 में से 7 है और माथे के दोनों तरफ है"
        })
        assert r.status_code == 200, f"Status {r.status_code}"
        data = r.json()
        log("6. Turn 2 (Severity/Location)", "OK", f"Facts captured: {len(data.get('extracted_facts', []))}")
    except Exception as e:
        log("6. Turn 2 (Severity/Location)", "FAIL", str(e))
        return False

    # Step 7: End Call Session
    try:
        r = client.post("/api/call/session/end", json={
            "session_id": session_id
        })
        assert r.status_code == 200, f"Status {r.status_code}"
        data = r.json()
        assigned_token = data.get("assigned_token")
        badge = data.get("severity_badge")
        total_facts = data.get("total_facts_captured")
        log("7. End Call Session", "OK", f"Status: {data.get('status')} | Token: {assigned_token} | Severity: {badge} | Total Facts: {total_facts}")
    except Exception as e:
        log("7. End Call Session", "FAIL", str(e))
        return False

    # Step 8: Rehydrate Full Encounter State (B6)
    try:
        r = client.get(f"/api/encounters/{encounter_id}", headers=auth_headers)
        assert r.status_code == 200, f"Status {r.status_code}"
        data = r.json()
        facts_list = data.get("clinical_facts", [])
        log("8. Rehydration (B6)", "OK", f"Encounter Status: {data.get('status')} | Facts count: {len(facts_list)}")
    except Exception as e:
        log("8. Rehydration (B6)", "FAIL", str(e))
        return False

    # Step 9: Verify Doctor Queue Displays the Patient (Ticket T-022)
    try:
        r = client.get("/api/doctor/queue")
        assert r.status_code == 200, f"Status {r.status_code}"
        q_data = r.json()
        patients = q_data.get("patients", []) or q_data.get("queue", [])
        match = next((p for p in patients if p["encounter_id"] == encounter_id), None)
        assert match is not None, f"Encounter {encounter_id} not found in doctor queue ({len(patients)} patients in queue)"
        token_shown = match.get("token_number") or match.get("token")
        log("9. Doctor Queue Visibility", "OK", f"Found {encounter_id} in Doctor Queue (Token: {token_shown}, Badge: {match.get('severity_badge')})")
    except Exception as e:
        log("9. Doctor Queue Visibility", "FAIL", str(e))
        return False

    # Step 10: Verify Doctor Patient Detail View (Evidence & Clinical Facts)
    try:
        r = client.get(f"/api/doctor/patient/{encounter_id}")
        assert r.status_code == 200, f"Status {r.status_code}"
        detail = r.json()
        assert detail["encounter"]["id"] == encounter_id
        facts_in_cockpit = detail.get("clinical_facts", [])
        log("10. Doctor Cockpit Detail View", "OK", f"Cockpit loaded successfully with {len(facts_in_cockpit)} facts and {len(detail.get('drug_alerts', []))} alerts")
    except Exception as e:
        log("10. Doctor Cockpit Detail View", "FAIL", str(e))
        return False

    print("\n ALL 10 VERTICAL SLICE TESTS PASSED (CHECKPOINT 2 COMPLETE)!\n")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
