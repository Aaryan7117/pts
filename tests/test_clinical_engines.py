"""
Unit tests for MediKiosk Deterministic Clinical Safety Engines.
Tests Drug-Drug Interactions, Lab Range Checker, Clinical Gap Detector, and NegEx Concept Normalizer.
"""

import pytest
from app.core.clinical.drug_safety import DrugInteractionEngine
from app.core.clinical.lab_checker import LabRangeChecker
from app.core.clinical.gap_detector import ClinicalGapDetector
from app.core.clinical.normalizer import SemanticConceptNormalizer


def test_drug_interaction_critical():
    """Test critical contraindication detection (e.g. Aspirin + Warfarin)."""
    medications = ["Aspirin", "Warfarin", "Paracetamol"]
    alerts = DrugInteractionEngine.check_prescriptions(medications)
    
    assert len(alerts) >= 1
    critical_alerts = [a for a in alerts if a["severity"] == "CRITICAL"]
    assert len(critical_alerts) >= 1
    assert "hemorrhage" in critical_alerts[0]["clinical_warning"].lower()


def test_herb_drug_interaction():
    """Test AYUSH Herb-Drug interaction detection (e.g. Ashwagandha + Sedatives)."""
    medications = ["Ashwagandha", "Diazepam"]
    alerts = DrugInteractionEngine.check_prescriptions(medications)
    
    assert len(alerts) >= 1
    assert any("ashwagandha" in a["drug_a"].lower() or "ashwagandha" in a["drug_b"].lower() for a in alerts)


def test_lab_range_normal_and_critical():
    """Test physiological lab reference ranges (normal, elevated, panic levels)."""
    # Fasting glucose normal
    res_normal = LabRangeChecker.evaluate_result("fasting_blood_glucose", 85.0)
    assert res_normal["status"] == "NORMAL"

    # Fasting glucose critical high
    res_critical = LabRangeChecker.evaluate_result("fasting_blood_glucose", 350.0)
    assert res_critical["status"] == "CRITICAL_HIGH"
    assert res_critical["requires_urgent_escalation"] is True

    # HbA1c elevated
    res_hba1c = LabRangeChecker.evaluate_result("hba1c", 8.2)
    assert res_hba1c["status"] == "HIGH"


def test_clinical_gap_detection():
    """Test silence detection for diabetes without neuropathy screening."""
    facts = [
        {"category": "history", "field": "diabetes", "value": "type_2_diabetes"},
        {"category": "symptoms", "field": "fever", "value": "mild_fever"}
    ]
    detector = ClinicalGapDetector()
    gaps = detector.detect_gaps(facts, patient_age=52, patient_gender="male")
    
    assert len(gaps) >= 1
    rule_ids = [g["rule_id"] for g in gaps]
    assert "DM_NEUROPATHY" in rule_ids or "DM_VISION" in rule_ids


def test_negex_concept_normalizer():
    """Test deterministic NegEx algorithm for Hindi and English negations."""
    normalizer = SemanticConceptNormalizer()

    # English negation
    match_neg = normalizer.normalize("patient has no fever or chest pain", lang="en")
    assert match_neg.is_negated is True

    # Hindi negation: "mujhe bukhar nahi hai"
    match_hi_neg = normalizer.normalize("mujhe bukhar nahi hai", lang="hi")
    assert match_hi_neg.is_negated is True

    # Affirmative Hindi: "3 din se bukhar hai"
    match_hi_pos = normalizer.normalize("teen din se bukhar hai", lang="hi")
    assert match_hi_pos.is_negated is False
