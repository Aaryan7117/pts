#!/usr/bin/env python3
"""
Phase 3 & Phase 4 Verification Test Harness:
- Phase 3: Prescription Document OCR, Bounding Box Evidence, and Drug Safety Checks (B2, T-030, T-031)
- Phase 4: AYUSH Dashavidha Pariksha Assessment and Real-Time Queue Tracking (T-040, T-041)
"""

import sys
import io
import httpx

BASE_URL = "http://localhost:8000"

def log(step: str, status: str, detail: str = ""):
    icon = "PASS" if status == "OK" else "FAIL"
    print(f"[{icon}] {step}: {detail}")

def run_tests():
    client = httpx.Client(base_url=BASE_URL, timeout=15.0)

    print("\n--- PHASE 3 & 4: DOCUMENT OCR & AYUSH QUEUE VERIFICATION ---\n")

    # Step 1: Bootstrap an encounter for document and AYUSH tests
    try:
        r = client.post("/api/encounters/bootstrap", json={
            "channel": "mobile_byod",
            "device_channel": "mobile_byod",
            "patient_id": "P-AYUSH-DOC",
            "language": "hi"
        }, headers={"Idempotency-Key": "doc-ayush-boot-001"})
        assert r.status_code == 200, f"Status {r.status_code}"
        data = r.json()
        encounter_id = data["encounter_id"]
        bearer_token = data.get("bearer_token")
        token_number = data.get("token_number")
        log("1. Encounter Bootstrap", "OK", f"Encounter: {encounter_id} | Token: {token_number}")
    except Exception as e:
        log("1. Encounter Bootstrap", "FAIL", str(e))
        return False

    auth_headers = {"Authorization": f"Bearer {bearer_token}"}

    # Step 2: Document OCR Upload (B2, T-030, T-031)
    try:
        # Create a simple test document
        dummy_file = io.BytesIO(b"Tab Metformin 500mg BD\nTab Glimepiride 2mg OD\nTab Atenolol 50mg OD")
        files = {
            "document": ("prescription_test.jpg", dummy_file, "image/jpeg")
        }
        data = {
            "encounter_id": encounter_id,
            "document_type": "prescription"
        }
        r = client.post("/api/documents/upload", data=data, files=files)
        assert r.status_code == 200, f"Status {r.status_code}"
        doc_res = r.json()
        doc_id = doc_res.get("document_id")
        meds = doc_res.get("extracted_medications", [])
        interactions = doc_res.get("flagged_interactions", [])
        evidence_url = doc_res.get("highlighted_image_url")
        log("2. Document Upload & OCR (B2)", "OK", f"Doc ID: {doc_id} | Meds: {len(meds)} | Flagged Interactions: {len(interactions)} | Evidence: {evidence_url}")
    except Exception as e:
        log("2. Document Upload & OCR (B2)", "FAIL", str(e))
        return False

    # Step 3: AYUSH Dashavidha Pariksha Assessment (T-040)
    try:
        ayush_payload = {
            "prakriti_baseline": {
                "dominant_dosha": "dvandvaja_pk",
                "body_frame": "medium_muscular",
                "skin_texture": "warm_reddish_sweaty",
                "digestion_speed": "rapid_sharp",
                "weather_sensitivity": "intolerant_to_heat",
                "sleep_pattern": "moderate_sound",
                "namaste_code": "NAMASTE:DOSHA-PK-001"
            },
            "agni": {
                "agni_type": "tikshna",
                "appetite_pattern": "excessive_burning",
                "post_meal_heaviness": False,
                "bowel_regularity": "regular",
                "namaste_code": "NAMASTE:AGNI-TIKSHNA-001"
            },
            "koshtha": {
                "koshtha_type": "mridu",
                "bowel_frequency": "twice_or_more_daily",
                "stool_consistency": "soft_loose",
                "namaste_code": "NAMASTE:KOSHTHA-MRIDU-001"
            },
            "ahara_vihara": {
                "diet_primary_taste": ["tikta", "kashaya"],
                "packaged_junk_frequency": "rarely",
                "sleep_wake_timing": "brahma_muhurta",
                "physical_exercise": "vyayama_daily"
            },
            "provisional_dosha_imbalance": ["pitta_vriddhi"]
        }
        r = client.post(f"/api/ayush/encounter/{encounter_id}/assessment", json=ayush_payload)
        assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
        saved_ayush = r.json()
        assert saved_ayush["prakriti_baseline"]["dominant_dosha"] == "dvandvaja_pk"
        log("3. AYUSH Dashavidha Pariksha (T-040)", "OK", f"Prakriti: {saved_ayush['prakriti_baseline']['dominant_dosha']} | Agni: {saved_ayush['agni']['agni_type']}")
    except Exception as e:
        log("3. AYUSH Dashavidha Pariksha (T-040)", "FAIL", str(e))
        return False

    # Step 4: AYUSH Calculate Scoring Endpoint (T-040)
    try:
        calc_payload = {
            "vata_score": 3,
            "pitta_score": 8,
            "kapha_score": 4,
            "appetite_regularity": "sharp",
            "bowel_pattern": "soft"
        }
        r = client.post("/api/ayush/calculate", json=calc_payload)
        assert r.status_code == 200, f"Status {r.status_code}"
        calc_res = r.json()
        log("4. AYUSH Calculate Scoring", "OK", f"Dominant Dosha: {calc_res.get('dominant_dosha')} | Agni: {calc_res.get('inferred_agni')}")
    except Exception as e:
        log("4. AYUSH Calculate Scoring", "FAIL", str(e))
        return False

    # Step 5: Real-Time Queue Status (T-041)
    try:
        r = client.get(f"/api/queue/status/{token_number}")
        assert r.status_code == 200, f"Status {r.status_code}"
        q_stat = r.json()
        log("5. Real-Time Queue Tracker (T-041)", "OK", f"Token: {q_stat.get('token')} | Position: {q_stat.get('patients_ahead')} ahead | Wait: ~{q_stat.get('estimated_wait_minutes')} mins")
    except Exception as e:
        log("5. Real-Time Queue Tracker (T-041)", "FAIL", str(e))
        return False

    # Step 6: OPD Queue Overview for Doctor Cockpit
    try:
        r = client.get("/api/queue/all")
        assert r.status_code == 200, f"Status {r.status_code}"
        all_queue = r.json()
        log("6. Global OPD Queue Overview", "OK", f"Total tokens in hospital queue: {len(all_queue)}")
    except Exception as e:
        log("6. Global OPD Queue Overview", "FAIL", str(e))
        return False

    print("\n ALL PHASE 3 & PHASE 4 TESTS PASSED SUCCESSFULLY!\n")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
