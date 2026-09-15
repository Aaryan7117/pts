"""
MediKiosk — Contract Verification Test Harness (Checkpoint 0)
Validates backend contract reconciliation (B1–B7) against live running FastAPI instance.
"""

import sys
import json
import uuid
import requests

BASE_URL = "http://localhost:8000"

def log_step(name: str):
    print(f"\n[STEP] {name}")

def assert_equal(actual, expected, desc: str):
    if actual != expected:
        print(f"FAILED: {desc}. Expected {expected!r}, got {actual!r}")
        sys.exit(1)
    print(f"  PASS: {desc} ({actual})")

def assert_in(field, container, desc: str):
    if field not in container:
        print(f"FAILED: {desc}. Field '{field}' not found.")
        sys.exit(1)
    print(f"  PASS: {desc} (contains '{field}')")

def main():
    print("=" * 60)
    print("MediKiosk Backend Contract Verification (B1–B7)")
    print(f"Target: {BASE_URL}")
    print("=" * 60)

    # 1. Health check
    log_step("1. Checking System Health")
    res = requests.get(f"{BASE_URL}/api/health", timeout=5)
    assert_equal(res.status_code, 200, "Health check status")
    health = res.json()
    assert_equal(health["status"], "healthy", "System status healthy")

    # 2. Bootstrap Encounter (B1, B4)
    log_step("2. Bootstrapping Encounter (B1 Bearer Token + B4 Flexible Channel)")
    idem_key = f"idem-boot-{uuid.uuid4().hex}"
    boot_payload = {
        "qr_token": f"TK-{uuid.uuid4().hex[:4].upper()}",
        "channel": "mobile_byod",
        "language": "hi"
    }
    res = requests.post(
        f"{BASE_URL}/api/encounters/bootstrap",
        json=boot_payload,
        headers={"Idempotency-Key": idem_key},
        timeout=5
    )
    assert_equal(res.status_code, 200, "Bootstrap status code")
    boot = res.json()
    assert_in("encounter_id", boot, "Bootstrap response contains encounter_id")
    assert_in("token_number", boot, "Bootstrap response contains token_number")
    assert_in("bearer_token", boot, "B1 Bearer Token issued")
    assert_in("supported_languages", boot, "B4 Supported languages returned")
    encounter_id = boot["encounter_id"]
    token_number = boot["token_number"]
    bearer_token = boot["bearer_token"]
    print(f"  Encounter ID: {encounter_id}")
    print(f"  Token Number: {token_number}")
    print(f"  Bearer Token: {bearer_token[:15]}...")

    # 2b. Test Idempotency (B5) on bootstrap
    log_step("2b. Testing Idempotency Cache (B5)")
    res_idem = requests.post(
        f"{BASE_URL}/api/encounters/bootstrap",
        json=boot_payload,
        headers={"Idempotency-Key": idem_key},
        timeout=5
    )
    assert_equal(res_idem.status_code, 200, "Idempotent call status code")
    assert_equal(res_idem.json()["encounter_id"], encounter_id, "Idempotent call returns identical encounter_id")
    print("  Idempotency Key cache validated.")

    # 3. Record Consent (B7)
    log_step("3. Recording DPDP Patient Consent (B7)")
    consent_payload = {
        "language": "hi",
        "consent_version": "1.0",
        "channel": "mobile_byod"
    }
    res = requests.post(
        f"{BASE_URL}/api/encounters/{encounter_id}/consent",
        json=consent_payload,
        headers={"Authorization": f"Bearer {bearer_token}"},
        timeout=5
    )
    assert_equal(res.status_code, 200, "Consent record status code")
    consent = res.json()
    assert_equal(consent["status"], "CONSENT_RECORDED", "Consent status")
    assert_in("recorded_at", consent, "Consent timestamp")

    # 4. Start Call Session (B3 Audio Streaming)
    log_step("4. Starting Voice Call Session (B3)")
    call_start_payload = {
        "encounter_id": encounter_id,
        "language": "hi"
    }
    res = requests.post(
        f"{BASE_URL}/api/call/session/start",
        json=call_start_payload,
        timeout=10
    )
    assert_equal(res.status_code, 200, "Call start status code")
    call_start = res.json()
    assert_in("session_id", call_start, "Call start contains session_id")
    assert_in("opening_text", call_start, "Call start contains opening_text")
    assert_in("opening_audio_url", call_start, "B3 Opening audio streaming URL present")
    session_id = call_start["session_id"]
    print(f"  Session ID: {session_id}")
    print(f"  Opening Audio URL: {call_start.get('opening_audio_url')}")

    # 5. Execute Intake Turn (Text/Audio turn with B3 and alias support)
    log_step("5. Executing Intake Turn (B3 next_question_audio_url & Aliases)")
    res = requests.post(
        f"{BASE_URL}/api/call/text-turn",
        data={
            "session_id": session_id,
            "text": "मुझे तीन दिन से सीने में तेज जलन और दर्द हो रहा है",
            "language": "hi"
        },
        timeout=15
    )
    assert_equal(res.status_code, 200, "Intake turn status code")
    turn = res.json()
    assert_in("transcript", turn, "Transcript field present")
    assert_in("extracted_facts", turn, "Extracted facts list present")
    assert_in("next_question_text", turn, "Next question text present")
    assert_in("next_question_audio_url", turn, "B3 Next question audio streaming URL present")
    print(f"  Transcript: {turn['transcript']}")
    print(f"  Facts Extracted: {len(turn['extracted_facts'])}")
    print(f"  Next Question URL: {turn.get('next_question_audio_url')}")

    # 6. Rehydration State (B6)
    log_step("6. Rehydrating Encounter Full State (B6)")
    res = requests.get(
        f"{BASE_URL}/api/encounters/{encounter_id}",
        headers={"Authorization": f"Bearer {bearer_token}"},
        timeout=5
    )
    assert_equal(res.status_code, 200, "Rehydration status code")
    state = res.json()
    assert_equal(state["encounter_id"], encounter_id, "Rehydrated encounter ID match")
    assert_in("clinical_facts", state, "Clinical facts array present")
    assert_in("active_call_session", state, "Active call session present")
    print(f"  Rehydrated fact count: {len(state['clinical_facts'])}")
    print(f"  Current status: {state['status']}")

    # 7. End Call Session
    log_step("7. Ending Voice Call Session & Locking Intake")
    res = requests.post(
        f"{BASE_URL}/api/call/session/end",
        json={"session_id": session_id},
        timeout=5
    )
    assert_equal(res.status_code, 200, "Call end status code")
    call_end = res.json()
    assert_equal(call_end["status"], "COMPLETED", "Encounter status COMPLETED")
    assert_in("assigned_token", call_end, "Assigned token present")

    print("\n" + "=" * 60)
    print("ALL CHECKPOINT 0 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    main()
