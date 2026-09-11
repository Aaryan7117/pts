"""
MediKiosk — Proactive Clinical Gap Detector ("What Wasn't Asked")
Rule-based silence detection engine.

Diagnostic errors in busy OPDs usually stem from the question that was NEVER asked.
After the intake interview, this engine checks captured facts against expected clinical
standards and generates a Clinical Gap List for the doctor.

Ref: MediKiosk_Full_Context_Handoff.md Innovation 3
"""

import logging
from typing import Optional

logger = logging.getLogger("medikiosk.gap_detector")


class ClinicalGapDetector:
    """
    Checks captured facts against condition-specific clinical rules to identify
    questions that should have been asked but weren't.

    Usage:
        detector = ClinicalGapDetector()
        gaps = detector.detect_gaps(facts, patient_age=55, patient_gender="male")
    """

    # Each rule: {trigger_condition, required_facts, gap_description, rationale, priority}
    GAP_RULES: list[dict] = [
        # === Diabetes-related ===
        {
            "rule_id": "DM_NEUROPATHY",
            "trigger": {
                "any_condition": ["diabetes", "diabetic", "metformin", "glimepiride", "insulin"],
                "min_age": 45
            },
            "required_fact_fields": ["peripheral_neuropathy", "foot_numbness", "tingling_extremities"],
            "gap_description": "Peripheral neuropathy screening (foot numbness / tingling)",
            "clinical_rationale": "Diabetic patients 45+ have 50% lifetime risk of diabetic neuropathy. Early detection prevents foot ulcers and amputations.",
            "priority": "HIGH"
        },
        {
            "rule_id": "DM_VISION",
            "trigger": {
                "any_condition": ["diabetes", "diabetic", "metformin"],
                "min_age": 40
            },
            "required_fact_fields": ["vision_changes", "blurred_vision", "eye_examination"],
            "gap_description": "Diabetic retinopathy screening (vision changes / blurred vision)",
            "clinical_rationale": "Diabetic retinopathy is the leading cause of preventable blindness. Annual eye exam is standard of care.",
            "priority": "HIGH"
        },

        # === Joint Pain ===
        {
            "rule_id": "JOINT_MORNING_STIFFNESS",
            "trigger": {
                "any_condition": ["joint_pain", "arthralgia", "knee_pain", "arthritis"],
                "min_duration_weeks": 2
            },
            "required_fact_fields": ["morning_stiffness", "morning_stiffness_duration"],
            "gap_description": "Morning stiffness duration (differentiates RA from OA)",
            "clinical_rationale": "Morning stiffness >30 minutes suggests inflammatory arthritis (RA). <30 minutes suggests osteoarthritis. Critical differential.",
            "priority": "HIGH"
        },
        {
            "rule_id": "JOINT_SWELLING",
            "trigger": {
                "any_condition": ["joint_pain", "arthralgia"]
            },
            "required_fact_fields": ["joint_swelling", "joint_redness", "joint_warmth"],
            "gap_description": "Joint swelling / redness / warmth assessment",
            "clinical_rationale": "Warm, swollen joints may indicate septic arthritis (medical emergency) or acute gout flare.",
            "priority": "MEDIUM"
        },

        # === Chest Pain ===
        {
            "rule_id": "CHEST_CARDIAC_RISK",
            "trigger": {
                "any_condition": ["chest_pain", "chest_discomfort", "retrosternal_pain"],
            },
            "required_fact_fields": ["exertion_relation", "radiation_pattern", "sweating_with_pain"],
            "gap_description": "Cardiac risk stratification (exertion, radiation, diaphoresis)",
            "clinical_rationale": "Chest pain with exertion, left arm radiation, and sweating is classic for acute coronary syndrome. Must be ruled out immediately.",
            "priority": "HIGH"
        },

        # === Hypertension ===
        {
            "rule_id": "HTN_HEADACHE",
            "trigger": {
                "any_condition": ["hypertension", "high_blood_pressure", "amlodipine", "losartan", "telmisartan"],
            },
            "required_fact_fields": ["headache_pattern", "visual_disturbance"],
            "gap_description": "Hypertensive headache and visual disturbance screening",
            "clinical_rationale": "Severe headache with visual changes in hypertensive patients may indicate hypertensive emergency requiring urgent intervention.",
            "priority": "MEDIUM"
        },

        # === Medication Adherence ===
        {
            "rule_id": "MED_ADHERENCE",
            "trigger": {
                "any_medication_stopped": True
            },
            "required_fact_fields": ["reason_for_stopping", "side_effects_experienced"],
            "gap_description": "Reason for medication discontinuation and side effects experienced",
            "clinical_rationale": "Understanding why patients stop medications prevents re-prescribing ineffective treatments and identifies adverse reactions.",
            "priority": "HIGH"
        },

        # === AYUSH-Specific ===
        {
            "rule_id": "AYUSH_AGNI",
            "trigger": {
                "any_condition": ["digestive_complaint", "appetite_loss", "indigestion", "bloating", "acidity"],
            },
            "required_fact_fields": ["ayush_agni", "post_meal_heaviness", "bowel_regularity"],
            "gap_description": "Agni (digestive fire) assessment — Sama/Vishama/Tikshna/Manda classification",
            "clinical_rationale": "In Ayurveda, Agni state directly determines treatment approach (Deepana, Pachana, or both). Missing this assessment invalidates the Ayurvedic treatment plan.",
            "priority": "HIGH"
        },
        {
            "rule_id": "AYUSH_PRAKRITI",
            "trigger": {
                "is_ayush_encounter": True
            },
            "required_fact_fields": ["ayush_prakriti", "dominant_dosha"],
            "gap_description": "Prakriti (constitutional baseline) assessment",
            "clinical_rationale": "Prakriti determines personalized Ayurvedic treatment. Without it, the physician cannot differentiate Vikriti (current imbalance) from baseline constitution.",
            "priority": "MEDIUM"
        },

        # === Elderly-Specific ===
        {
            "rule_id": "ELDERLY_FALLS",
            "trigger": {
                "min_age": 65
            },
            "required_fact_fields": ["fall_history", "balance_issues", "dizziness"],
            "gap_description": "Fall risk assessment (history of falls, balance, dizziness)",
            "clinical_rationale": "Falls are the leading cause of injury-related death in elderly. Screening is standard geriatric care.",
            "priority": "MEDIUM"
        },
        {
            "rule_id": "ELDERLY_POLYPHARMACY",
            "trigger": {
                "min_age": 60,
                "min_medications": 4
            },
            "required_fact_fields": ["polypharmacy_review_done"],
            "gap_description": "Polypharmacy review (4+ concurrent medications in elderly patient)",
            "clinical_rationale": "Elderly patients on 4+ medications have exponentially higher adverse drug event risk. Systematic review is required.",
            "priority": "HIGH"
        },

        # === Allergy ===
        {
            "rule_id": "ALLERGY_HISTORY",
            "trigger": {
                "always": True
            },
            "required_fact_fields": ["drug_allergy", "allergy_history"],
            "gap_description": "Drug allergy history (critical for safe prescribing)",
            "clinical_rationale": "Drug allergies must be captured before any prescription is generated. Most common preventable adverse event.",
            "priority": "HIGH"
        },
    ]

    def detect_gaps(
        self,
        facts: list[dict],
        patient_age: Optional[int] = None,
        patient_gender: Optional[str] = None,
        medication_count: int = 0,
        is_ayush_encounter: bool = True,
        stopped_medications: Optional[list[str]] = None
    ) -> list[dict]:
        """
        Run all gap rules against the captured facts.

        Args:
            facts: List of ClinicalFact dicts (with 'category', 'field', 'value' fields)
            patient_age: Patient age in years (if known)
            patient_gender: 'male' or 'female' (if known)
            medication_count: Total number of active medications
            is_ayush_encounter: Whether this is an AYUSH-specific encounter
            stopped_medications: List of medications the patient has stopped taking

        Returns:
            List of gap alert dicts, sorted by priority.
        """
        # Build a set of all captured fact fields and conditions for fast lookup
        captured_fields = set()
        captured_conditions = set()
        captured_values = set()

        for fact in facts:
            field = fact.get("field", "").lower()
            value = fact.get("value", "").lower()
            category = fact.get("category", "").lower()
            concept = fact.get("normalized_concept", "").lower() if fact.get("normalized_concept") else ""

            captured_fields.add(field)
            captured_conditions.add(value)
            captured_conditions.add(field)
            captured_conditions.add(concept)

            if category == "medication":
                captured_conditions.add(value)

        gaps = []

        for rule in self.GAP_RULES:
            # Check if this rule's trigger conditions are met
            if not self._check_trigger(
                rule["trigger"],
                captured_conditions=captured_conditions,
                patient_age=patient_age,
                medication_count=medication_count,
                is_ayush_encounter=is_ayush_encounter,
                has_stopped_medications=bool(stopped_medications)
            ):
                continue

            # Check if required facts are missing
            required = rule["required_fact_fields"]
            missing = [f for f in required if f not in captured_fields]

            if missing:
                gaps.append({
                    "rule_id": rule["rule_id"],
                    "gap_type": "MISSING_CLINICAL_QUESTION",
                    "condition_trigger": str(rule["trigger"]),
                    "missing_question": rule["gap_description"],
                    "missing_fields": missing,
                    "clinical_rationale": rule["clinical_rationale"],
                    "priority": rule["priority"]
                })

        # Sort: HIGH priority first
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        gaps.sort(key=lambda g: priority_order.get(g["priority"], 99))

        if gaps:
            logger.info(f"Clinical gaps detected: {len(gaps)} missing assessments.")

        return gaps

    def _check_trigger(
        self,
        trigger: dict,
        captured_conditions: set,
        patient_age: Optional[int],
        medication_count: int,
        is_ayush_encounter: bool,
        has_stopped_medications: bool
    ) -> bool:
        """Check if a rule's trigger conditions are satisfied."""

        # "always" trigger — always fires
        if trigger.get("always"):
            return True

        # Age check
        min_age = trigger.get("min_age")
        if min_age is not None:
            if patient_age is None or patient_age < min_age:
                return False

        # Medication count check
        min_meds = trigger.get("min_medications")
        if min_meds is not None:
            if medication_count < min_meds:
                return False

        # AYUSH encounter check
        if trigger.get("is_ayush_encounter"):
            if not is_ayush_encounter:
                return False

        # Stopped medication check
        if trigger.get("any_medication_stopped"):
            return has_stopped_medications

        # Duration check (simplified — would need actual duration parsing in production)
        # For now, we skip duration filtering in the hackathon demo

        # Condition match check
        any_condition = trigger.get("any_condition", [])
        if any_condition:
            matched = any(
                cond.lower() in captured_conditions
                for cond in any_condition
            )
            if not matched:
                return False

        return True
