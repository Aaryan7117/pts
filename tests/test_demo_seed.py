"""
Integration tests verifying the seeded MediKiosk demonstration dataset and doctor endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from app.main import app
from scripts.seed_demo_data import seed_database


@pytest.fixture(scope="module", autouse=True)
def setup_seed_data():
    """Ensure database is seeded before running seed tests."""
    seed_database(reset=True)


@pytest.fixture(scope="module")
def client():
    """TestClient fixture."""
    with TestClient(app) as c:
        yield c


def test_doctor_queue_seeded_order(client):
    """Verify doctor queue contains 15 patients correctly prioritized by severity."""
    res = client.get("/api/doctor/queue")
    assert res.status_code == 200
    data = res.json()

    assert "queue" in data
    assert data["total_waiting"] == 15
    queue = data["queue"]

    # First 5 entries must be RED
    for entry in queue[:5]:
        assert entry["severity_badge"] == "RED", f"Expected RED but got {entry['severity_badge']} for {entry['token_number']}"
        assert entry["has_red_flags"] is True

    # Next 3 entries must be YELLOW
    for entry in queue[5:8]:
        assert entry["severity_badge"] == "YELLOW", f"Expected YELLOW but got {entry['severity_badge']} for {entry['token_number']}"

    # Remaining entries must be GREEN
    for entry in queue[8:]:
        assert entry["severity_badge"] == "GREEN", f"Expected GREEN but got {entry['severity_badge']} for {entry['token_number']}"


def test_primary_demo_case_lakshmi_devi(client):
    """Verify primary demo case (Lakshmi Devi, enc-demo-lakshmi-001) details."""
    res = client.get("/api/doctor/patient/enc-demo-lakshmi-001")
    assert res.status_code == 200
    detail = res.json()

    # 1. Encounter info
    enc = detail["encounter"]
    assert enc["encounter_id"] == "enc-demo-lakshmi-001"
    assert enc["token_number"] == "A-101"
    assert enc["severity_badge"] == "RED"
    assert enc["language"] == "ta"

    # 2. Clinical facts mapped
    facts = detail["clinical_facts"]
    assert len(facts) >= 10

    categories = {f["category"] for f in facts}
    assert "chief_complaint" in categories
    assert "medication" in categories
    assert "lab_result" in categories
    assert "vital" in categories
    assert "ayush_agni" in categories
    assert "ayush_prakriti" in categories

    # Verify Metformin & Amlodipine facts
    med_values = [f["value"] for f in facts if f["category"] == "medication"]
    assert "Metformin" in med_values
    assert "Amlodipine" in med_values

    # 3. Lab alerts (HbA1c 7.8% is HIGH)
    lab_alerts = detail["lab_result_alerts"]
    assert len(lab_alerts) >= 1
    hba1c_alert = next((a for a in lab_alerts if a["test_name"] == "hba1c"), None)
    assert hba1c_alert is not None
    assert hba1c_alert["status"] == "HIGH"
    assert hba1c_alert["measured_value"] == 7.8

    # 4. Proactive clinical gap alerts
    gaps = detail["clinical_gap_alerts"]
    assert len(gaps) > 0
    gap_types = [g["gap_type"] for g in gaps]
    assert "MISSING_CLINICAL_QUESTION" in gap_types

    # 5. Documents & Evidence
    docs = detail["documents"]
    assert len(docs) == 2
    for doc in docs:
        assert doc["ocr_status"] == "SUCCESS"
        assert len(doc["ocr_raw_text"]) > 0
        assert Path(doc["file_path"]).exists()
        assert Path(doc["highlighted_path"]).exists()

    # 6. AYUSH intake
    ayush = detail["ayush_intake"]
    assert ayush is not None
    assert "manda_agni" in ayush or "prakriti_assessment" in ayush


def test_critical_drug_interaction_alert(client):
    """Verify Case 2 (Rajesh Sharma) triggers CRITICAL Warfarin + Aspirin alert."""
    res = client.get("/api/doctor/patient/enc-demo-rajesh-002")
    assert res.status_code == 200
    detail = res.json()

    alerts = detail["drug_interaction_alerts"]
    assert len(alerts) >= 1
    crit_alert = next((a for a in alerts if a["severity"] == "CRITICAL"), None)
    assert crit_alert is not None
    pair = {crit_alert["drug_a"].lower(), crit_alert["drug_b"].lower()}
    assert "warfarin" in pair
    assert "aspirin" in pair


def test_ayush_herb_drug_interaction_alert(client):
    """Verify Case 6 (Meenakshi Sundaram) triggers MODERATE Licorice + Amlodipine alert."""
    res = client.get("/api/doctor/patient/enc-demo-meenakshi-006")
    assert res.status_code == 200
    detail = res.json()

    alerts = detail["drug_interaction_alerts"]
    assert len(alerts) >= 1
    mod_alert = next((a for a in alerts if a["severity"] == "MODERATE"), None)
    assert mod_alert is not None
    pair = {mod_alert["drug_a"].lower(), mod_alert["drug_b"].lower()}
    assert "amlodipine" in pair
    assert any("licorice" in d or "yashtimadhu" in d for d in pair)


def test_critical_lab_panic_alert(client):
    """Verify Case 4 (Sunita Patel) triggers CRITICAL_HIGH FBS 342 mg/dL panic alert."""
    res = client.get("/api/doctor/patient/enc-demo-sunita-004")
    assert res.status_code == 200
    detail = res.json()

    lab_alerts = detail["lab_result_alerts"]
    assert len(lab_alerts) >= 1
    panic_alert = next((a for a in lab_alerts if a["test_name"] == "fasting_blood_glucose"), None)
    assert panic_alert is not None
    assert panic_alert["status"] == "CRITICAL_HIGH"
    assert panic_alert["requires_urgent_escalation"] is True


def test_static_document_serving(client):
    """Verify static prescription and evidence images are servable via HTTP."""
    res = client.get("/static/evidence/doc-demo-lakshmi-rx-boxed.jpg")
    assert res.status_code == 200
    assert res.headers["content-type"] in ("image/jpeg", "image/jpg")
    assert len(res.content) > 1000
