"""
Tests for MediKiosk Multi-Document Timeline, Batch Upload, and Lab Range Outlier Detection.
Verifies Phase 3 deliverables.
"""

import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.core.clinical.lab_checker import LabRangeChecker


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _create_test_image_bytes(text: str = "Test Rx") -> bytes:
    """Helper to generate a minimal in-memory test image."""
    img = Image.new("RGB", (300, 150), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_extract_lab_values_from_text():
    """Verify deterministic regex extraction of physiological lab investigations."""
    sample_ocr = (
        "CENTRAL CLINICAL BIOCHEMISTRY REPORT\n"
        "Patient: Ramesh Kumar, Age: 52\n"
        "Fasting Blood Glucose : 185.5 mg/dL\n"
        "HbA1c : 8.4 %\n"
        "Serum Creatinine : 2.1 mg/dL\n"
        "Blood Urea : 55.0 mg/dL\n"
        "Hemoglobin : 14.2 g/dL\n"
        "Total WBC Count : 7800 cells/uL\n"
    )
    labs = LabRangeChecker.extract_lab_values_from_text(sample_ocr)
    test_names = [l["test_name"] for l in labs]
    
    assert "fasting_blood_glucose" in test_names
    assert "hba1c" in test_names
    assert "serum_creatinine" in test_names
    assert "blood_urea" in test_names
    assert "hemoglobin" in test_names
    assert "total_wbc_count" in test_names

    fbs = next(l for l in labs if l["test_name"] == "fasting_blood_glucose")
    assert fbs["value"] == 185.5

    cr = next(l for l in labs if l["test_name"] == "serum_creatinine")
    assert cr["value"] == 2.1


def test_lab_outlier_panic_evaluation():
    """Verify critical panic detection and clinical interpretation generation."""
    # Panic High Glucose (> 300 mg/dL)
    panic_fbs = LabRangeChecker.evaluate_result("fasting_blood_glucose", 342.0)
    assert panic_fbs["status"] == "CRITICAL_HIGH"
    assert panic_fbs["requires_urgent_escalation"] is True
    assert "Immediate physician escalation" in panic_fbs["interpretation"]

    # Critical Low Glucose (<= 50 mg/dL)
    panic_low = LabRangeChecker.evaluate_result("fasting_blood_glucose", 45.0)
    assert panic_low["status"] == "CRITICAL_LOW"
    assert panic_low["requires_urgent_escalation"] is True

    # Normal Range
    norm = LabRangeChecker.evaluate_result("fasting_blood_glucose", 88.0)
    assert norm["status"] == "NORMAL"
    assert norm["requires_urgent_escalation"] is False


def test_batch_document_upload_and_timeline(client):
    """Verify POST /api/documents/batch-upload and GET /api/documents/encounter/{id}/timeline."""
    # 1. Bootstrap encounter
    b_res = client.post("/api/encounters/bootstrap", json={
        "patient_name": "Suresh Patel",
        "preferred_language": "hi",
        "department": "General Medicine"
    })
    encounter_id = b_res.json()["encounter_id"]

    # 2. Prepare multiple files for batch upload
    img1 = _create_test_image_bytes("Prescription 1")
    img2 = _create_test_image_bytes("Lab Report 1")

    files = [
        ("files", ("rx_patel_1.jpg", img1, "image/jpeg")),
        ("files", ("lab_patel_2.jpg", img2, "image/jpeg"))
    ]

    batch_res = client.post(
        "/api/documents/batch-upload",
        data={
            "encounter_id": encounter_id,
            "document_type": "prescription",
            "document_date": "2026-09-12"
        },
        files=files
    )
    assert batch_res.status_code == 200
    b_data = batch_res.json()
    assert b_data["success"] is True
    assert b_data["total_uploaded"] == 2
    assert len(b_data["documents"]) == 2

    # 3. Retrieve Multi-Document Timeline
    timeline_res = client.get(f"/api/documents/encounter/{encounter_id}/timeline")
    assert timeline_res.status_code == 200
    t_data = timeline_res.json()
    assert t_data["total_documents"] >= 2
    assert "timeline" in t_data
    assert len(t_data["timeline"]) >= 2
    assert t_data["timeline"][0]["document_type"] == "prescription"
