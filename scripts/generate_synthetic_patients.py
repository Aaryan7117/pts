"""
MediKiosk — Synthetic Patient Dataset Generator
Provides 15 deterministic, reproducible, clinically realistic patient profiles:
  - 5 RED flag emergency cases (Chest pain / Lakshmi Devi, Anticoagulant conflict, Acute Dyspnea, Panic Hyperglycemia, Angina)
  - 3 YELLOW flag cases (AYUSH Herb-Drug interactions: Licorice+Amlodipine, Ashwagandha+Diazepam, Triphala+Metformin)
  - 7 GREEN normal cases (Dyspepsia, Osteoarthritis, Allergic rhinitis, Thyroid, Dermatitis, Lumbar strain, Health checkup)

Covers all channels (Kiosk, Android BYOD, IVR phone) and languages (ta, hi, te, mr, en).
"""

from typing import Any


def get_synthetic_patients() -> list[dict[str, Any]]:
    """Return 15 fully specified, reproducible synthetic patient cases."""
    return [
        # =====================================================================
        # CASE 1: LAKSHMI DEVI (PRIMARY SHOWCASE DEMO CASE)
        # =====================================================================
        {
            "case_key": "lakshmi_devi",
            "patient": {
                "id": "pat-demo-lakshmi-001",
                "name": "Lakshmi Devi",
                "age": 58,
                "gender": "female",
                "phone": "+91 98410 23456",
                "language": "ta",
                "abha_id": "91-4820-9182-3849",
                "hospital_mrn": "MRN-2026-00101",
            },
            "encounter": {
                "id": "enc-demo-lakshmi-001",
                "token_number": "A-101",
                "language": "ta",
                "channel": "kiosk",
                "status": "COMPLETED",
                "department": "General Medicine",
                "severity_badge": "RED",
            },
            "queue": {
                "token": "A-101",
                "department": "General Medicine",
                "status": "WAITING",
                "position": 1,
                "doctor_room": "OPD Room 101",
            },
            "call_session": {
                "id": "call-demo-lakshmi-001",
                "status": "COMPLETED",
                "language": "ta",
                "current_step": "completed",
                "turn_count": 6,
            },
            "clinical_facts": [
                {
                    "id": "fact-lakshmi-cc-01",
                    "category": "chief_complaint",
                    "field": "chest_pain",
                    "value": "Chest pain for 3 days with tightness",
                    "patient_words": "எனக்கு மூன்று நாட்களாக மார்பு வலி உள்ளது.",
                    "normalized_concept": "Chest pain",
                    "concept_code": "SNOMED:29857009",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.96,
                    "confidence_breakdown": {"tier_score": 0.98, "input_quality": 0.98, "completeness": 1.0},
                    "temporal_state": None,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-lakshmi-sym-01",
                    "category": "symptom",
                    "field": "duration",
                    "value": "3 days",
                    "patient_words": "மூன்று நாட்களாக",
                    "normalized_concept": "Symptom duration",
                    "concept_code": "SNOMED:282840006",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.95,
                    "temporal_state": None,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-lakshmi-sym-02",
                    "category": "symptom",
                    "field": "dyspnea",
                    "value": "Breathlessness on exertion",
                    "patient_words": "வேலை செய்யும்போது மூச்சுத் திணறல் அதிகமாகிறது.",
                    "normalized_concept": "Dyspnea on exertion",
                    "concept_code": "SNOMED:282840006",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.92,
                    "confidence_breakdown": {"tier_score": 0.95, "input_quality": 0.97, "completeness": 1.0},
                    "temporal_state": None,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-lakshmi-pmh-01",
                    "category": "symptom",
                    "field": "past_medical_history",
                    "value": "Type 2 Diabetes Mellitus",
                    "patient_words": "எனக்கு 5 வருடமாக சர்க்கரை நோய் உள்ளது.",
                    "normalized_concept": "Type 2 diabetes mellitus",
                    "concept_code": "SNOMED:44054006",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.96,
                    "temporal_state": None,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-lakshmi-pmh-02",
                    "category": "symptom",
                    "field": "past_medical_history",
                    "value": "Essential Hypertension",
                    "patient_words": "இரத்த அழுத்தம் (BP) உள்ளது.",
                    "normalized_concept": "Essential hypertension",
                    "concept_code": "SNOMED:59621000",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.94,
                    "temporal_state": None,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-lakshmi-med-01",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Metformin",
                    "dose": "500 mg",
                    "frequency": "BD (Twice daily)",
                    "patient_words": "மெட்ஃபோர்மின் காலை இரவு சாப்பிடுகிறேன்",
                    "normalized_concept": "Metformin 500mg tablet",
                    "concept_code": "SNOMED:318466000",
                    "provenance_tier": "OCR",
                    "source_type": "document_ocr",
                    "source_reference": {
                        "type": "document_ocr",
                        "document_id": "doc-demo-lakshmi-rx",
                        "line_indices": [3],
                        "bbox": [80, 240, 480, 280],
                        "ocr_confidence": 0.96,
                        "raw_text": "Tab. Metformin 500mg BD x 30 days"
                    },
                    "confidence": 0.94,
                    "temporal_state": "taking",
                    "valid_from": "2026-06-01",
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-lakshmi-med-02",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Amlodipine",
                    "dose": "5 mg",
                    "frequency": "OD (Once daily)",
                    "patient_words": "ஆம்லோடிபின் ஒரு வேளை",
                    "normalized_concept": "Amlodipine 5mg tablet",
                    "concept_code": "SNOMED:324024003",
                    "provenance_tier": "OCR",
                    "source_type": "document_ocr",
                    "source_reference": {
                        "type": "document_ocr",
                        "document_id": "doc-demo-lakshmi-rx",
                        "line_indices": [4],
                        "bbox": [80, 290, 480, 330],
                        "ocr_confidence": 0.95,
                        "raw_text": "Tab. Amlodipine 5mg OD (Morning)"
                    },
                    "confidence": 0.93,
                    "temporal_state": "taking",
                    "valid_from": "2026-06-01",
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-lakshmi-lab-01",
                    "category": "lab_result",
                    "field": "hba1c",
                    "value": "7.8",
                    "patient_words": None,
                    "normalized_concept": "Glycated hemoglobin (HbA1c)",
                    "concept_code": "SNOMED:43396009",
                    "provenance_tier": "OCR",
                    "source_type": "document_ocr",
                    "source_reference": {
                        "type": "document_ocr",
                        "document_id": "doc-demo-lakshmi-lab",
                        "line_indices": [2],
                        "bbox": [80, 200, 520, 240],
                        "ocr_confidence": 0.97,
                        "raw_text": "HbA1c (Glycosylated Hemoglobin): 7.8 % [Reference: 4.0 - 5.6 %]"
                    },
                    "confidence": 0.97,
                    "temporal_state": None,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-lakshmi-vit-01",
                    "category": "vital",
                    "field": "blood_pressure",
                    "value": "148/92 mmHg",
                    "patient_words": None,
                    "normalized_concept": "Blood pressure reading",
                    "concept_code": "SNOMED:75367002",
                    "provenance_tier": "TOUCH",
                    "source_type": "touch_input",
                    "confidence": 1.0,
                    "temporal_state": None,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-lakshmi-ayush-01",
                    "category": "ayush_agni",
                    "field": "manda_agni",
                    "value": "Manda Agni (Sluggish digestion / heavy feeling after meals)",
                    "patient_words": "சாப்பிட்ட பிறகு வயிறு கனமாக இருக்கும், பசி குறைவு.",
                    "normalized_concept": "Manda Agni",
                    "concept_code": "NAMASTE:AYU-AGNI-002",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.89,
                    "temporal_state": None,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-lakshmi-ayush-02",
                    "category": "ayush_prakriti",
                    "field": "prakriti_assessment",
                    "value": "Vata-Pitta Prakriti",
                    "patient_words": "குளிரும் காற்றும் ஒத்துக்கொள்ளாது, எளிதில் தாகம் எடுக்கும்.",
                    "normalized_concept": "Vata-Pitta Prakriti",
                    "concept_code": "NAMASTE:AYU-PRAK-003",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.88,
                    "temporal_state": None,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-lakshmi-alg-01",
                    "category": "allergy",
                    "field": "drug_allergy",
                    "value": "Penicillin / Sulfa",
                    "patient_words": "மருந்து அலர்ஜி எதுவும் இல்லை",
                    "normalized_concept": "No known drug allergies",
                    "concept_code": "SNOMED:409137002",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.95,
                    "is_negated": True,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-lakshmi-rx",
                    "filename": "lakshmi_devi_prescription.jpg",
                    "title": "AIIA New Delhi - OPD Prescription Note",
                    "type": "prescription",
                    "header": "ALL INDIA INSTITUTE OF AYURVEDA / OPD CLINIC",
                    "patient_name": "Lakshmi Devi",
                    "patient_info": "Age: 58Y / F | MRN: 2026-00101 | Date: 12-Sep-2026",
                    "body_lines": [
                        "Diagnosis: T2DM / Essential HTN / Atypical Angina under evaluation",
                        "Rx:",
                        "1. Tab. Metformin 500mg BD (after meals)",
                        "2. Tab. Amlodipine 5mg OD (morning)",
                        "Adv: Fasting Blood Sugar, HbA1c, Resting ECG 12-Lead",
                    ],
                    "highlights": [
                        {"text": "Tab. Metformin 500mg BD", "box": [80, 240, 480, 280], "color": "#3B82F6"},
                        {"text": "Tab. Amlodipine 5mg OD", "box": [80, 290, 480, 330], "color": "#10B981"}
                    ]
                },
                {
                    "id": "doc-demo-lakshmi-lab",
                    "filename": "lakshmi_devi_hba1c_report.jpg",
                    "title": "Clinical Biochemistry Investigation Report",
                    "type": "lab_report",
                    "header": "CENTRAL CLINICAL LABORATORY — BIOCHEMISTRY DIVISION",
                    "patient_name": "Lakshmi Devi",
                    "patient_info": "Age: 58Y / F | Sample Date: 11-Sep-2026",
                    "body_lines": [
                        "TEST PARAMETER                     RESULT      REFERENCE INTERVAL",
                        "------------------------------------------------------------------",
                        "HbA1c (Glycosylated Hemoglobin)     7.8 %       4.0 - 5.6 % (HIGH)",
                        "Estimated Average Glucose (eAG)    177 mg/dL   70 - 126 mg/dL",
                        "Serum Creatinine                   0.9 mg/dL   0.6 - 1.2 mg/dL",
                    ],
                    "highlights": [
                        {"text": "HbA1c: 7.8 % (HIGH)", "box": [80, 200, 520, 240], "color": "#EF4444"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 2: RAJESH SHARMA (CRITICAL DRUG INTERACTION: ASPIRIN + WARFARIN)
        # =====================================================================
        {
            "case_key": "rajesh_sharma",
            "patient": {
                "id": "pat-demo-rajesh-002",
                "name": "Rajesh Sharma",
                "age": 64,
                "gender": "male",
                "phone": "+91 98111 87654",
                "language": "hi",
                "abha_id": "91-3141-5926-5358",
                "hospital_mrn": "MRN-2026-00102",
            },
            "encounter": {
                "id": "enc-demo-rajesh-002",
                "token_number": "A-102",
                "language": "hi",
                "channel": "kiosk",
                "status": "COMPLETED",
                "department": "Cardiology",
                "severity_badge": "RED",
            },
            "queue": {
                "token": "A-102",
                "department": "Cardiology",
                "status": "WAITING",
                "position": 2,
                "doctor_room": "OPD Room 108",
            },
            "call_session": {
                "id": "call-demo-rajesh-002",
                "status": "COMPLETED",
                "language": "hi",
                "current_step": "completed",
                "turn_count": 5,
            },
            "clinical_facts": [
                {
                    "id": "fact-rajesh-cc-01",
                    "category": "chief_complaint",
                    "field": "palpitations",
                    "value": "Severe palpitations and intermittent dizziness",
                    "patient_words": "मुझे 2 दिन से बहुत घबराहट और चक्कर आ रहे हैं।",
                    "normalized_concept": "Palpitations",
                    "concept_code": "SNOMED:80313002",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.94,
                    "temporal_state": None,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-rajesh-med-01",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Warfarin",
                    "dose": "5 mg",
                    "frequency": "OD",
                    "patient_words": "वारफारिन खून पतला करने के लिए",
                    "normalized_concept": "Warfarin 5mg",
                    "concept_code": "SNOMED:318851002",
                    "provenance_tier": "OCR",
                    "source_type": "document_ocr",
                    "confidence": 0.95,
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-rajesh-med-02",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Aspirin",
                    "dose": "150 mg",
                    "frequency": "OD",
                    "patient_words": "सिरदर्द के लिए एस्पिरिन खुद से शुरू की",
                    "normalized_concept": "Aspirin 150mg",
                    "concept_code": "SNOMED:387458008",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.92,
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-rajesh-vit-01",
                    "category": "vital",
                    "field": "heart_rate",
                    "value": "114 bpm (Irregular)",
                    "normalized_concept": "Tachycardia / Arrhythmia",
                    "provenance_tier": "TOUCH",
                    "confidence": 1.0,
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-rajesh-rx",
                    "filename": "rajesh_sharma_cardio_rx.jpg",
                    "title": "Cardiology Consultation Note & Anticoagulation Sheet",
                    "type": "prescription",
                    "header": "DEPARTMENT OF CARDIOLOGY — CARDIAC OPD",
                    "patient_name": "Rajesh Sharma",
                    "patient_info": "Age: 64Y / M | MRN: 2026-00102",
                    "body_lines": [
                        "Diagnosis: Non-valvular Atrial Fibrillation / Hypertension",
                        "Medications:",
                        "1. Tab. Warfarin 5mg OD (evening, target INR 2.0-3.0)",
                        "2. Tab. Metoprolol XL 25mg OD",
                        "WARNING: Strictly avoid OTC NSAIDs/Aspirin without physician consult.",
                    ],
                    "highlights": [
                        {"text": "Tab. Warfarin 5mg OD", "box": [80, 240, 460, 280], "color": "#DC2626"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 3: ANANYA MUKHERJEE (ACUTE DYSPNEA / ASTHMA RED FLAG)
        # =====================================================================
        {
            "case_key": "ananya_mukherjee",
            "patient": {
                "id": "pat-demo-ananya-003",
                "name": "Ananya Mukherjee",
                "age": 32,
                "gender": "female",
                "phone": "+91 97170 45678",
                "language": "en",
                "abha_id": "91-2718-2818-2845",
                "hospital_mrn": "MRN-2026-00103",
            },
            "encounter": {
                "id": "enc-demo-ananya-003",
                "token_number": "A-103",
                "language": "en",
                "channel": "android_byod",
                "status": "COMPLETED",
                "department": "General Medicine",
                "severity_badge": "RED",
            },
            "queue": {
                "token": "A-103",
                "department": "General Medicine",
                "status": "WAITING",
                "position": 3,
                "doctor_room": "OPD Room 101",
            },
            "clinical_facts": [
                {
                    "id": "fact-ananya-cc-01",
                    "category": "chief_complaint",
                    "field": "dyspnea",
                    "value": "Severe acute breathlessness and chest tightness with wheezing",
                    "patient_words": "I cannot catch my breath, chest feels extremely tight since last night.",
                    "normalized_concept": "Acute asthma exacerbation",
                    "concept_code": "SNOMED:26636000",
                    "provenance_tier": "TOUCH",
                    "source_type": "touch_input",
                    "confidence": 0.98,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-ananya-vit-01",
                    "category": "vital",
                    "field": "oxygen_saturation",
                    "value": "89 % (Hypoxemic)",
                    "normalized_concept": "Low SpO2",
                    "provenance_tier": "TOUCH",
                    "confidence": 1.0,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-ananya-med-01",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Salbutamol",
                    "dose": "100 mcg",
                    "frequency": "Inhaler SOS",
                    "normalized_concept": "Salbutamol inhaler",
                    "concept_code": "SNOMED:372897005",
                    "provenance_tier": "TOUCH",
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-ananya-rx",
                    "filename": "ananya_mukherjee_pulmonary_rx.jpg",
                    "title": "Pulmonology Asthma Management Plan",
                    "type": "prescription",
                    "header": "PULMONARY & CRITICAL CARE MEDICINE",
                    "patient_name": "Ananya Mukherjee",
                    "patient_info": "Age: 32Y / F | MRN: 2026-00103",
                    "body_lines": [
                        "Diagnosis: Moderate Persistent Bronchial Asthma",
                        "Plan:",
                        "1. Budesonide + Formoterol Inhaler 200/6 mcg 2 puffs BD",
                        "2. Salbutamol MDI 100mcg 2 puffs PRN for acute wheezing",
                        "Emergency trigger: If SpO2 < 92% report to ER immediately.",
                    ],
                    "highlights": [
                        {"text": "Budesonide + Formoterol 200/6", "box": [80, 240, 480, 280], "color": "#3B82F6"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 4: SUNITA PATEL (CRITICAL HIGH GLYCEMIC PANIC LAB RED FLAG)
        # =====================================================================
        {
            "case_key": "sunita_patel",
            "patient": {
                "id": "pat-demo-sunita-004",
                "name": "Sunita Patel",
                "age": 50,
                "gender": "female",
                "phone": "+91 99200 33445",
                "language": "hi",
                "abha_id": "91-1618-0339-8874",
                "hospital_mrn": "MRN-2026-00104",
            },
            "encounter": {
                "id": "enc-demo-sunita-004",
                "token_number": "A-104",
                "language": "hi",
                "channel": "ivr_phone",
                "status": "COMPLETED",
                "department": "General Medicine",
                "severity_badge": "RED",
            },
            "queue": {
                "token": "A-104",
                "department": "General Medicine",
                "status": "WAITING",
                "position": 4,
                "doctor_room": "OPD Room 101",
            },
            "call_session": {
                "id": "call-demo-sunita-004",
                "status": "COMPLETED",
                "language": "hi",
                "current_step": "completed",
                "turn_count": 4,
            },
            "clinical_facts": [
                {
                    "id": "fact-sunita-cc-01",
                    "category": "chief_complaint",
                    "field": "altered_state",
                    "value": "Extreme drowsiness, excessive thirst and blurred vision",
                    "patient_words": "बहुत ज़्यादा प्यास लग रही है, सिर घूम रहा है और कमज़ोरी है।",
                    "normalized_concept": "Diabetic hyperglycemia syndrome",
                    "concept_code": "SNOMED:80394007",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.95,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-sunita-lab-01",
                    "category": "lab_result",
                    "field": "fasting_blood_glucose",
                    "value": "342",
                    "normalized_concept": "Fasting blood glucose",
                    "concept_code": "SNOMED:166898004",
                    "provenance_tier": "OCR",
                    "source_type": "document_ocr",
                    "confidence": 0.98,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-sunita-med-01",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Glimepiride",
                    "dose": "2 mg",
                    "frequency": "OD",
                    "normalized_concept": "Glimepiride 2mg",
                    "concept_code": "SNOMED:318536001",
                    "provenance_tier": "TOUCH",
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-sunita-lab",
                    "filename": "sunita_patel_glucose_panic_report.jpg",
                    "title": "Emergency STAT Blood Sugar Analysis",
                    "type": "lab_report",
                    "header": "DEPARTMENT OF CLINICAL PATHOLOGY & METABOLISM",
                    "patient_name": "Sunita Patel",
                    "patient_info": "Age: 50Y / F | MRN: 2026-00104 | Urgency: STAT",
                    "body_lines": [
                        "TEST                             RESULT      REFERENCE RANGE",
                        "-------------------------------------------------------------",
                        "Fasting Blood Glucose (FBS)       342 mg/dL   70 - 99 mg/dL (CRITICAL)",
                        "Urine Ketones                     Positive (+) Negative",
                        "Serum Sodium                     132 mEq/L   135 - 145 mEq/L",
                        "ALERT: PANIC CRITICAL HIGH GLUCOSE. NOTIFY PHYSICIAN STAT.",
                    ],
                    "highlights": [
                        {"text": "FBS: 342 mg/dL (CRITICAL)", "box": [80, 200, 520, 240], "color": "#DC2626"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 5: BALWINDER SINGH (ANGINA PECTORIS RADIATING TO LEFT ARM - RED)
        # =====================================================================
        {
            "case_key": "balwinder_singh",
            "patient": {
                "id": "pat-demo-balwinder-005",
                "name": "Balwinder Singh",
                "age": 61,
                "gender": "male",
                "phone": "+91 98765 11223",
                "language": "hi",
                "abha_id": "91-9988-7766-5544",
                "hospital_mrn": "MRN-2026-00105",
            },
            "encounter": {
                "id": "enc-demo-balwinder-005",
                "token_number": "A-105",
                "language": "hi",
                "channel": "kiosk",
                "status": "COMPLETED",
                "department": "Cardiology",
                "severity_badge": "RED",
            },
            "queue": {
                "token": "A-105",
                "department": "Cardiology",
                "status": "WAITING",
                "position": 5,
                "doctor_room": "OPD Room 108",
            },
            "clinical_facts": [
                {
                    "id": "fact-balwinder-cc-01",
                    "category": "chief_complaint",
                    "field": "chest_pain",
                    "value": "Substernal chest heaviness radiating to left arm and jaw",
                    "patient_words": "चलने पर छाती में भारीपन और बाएँ हाथ में दर्द होता है।",
                    "normalized_concept": "Angina pectoris with radiation",
                    "concept_code": "SNOMED:194828000",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.97,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-balwinder-med-01",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Atorvastatin",
                    "dose": "40 mg",
                    "frequency": "HS",
                    "normalized_concept": "Atorvastatin 40mg",
                    "concept_code": "SNOMED:318903004",
                    "provenance_tier": "OCR",
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-balwinder-ecg",
                    "filename": "balwinder_singh_ecg_note.jpg",
                    "title": "Emergency Cardiology Assessment & ECG Note",
                    "type": "prescription",
                    "header": "CARDIAC EMERGENCY TRIAGE SERVICE",
                    "patient_name": "Balwinder Singh",
                    "patient_info": "Age: 61Y / M | MRN: 2026-00105",
                    "body_lines": [
                        "Clinical Impression: Acute Coronary Syndrome / Unstable Angina",
                        "12-Lead ECG: ST-segment depression in Leads II, III, aVF (0.15 mV)",
                        "Immediate Plan: Sorbitrate 5mg SL SOS, Troponin-I test STAT",
                        "Cardiology admission recommended.",
                    ],
                    "highlights": [
                        {"text": "ACS / Unstable Angina", "box": [80, 200, 480, 240], "color": "#EF4444"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 6: MEENAKSHI SUNDARAM (AYUSH HERB-DRUG INTERACTION: LICORICE + AMLODIPINE)
        # =====================================================================
        {
            "case_key": "meenakshi_sundaram",
            "patient": {
                "id": "pat-demo-meenakshi-006",
                "name": "Meenakshi Sundaram",
                "age": 48,
                "gender": "female",
                "phone": "+91 94440 98765",
                "language": "ta",
                "abha_id": "91-4455-6677-8899",
                "hospital_mrn": "MRN-2026-00106",
            },
            "encounter": {
                "id": "enc-demo-meenakshi-006",
                "token_number": "B-201",
                "language": "ta",
                "channel": "kiosk",
                "status": "COMPLETED",
                "department": "Kayachikitsa",
                "severity_badge": "YELLOW",
            },
            "queue": {
                "token": "B-201",
                "department": "Kayachikitsa",
                "status": "WAITING",
                "position": 6,
                "doctor_room": "OPD Room 204",
            },
            "clinical_facts": [
                {
                    "id": "fact-meenakshi-cc-01",
                    "category": "chief_complaint",
                    "field": "joint_pain",
                    "value": "Chronic knee joint pain and morning stiffness",
                    "patient_words": "மூட்டு வலி மற்றும் காலையில் விரல்கள் இறுகிப் போகிறது.",
                    "normalized_concept": "Arthralgia / Sandhivata",
                    "concept_code": "NAMASTE:AYU-ROGA-014",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.94,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-meenakshi-med-01",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Amlodipine",
                    "dose": "5 mg",
                    "frequency": "OD",
                    "normalized_concept": "Amlodipine 5mg",
                    "concept_code": "SNOMED:324024003",
                    "provenance_tier": "OCR",
                    "source_type": "document_ocr",
                    "confidence": 0.95,
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-meenakshi-med-02",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Licorice_Yashtimadhu",
                    "dose": "3 g",
                    "frequency": "BD with warm water",
                    "patient_words": "நாட்டு மருந்து கடையில் அதிமதுரம் பொடி சாப்பிடுகிறேன்",
                    "normalized_concept": "Glycyrrhiza glabra (Yashtimadhu)",
                    "concept_code": "NAMASTE:AYU-DRUG-045",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.93,
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-meenakshi-med-03",
                    "category": "medication",
                    "field": "stopped_medication",
                    "value": "Diclofenac",
                    "dose": "50 mg",
                    "patient_words": "வயிற்று வலி ஏற்பட்டதால் டைக்ளோஃபெனாக் நிறுத்திவிட்டேன்",
                    "normalized_concept": "Diclofenac 50mg",
                    "concept_code": "SNOMED:318465001",
                    "provenance_tier": "VOICE",
                    "temporal_state": "stopped",
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-meenakshi-ayush-01",
                    "category": "ayush_agni",
                    "field": "manda_agni",
                    "value": "Manda Agni with Ama accumulation",
                    "concept_code": "NAMASTE:AYU-AGNI-002",
                    "provenance_tier": "VOICE",
                    "confidence": 0.91,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-meenakshi-ayush-02",
                    "category": "ayush_prakriti",
                    "field": "prakriti_assessment",
                    "value": "Vata-Kapha Prakriti",
                    "concept_code": "NAMASTE:AYU-PRAK-002",
                    "provenance_tier": "VOICE",
                    "confidence": 0.90,
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-meenakshi-rx",
                    "filename": "meenakshi_sundaram_ayush_rx.jpg",
                    "title": "Integrative AYUSH Kayachikitsa Prescription",
                    "type": "prescription",
                    "header": "AIIA AYUSH INTEGRATIVE OPD — KAYACHIKITSA DEPT",
                    "patient_name": "Meenakshi Sundaram",
                    "patient_info": "Age: 48Y / F | MRN: 2026-00106",
                    "body_lines": [
                        "Nidana: Sandhivata (Osteoarthritis) / Vata-Kapha Prakriti",
                        "Chikitsa Plan:",
                        "1. Yashtimadhu Churna 3g BD with lukewarm water",
                        "2. Yogaraj Guggulu 2 tabs BD after meals",
                        "Note: Patient also on Allopathic Tab. Amlodipine 5mg for HTN.",
                        "Advisory: Monitor BP weekly; Glycyrrhizin may oppose Amlodipine.",
                    ],
                    "highlights": [
                        {"text": "Yashtimadhu Churna 3g BD", "box": [80, 240, 480, 280], "color": "#F59E0B"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 7: ARVIND JOSHI (AYUSH HERB-DRUG INTERACTION: ASHWAGANDHA + DIAZEPAM)
        # =====================================================================
        {
            "case_key": "arvind_joshi",
            "patient": {
                "id": "pat-demo-arvind-007",
                "name": "Arvind Joshi",
                "age": 55,
                "gender": "male",
                "phone": "+91 98220 55667",
                "language": "mr",
                "abha_id": "91-5566-7788-9900",
                "hospital_mrn": "MRN-2026-00107",
            },
            "encounter": {
                "id": "enc-demo-arvind-007",
                "token_number": "B-202",
                "language": "mr",
                "channel": "android_byod",
                "status": "COMPLETED",
                "department": "Kayachikitsa",
                "severity_badge": "YELLOW",
            },
            "queue": {
                "token": "B-202",
                "department": "Kayachikitsa",
                "status": "WAITING",
                "position": 7,
                "doctor_room": "OPD Room 204",
            },
            "clinical_facts": [
                {
                    "id": "fact-arvind-cc-01",
                    "category": "chief_complaint",
                    "field": "anxiety_insomnia",
                    "value": "Chronic insomnia, restlessness and excessive daytime sleepiness",
                    "patient_words": "काही दिवसांपासून रात्री झोप येत नाही आणि दिवसा खूप गुंगी वाटते.",
                    "normalized_concept": "Insomnia and somnolence",
                    "concept_code": "SNOMED:84757009",
                    "provenance_tier": "VOICE",
                    "source_type": "patient_voice",
                    "confidence": 0.93,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-arvind-med-01",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Diazepam",
                    "dose": "5 mg",
                    "frequency": "HS",
                    "normalized_concept": "Diazepam 5mg",
                    "concept_code": "SNOMED:318451006",
                    "provenance_tier": "OCR",
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-arvind-med-02",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Ashwagandha",
                    "dose": "500 mg",
                    "frequency": "BD",
                    "patient_words": "अश्वगंधा चूर्ण ताक किंवा दुधासोबत घेतोय",
                    "normalized_concept": "Withania somnifera (Ashwagandha)",
                    "concept_code": "NAMASTE:AYU-DRUG-012",
                    "provenance_tier": "VOICE",
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-arvind-ayush-01",
                    "category": "ayush_agni",
                    "field": "vishama_agni",
                    "value": "Vishama Agni (Irregular appetite and digestion)",
                    "concept_code": "NAMASTE:AYU-AGNI-001",
                    "provenance_tier": "VOICE",
                    "confidence": 0.90,
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-arvind-rx",
                    "filename": "arvind_joshi_rx.jpg",
                    "title": "Neuropsychiatry & Wellness Prescription Note",
                    "type": "prescription",
                    "header": "DEPARTMENT OF CLINICAL NEUROLOGY & WELLNESS",
                    "patient_name": "Arvind Joshi",
                    "patient_info": "Age: 55Y / M | MRN: 2026-00107",
                    "body_lines": [
                        "Diagnosis: Chronic Primary Insomnia / Generalized Anxiety",
                        "Rx:",
                        "1. Tab. Diazepam 5mg at bedtime x 14 days",
                        "OTC Note: Patient using Ayurvedic Ashwagandha extract 500mg BD.",
                        "Interaction Alert: Excessive sedation hazard due to additive GABA-mimetic effects.",
                    ],
                    "highlights": [
                        {"text": "Tab. Diazepam 5mg", "box": [80, 240, 480, 280], "color": "#F59E0B"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 8: DEEPA DESHMUKH (AYUSH HERB-DRUG INTERACTION: TRIPHALA + METFORMIN)
        # =====================================================================
        {
            "case_key": "deepa_deshmukh",
            "patient": {
                "id": "pat-demo-deepa-008",
                "name": "Deepa Deshmukh",
                "age": 56,
                "gender": "female",
                "phone": "+91 97654 33221",
                "language": "mr",
                "abha_id": "91-6677-8899-0011",
                "hospital_mrn": "MRN-2026-00108",
            },
            "encounter": {
                "id": "enc-demo-deepa-008",
                "token_number": "B-203",
                "language": "mr",
                "channel": "kiosk",
                "status": "COMPLETED",
                "department": "General Medicine",
                "severity_badge": "YELLOW",
            },
            "queue": {
                "token": "B-203",
                "department": "General Medicine",
                "status": "WAITING",
                "position": 8,
                "doctor_room": "OPD Room 101",
            },
            "clinical_facts": [
                {
                    "id": "fact-deepa-cc-01",
                    "category": "chief_complaint",
                    "field": "diabetes_followup",
                    "value": "Type 2 Diabetes mellitus routine 3-month review",
                    "patient_words": "मधुमेहाची नियमित तपासणी करायची आहे.",
                    "normalized_concept": "Type 2 diabetes follow-up",
                    "concept_code": "SNOMED:44054006",
                    "provenance_tier": "VOICE",
                    "confidence": 0.95,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-deepa-med-01",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Metformin",
                    "dose": "1000 mg",
                    "frequency": "BD",
                    "normalized_concept": "Metformin 1000mg",
                    "concept_code": "SNOMED:318466000",
                    "provenance_tier": "OCR",
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-deepa-med-02",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Triphala",
                    "dose": "5 g",
                    "frequency": "HS with warm water",
                    "patient_words": "पोटासाठी रोज रात्री त्रिफळा चूर्ण घेते",
                    "normalized_concept": "Triphala Churna",
                    "concept_code": "NAMASTE:AYU-FORM-009",
                    "provenance_tier": "VOICE",
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-deepa-rx",
                    "filename": "deepa_deshmukh_rx.jpg",
                    "title": "Diabetic Clinic OPD Follow-up Slip",
                    "type": "prescription",
                    "header": "COMMUNITY DIABETES & METABOLIC CARE CLINIC",
                    "patient_name": "Deepa Deshmukh",
                    "patient_info": "Age: 56Y / F | MRN: 2026-00108",
                    "body_lines": [
                        "Diagnosis: T2DM on Oral Hypoglycemic Therapy",
                        "Medication: Tab. Metformin 1000mg SR BD (post meals)",
                        "Ayurvedic adjunct: Triphala Churna 5g HS",
                        "Precaution: Monitor for additive hypoglycemic symptoms (sweating, tremor).",
                    ],
                    "highlights": [
                        {"text": "Metformin 1000mg SR BD", "box": [80, 240, 480, 280], "color": "#10B981"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 9: PRIYA NAIR (AYUSH DYSPEPSIA / AMLAPITTA - GREEN)
        # =====================================================================
        {
            "case_key": "priya_nair",
            "patient": {
                "id": "pat-demo-priya-009",
                "name": "Priya Nair",
                "age": 29,
                "gender": "female",
                "phone": "+91 94470 12345",
                "language": "en",
                "abha_id": "91-7788-9900-1122",
                "hospital_mrn": "MRN-2026-00109",
            },
            "encounter": {
                "id": "enc-demo-priya-009",
                "token_number": "C-301",
                "language": "en",
                "channel": "android_byod",
                "status": "COMPLETED",
                "department": "Kayachikitsa",
                "severity_badge": "GREEN",
            },
            "queue": {
                "token": "C-301",
                "department": "Kayachikitsa",
                "status": "WAITING",
                "position": 9,
                "doctor_room": "OPD Room 204",
            },
            "clinical_facts": [
                {
                    "id": "fact-priya-cc-01",
                    "category": "chief_complaint",
                    "field": "dyspepsia",
                    "value": "Burning sensation in epigastrium and acid regurgitation",
                    "patient_words": "Burning in chest and sour belching especially after spicy food.",
                    "normalized_concept": "Amlapitta / GERD",
                    "concept_code": "NAMASTE:AYU-ROGA-003",
                    "provenance_tier": "VOICE",
                    "confidence": 0.94,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-priya-ayush-01",
                    "category": "ayush_agni",
                    "field": "tikshna_agni",
                    "value": "Tikshna Agni (Sharp, hyperactive digestive fire)",
                    "concept_code": "NAMASTE:AYU-AGNI-003",
                    "provenance_tier": "VOICE",
                    "confidence": 0.92,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-priya-ayush-02",
                    "category": "ayush_prakriti",
                    "field": "prakriti_assessment",
                    "value": "Pitta Prakriti",
                    "concept_code": "NAMASTE:AYU-PRAK-001",
                    "provenance_tier": "VOICE",
                    "confidence": 0.91,
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-priya-rx",
                    "filename": "priya_nair_gastro_rx.jpg",
                    "title": "Digestive Health Clinic Case Record",
                    "type": "prescription",
                    "header": "INTEGRATIVE GASTROENTEROLOGY & LIFESTYLE CLINIC",
                    "patient_name": "Priya Nair",
                    "patient_info": "Age: 29Y / F | MRN: 2026-00109",
                    "body_lines": [
                        "Diagnosis: Functional Dyspepsia (Amlapitta)",
                        "Prescription:",
                        "1. Avipattikar Churna 3g before food BD with honey",
                        "2. Kamadudha Rasa 1 tab BD after meals",
                        "Dietary advise: Avoid excessively pungent, fermented and sour food.",
                    ],
                    "highlights": [
                        {"text": "Avipattikar Churna 3g BD", "box": [80, 240, 480, 280], "color": "#10B981"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 10: VENKATESH RAO (OSTEOARTHRITIS KNEE - GREEN)
        # =====================================================================
        {
            "case_key": "venkatesh_rao",
            "patient": {
                "id": "pat-demo-venkatesh-010",
                "name": "Venkatesh Rao",
                "age": 67,
                "gender": "male",
                "phone": "+91 98490 66778",
                "language": "te",
                "abha_id": "91-8899-0011-2233",
                "hospital_mrn": "MRN-2026-00110",
            },
            "encounter": {
                "id": "enc-demo-venkatesh-010",
                "token_number": "C-302",
                "language": "te",
                "channel": "kiosk",
                "status": "COMPLETED",
                "department": "General Medicine",
                "severity_badge": "GREEN",
            },
            "queue": {
                "token": "C-302",
                "department": "General Medicine",
                "status": "WAITING",
                "position": 10,
                "doctor_room": "OPD Room 101",
            },
            "clinical_facts": [
                {
                    "id": "fact-venkatesh-cc-01",
                    "category": "chief_complaint",
                    "field": "knee_pain",
                    "value": "Bilateral knee joint pain aggravated by walking and stairs",
                    "patient_words": "రెండు మోకాళ్లలో నొప్పి, మెట్లు ఎక్కడం చాలా కష్టంగా ఉంది.",
                    "normalized_concept": "Bilateral knee osteoarthritis",
                    "concept_code": "SNOMED:239873007",
                    "provenance_tier": "VOICE",
                    "confidence": 0.95,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-venkatesh-med-01",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Calcium_Vit_D3",
                    "dose": "500 mg / 400 IU",
                    "frequency": "OD",
                    "normalized_concept": "Calcium with Vitamin D3",
                    "concept_code": "SNOMED:318854005",
                    "provenance_tier": "TOUCH",
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-venkatesh-xray",
                    "filename": "venkatesh_rao_ortho_note.jpg",
                    "title": "Orthopedic OPD Case Record & Knee Radiograph",
                    "type": "prescription",
                    "header": "DEPARTMENT OF ORTHOPEDIC SURGERY & REHABILITATION",
                    "patient_name": "Venkatesh Rao",
                    "patient_info": "Age: 67Y / M | MRN: 2026-00110",
                    "body_lines": [
                        "Clinical Impression: Bilateral Knee OA (Kellgren-Lawrence Grade II)",
                        "X-Ray Bilateral Knees: Medial compartment joint space narrowing",
                        "Plan: Quadriceps strengthening exercises, Tab. Calcium + Vit D3 OD",
                    ],
                    "highlights": [
                        {"text": "Bilateral Knee OA (Grade II)", "box": [80, 200, 480, 240], "color": "#3B82F6"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 11: SURESH VERMA (ALLERGIC RHINITIS - IVR CHANNEL - GREEN)
        # =====================================================================
        {
            "case_key": "suresh_verma",
            "patient": {
                "id": "pat-demo-suresh-011",
                "name": "Suresh Verma",
                "age": 38,
                "gender": "male",
                "phone": "+91 98100 22334",
                "language": "hi",
                "abha_id": "91-9900-1122-3344",
                "hospital_mrn": "MRN-2026-00111",
            },
            "encounter": {
                "id": "enc-demo-suresh-011",
                "token_number": "C-303",
                "language": "hi",
                "channel": "ivr_phone",
                "status": "COMPLETED",
                "department": "General Medicine",
                "severity_badge": "GREEN",
            },
            "queue": {
                "token": "C-303",
                "department": "General Medicine",
                "status": "WAITING",
                "position": 11,
                "doctor_room": "OPD Room 101",
            },
            "call_session": {
                "id": "call-demo-suresh-011",
                "status": "COMPLETED",
                "language": "hi",
                "current_step": "completed",
                "turn_count": 5,
            },
            "clinical_facts": [
                {
                    "id": "fact-suresh-cc-01",
                    "category": "chief_complaint",
                    "field": "rhinitis",
                    "value": "Frequent sneezing, watery rhinorrhea and itchy eyes for 1 week",
                    "patient_words": "छींकें आना, नाक बहना और आँखों में जलन हो रही है।",
                    "normalized_concept": "Allergic rhinitis",
                    "concept_code": "SNOMED:61582004",
                    "provenance_tier": "VOICE",
                    "confidence": 0.96,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-suresh-neg-01",
                    "category": "symptom",
                    "field": "fever",
                    "value": "Fever",
                    "patient_words": "बुखार बिल्कुल नहीं है",
                    "normalized_concept": "Absence of fever",
                    "provenance_tier": "VOICE",
                    "confidence": 0.98,
                    "is_negated": True,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-suresh-rx",
                    "filename": "suresh_verma_ent_rx.jpg",
                    "title": "Otorhinolaryngology (ENT) OPD Note",
                    "type": "prescription",
                    "header": "ENT & ALLERGY CARE DISPENSARY",
                    "patient_name": "Suresh Verma",
                    "patient_info": "Age: 38Y / M | MRN: 2026-00111",
                    "body_lines": [
                        "Diagnosis: Seasonal Allergic Rhinitis",
                        "Rx: Tab. Levocetirizine 5mg HS x 7 days",
                        "Nasal Saline spray BD",
                    ],
                    "highlights": [
                        {"text": "Tab. Levocetirizine 5mg HS", "box": [80, 240, 480, 280], "color": "#10B981"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 12: KAVITA KRISHNAN (HYPOTHYROIDISM ROUTINE REVIEW - GREEN)
        # =====================================================================
        {
            "case_key": "kavita_krishnan",
            "patient": {
                "id": "pat-demo-kavita-012",
                "name": "Kavita Krishnan",
                "age": 42,
                "gender": "female",
                "phone": "+91 94441 55667",
                "language": "ta",
                "abha_id": "91-1122-3344-5566",
                "hospital_mrn": "MRN-2026-00112",
            },
            "encounter": {
                "id": "enc-demo-kavita-012",
                "token_number": "C-304",
                "language": "ta",
                "channel": "android_byod",
                "status": "COMPLETED",
                "department": "General Medicine",
                "severity_badge": "GREEN",
            },
            "queue": {
                "token": "C-304",
                "department": "General Medicine",
                "status": "WAITING",
                "position": 12,
                "doctor_room": "OPD Room 101",
            },
            "clinical_facts": [
                {
                    "id": "fact-kavita-cc-01",
                    "category": "chief_complaint",
                    "field": "thyroid_review",
                    "value": "Routine 6-month hypothyroidism dosage titration review",
                    "patient_words": "தைராய்டு வழக்கமான பரிசோதனை மற்றும் மாத்திரை சரிபார்க்க வேண்டும்.",
                    "normalized_concept": "Hypothyroidism follow-up",
                    "concept_code": "SNOMED:40930008",
                    "provenance_tier": "TOUCH",
                    "confidence": 0.95,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-kavita-med-01",
                    "category": "medication",
                    "field": "current_medication",
                    "value": "Levothyroxine",
                    "dose": "75 mcg",
                    "frequency": "OD (Empty stomach)",
                    "normalized_concept": "Levothyroxine 75mcg",
                    "concept_code": "SNOMED:318548007",
                    "provenance_tier": "TOUCH",
                    "temporal_state": "taking",
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-kavita-lab",
                    "filename": "kavita_krishnan_thyroid_report.jpg",
                    "title": "Serum Thyroid Profile Radioimmunoassay",
                    "type": "lab_report",
                    "header": "ENDOCRINOLOGY INVESTIGATION CENTER",
                    "patient_name": "Kavita Krishnan",
                    "patient_info": "Age: 42Y / F | MRN: 2026-00112",
                    "body_lines": [
                        "PARAMETER                        RESULT       BIOLOGICAL INTERVAL",
                        "-----------------------------------------------------------------",
                        "Thyroid Stimulating Hormone (TSH)  2.8 uIU/mL   0.4 - 4.2 uIU/mL (EUTHYROID)",
                        "Free T4 (FT4)                     1.2 ng/dL    0.8 - 1.8 ng/dL",
                    ],
                    "highlights": [
                        {"text": "TSH: 2.8 uIU/mL (Normal)", "box": [80, 200, 500, 240], "color": "#10B981"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 13: MOHAMMED FAROOQ (CONTACT DERMATITIS - GREEN)
        # =====================================================================
        {
            "case_key": "mohammed_farooq",
            "patient": {
                "id": "pat-demo-farooq-013",
                "name": "Mohammed Farooq",
                "age": 45,
                "gender": "male",
                "phone": "+91 98200 44556",
                "language": "hi",
                "abha_id": "91-2233-4455-6677",
                "hospital_mrn": "MRN-2026-00113",
            },
            "encounter": {
                "id": "enc-demo-farooq-013",
                "token_number": "C-305",
                "language": "hi",
                "channel": "kiosk",
                "status": "COMPLETED",
                "department": "General Medicine",
                "severity_badge": "GREEN",
            },
            "queue": {
                "token": "C-305",
                "department": "General Medicine",
                "status": "WAITING",
                "position": 13,
                "doctor_room": "OPD Room 101",
            },
            "clinical_facts": [
                {
                    "id": "fact-farooq-cc-01",
                    "category": "chief_complaint",
                    "field": "dermatitis",
                    "value": "Pruritic erythematous macular rash over both forearms",
                    "patient_words": "हाथों पर खुजली और लाल दाने हो गए हैं।",
                    "normalized_concept": "Contact dermatitis",
                    "concept_code": "SNOMED:40275004",
                    "provenance_tier": "VOICE",
                    "confidence": 0.94,
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-farooq-rx",
                    "filename": "mohammed_farooq_derm_rx.jpg",
                    "title": "Dermatology & Skin Allergy Consultation Note",
                    "type": "prescription",
                    "header": "DEPARTMENT OF DERMATOLOGY & VENEREOLOGY",
                    "patient_name": "Mohammed Farooq",
                    "patient_info": "Age: 45Y / M | MRN: 2026-00113",
                    "body_lines": [
                        "Diagnosis: Subacute Allergic Contact Dermatitis (Forearms)",
                        "Rx: Calamine lotion local application TDS",
                        "Hydrocortisone 1% cream BD for 5 days",
                    ],
                    "highlights": [
                        {"text": "Calamine lotion TDS", "box": [80, 240, 480, 280], "color": "#10B981"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 14: GEETA BEN (LUMBAR MUSCLE SPASM - GREEN)
        # =====================================================================
        {
            "case_key": "geeta_ben",
            "patient": {
                "id": "pat-demo-geeta-014",
                "name": "Geeta Ben",
                "age": 52,
                "gender": "female",
                "phone": "+91 97230 77889",
                "language": "hi",
                "abha_id": "91-3344-5566-7788",
                "hospital_mrn": "MRN-2026-00114",
            },
            "encounter": {
                "id": "enc-demo-geeta-014",
                "token_number": "C-306",
                "language": "hi",
                "channel": "kiosk",
                "status": "COMPLETED",
                "department": "General Medicine",
                "severity_badge": "GREEN",
            },
            "queue": {
                "token": "C-306",
                "department": "General Medicine",
                "status": "WAITING",
                "position": 14,
                "doctor_room": "OPD Room 101",
            },
            "clinical_facts": [
                {
                    "id": "fact-geeta-cc-01",
                    "category": "chief_complaint",
                    "field": "lumbar_strain",
                    "value": "Lower back muscle pain and stiffness after lifting weight",
                    "patient_words": "कमर में तेज दर्द और खिंचाव है, झुकने में तकलीफ होती है।",
                    "normalized_concept": "Acute lumbosacral muscle strain",
                    "concept_code": "SNOMED:268023000",
                    "provenance_tier": "VOICE",
                    "confidence": 0.95,
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-geeta-rx",
                    "filename": "geeta_ben_physio_rx.jpg",
                    "title": "Physical Medicine & Rehabilitation OPD Note",
                    "type": "prescription",
                    "header": "DEPARTMENT OF PHYSICAL MEDICINE & REHABILITATION",
                    "patient_name": "Geeta Ben",
                    "patient_info": "Age: 52Y / F | MRN: 2026-00114",
                    "body_lines": [
                        "Impression: Acute Mechanical Low Back Ache (Lumbar Spasm)",
                        "Plan: Hot water fermentation, Paracetamol 650mg SOS",
                        "Avoid forward bending and heavy lifting for 7 days.",
                    ],
                    "highlights": [
                        {"text": "Paracetamol 650mg SOS", "box": [80, 240, 480, 280], "color": "#10B981"}
                    ]
                }
            ]
        },

        # =====================================================================
        # CASE 15: HARISH CHANDRA (ANNUAL HEALTH CHECKUP - GREEN)
        # =====================================================================
        {
            "case_key": "harish_chandra",
            "patient": {
                "id": "pat-demo-harish-015",
                "name": "Harish Chandra",
                "age": 60,
                "gender": "male",
                "phone": "+91 98118 99001",
                "language": "hi",
                "abha_id": "91-4455-6677-8899",
                "hospital_mrn": "MRN-2026-00115",
            },
            "encounter": {
                "id": "enc-demo-harish-015",
                "token_number": "C-307",
                "language": "hi",
                "channel": "kiosk",
                "status": "COMPLETED",
                "department": "General Medicine",
                "severity_badge": "GREEN",
            },
            "queue": {
                "token": "C-307",
                "department": "General Medicine",
                "status": "WAITING",
                "position": 15,
                "doctor_room": "OPD Room 101",
            },
            "clinical_facts": [
                {
                    "id": "fact-harish-cc-01",
                    "category": "chief_complaint",
                    "field": "general_checkup",
                    "value": "Annual routine preventative medical checkup and BP monitoring",
                    "patient_words": "सालाना स्वास्थ्य जाँच और बीपी चेक करवाने आया हूँ।",
                    "normalized_concept": "General health check",
                    "concept_code": "SNOMED:185349003",
                    "provenance_tier": "VOICE",
                    "confidence": 0.98,
                    "is_negated": False,
                    "status": "patient_confirmed",
                },
                {
                    "id": "fact-harish-vit-01",
                    "category": "vital",
                    "field": "blood_pressure",
                    "value": "122/80 mmHg",
                    "normalized_concept": "Normal blood pressure",
                    "provenance_tier": "TOUCH",
                    "confidence": 1.0,
                    "is_negated": False,
                    "status": "patient_confirmed",
                }
            ],
            "documents": [
                {
                    "id": "doc-demo-harish-lab",
                    "filename": "harish_chandra_annual_checkup.jpg",
                    "title": "Comprehensive Executive Health Checkup Summary",
                    "type": "lab_report",
                    "header": "PREVENTIVE HEALTHCARE CLINIC — ANNUAL SCREENING",
                    "patient_name": "Harish Chandra",
                    "patient_info": "Age: 60Y / M | MRN: 2026-00115",
                    "body_lines": [
                        "INVESTIGATION                    RESULT       STATUS",
                        "-----------------------------------------------------",
                        "Fasting Blood Glucose            92 mg/dL     NORMAL",
                        "Serum Creatinine                 0.95 mg/dL   NORMAL",
                        "Lipid Total Cholesterol          178 mg/dL    DESIRABLE",
                        "Resting ECG                      Within Normal Limits",
                    ],
                    "highlights": [
                        {"text": "FBS: 92 mg/dL (NORMAL)", "box": [80, 200, 480, 240], "color": "#10B981"}
                    ]
                }
            ]
        },
    ]
