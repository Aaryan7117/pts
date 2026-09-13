"""
MediKiosk — Deterministic Pairwise Drug-Drug & Herb-Drug Interaction Engine
100% offline, executes in <1ms. Zero LLM hallucination risk.

Covers:
  - Allopathic-Allopathic critical interactions
  - AYUSH Herb-Drug interactions (Ashwagandha, Yashtimadhu, Guggulu, etc.)
  - Common OPD medication pairs

Ref: MediKiosk_Tech_Stack_Finalized.md Section 5A
"""

from typing import Optional
import logging

logger = logging.getLogger("medikiosk.drug_safety")


class DrugInteractionEngine:
    """
    Deterministic pairwise matrix covering common allopathic regimens and
    allopathic-ayurvedic herb-drug interactions. Zero LLM hallucination risk.

    Usage:
        alerts = DrugInteractionEngine.check_prescriptions(["metformin", "aspirin", "warfarin"])
    """

    # Key: tuple(sorted([drug_a, drug_b])) → interaction info
    # Drugs are stored as lowercase canonical names
    INTERACTION_MATRIX: dict[tuple[str, str], dict] = {
        # ==================== CRITICAL ====================
        ("metformin", "radiopaque_contrast"): {
            "severity": "CRITICAL",
            "warning": "Risk of Metformin-induced lactic acidosis. Contrast procedure requires withholding Metformin for 48 hrs.",
            "source": "CDSCO / FDA Black Box Warning"
        },
        ("aspirin", "warfarin"): {
            "severity": "CRITICAL",
            "warning": "Severe hemorrhage risk due to synergistic antiplatelet/anticoagulant activity.",
            "source": "Standard Pharmacopoeia"
        },
        ("clopidogrel", "warfarin"): {
            "severity": "CRITICAL",
            "warning": "Triple antithrombotic risk. Major bleeding hazard without gastric protection.",
            "source": "AHA/ACC Clinical Guidelines"
        },
        ("methotrexate", "trimethoprim"): {
            "severity": "CRITICAL",
            "warning": "Both are folate antagonists. Combined use may cause severe pancytopenia.",
            "source": "Clinical Rheumatology Guidelines"
        },

        # ==================== HIGH ====================
        ("methotrexate", "nsaids"): {
            "severity": "HIGH",
            "warning": "NSAIDs reduce renal clearance of Methotrexate, potentially causing severe bone marrow toxicity.",
            "source": "Clinical Rheumatology Guidelines"
        },
        ("ace_inhibitors", "potassium_supplements"): {
            "severity": "HIGH",
            "warning": "Risk of life-threatening hyperkalemia. Monitor serum potassium closely.",
            "source": "JNC Hypertension Guidelines"
        },
        ("digoxin", "amiodarone"): {
            "severity": "HIGH",
            "warning": "Amiodarone increases serum digoxin levels by 70-100%. Dose reduction required.",
            "source": "Cardiology Pharmacology"
        },
        ("ssri", "tramadol"): {
            "severity": "HIGH",
            "warning": "Risk of serotonin syndrome: agitation, hyperthermia, clonus.",
            "source": "FDA Safety Communication"
        },
        ("lithium", "nsaids"): {
            "severity": "HIGH",
            "warning": "NSAIDs decrease lithium excretion, risking lithium toxicity (tremor, confusion).",
            "source": "Standard Pharmacopoeia"
        },

        # ==================== AYUSH HERB-DRUG INTERACTIONS ====================
        ("ashwagandha", "sedatives"): {
            "severity": "MODERATE",
            "warning": "Ashwagandha possesses GABA-mimetic properties and may potentiate CNS depressants / benzodiazepines.",
            "source": "AYUSH Integrative Safety Database"
        },
        ("ashwagandha", "thyroid_medication"): {
            "severity": "MODERATE",
            "warning": "Ashwagandha may increase thyroid hormone levels, requiring dose adjustment of levothyroxine.",
            "source": "J Ayurveda Integr Med"
        },
        ("licorice_yashtimadhu", "antihypertensives"): {
            "severity": "MODERATE",
            "warning": "Glycyrrhizin in Yashtimadhu can induce pseudoaldosteronism, reducing antihypertensive efficacy.",
            "source": "AYUSH-Pharmacovigilance Database"
        },
        ("licorice_yashtimadhu", "diuretics"): {
            "severity": "MODERATE",
            "warning": "May worsen hypokalemia when combined with thiazide or loop diuretics.",
            "source": "AYUSH-Pharmacovigilance Database"
        },
        ("guggulu", "anticoagulants"): {
            "severity": "MODERATE",
            "warning": "Guggulsterone may enhance anticoagulant effects, increasing bleeding risk.",
            "source": "CCRAS Research Publications"
        },
        ("turmeric_haridra", "anticoagulants"): {
            "severity": "MODERATE",
            "warning": "Curcumin inhibits platelet aggregation. Combined with Warfarin/Aspirin may increase bleeding risk.",
            "source": "J Ethnopharmacol"
        },
        ("brahmi", "sedatives"): {
            "severity": "MODERATE",
            "warning": "Bacopa monnieri may potentiate sedative effects. Monitor for excessive drowsiness.",
            "source": "AYUSH Integrative Safety Database"
        },
        ("triphala", "diabetes_medication"): {
            "severity": "LOW",
            "warning": "Triphala may lower blood glucose levels. Monitor for additive hypoglycemia with oral hypoglycemics.",
            "source": "Ayu Journal"
        },
    }

    # Aliases: map common drug names to canonical interaction keys
    DRUG_ALIASES: dict[str, list[str]] = {
        "nsaids": ["ibuprofen", "diclofenac", "naproxen", "piroxicam", "indomethacin", "aspirin_high_dose"],
        "ace_inhibitors": ["enalapril", "ramipril", "lisinopril", "captopril", "perindopril"],
        "ssri": ["fluoxetine", "sertraline", "paroxetine", "escitalopram", "citalopram"],
        "sedatives": ["diazepam", "lorazepam", "alprazolam", "clonazepam", "zolpidem"],
        "anticoagulants": ["warfarin", "heparin", "enoxaparin", "rivaroxaban", "apixaban"],
        "antihypertensives": ["amlodipine", "losartan", "atenolol", "metoprolol", "nifedipine", "telmisartan"],
        "diuretics": ["furosemide", "hydrochlorothiazide", "spironolactone"],
        "thyroid_medication": ["levothyroxine", "thyroxine"],
        "diabetes_medication": ["metformin", "glimepiride", "glipizide", "sitagliptin"],
        "potassium_supplements": ["potassium_chloride", "k_dur"],
        "licorice_yashtimadhu": ["licorice", "yashtimadhu", "mulethi", "licorice_yashtimadhu"],
        "ashwagandha": ["ashwagandha", "withania_somnifera"],
        "guggulu": ["guggulu", "yogaraj_guggulu", "guggul"],
        "turmeric_haridra": ["turmeric", "haridra", "curcumin"],
        "triphala": ["triphala", "triphala_churna"],
    }

    @classmethod
    def _resolve_aliases(cls, drug_name: str) -> list[str]:
        """Resolve a drug name to its canonical group names plus itself."""
        normalized = drug_name.lower().strip().replace(" ", "_")
        result = [normalized]

        for group, members in cls.DRUG_ALIASES.items():
            if normalized in members:
                result.append(group)

        return result

    @classmethod
    def check_pair(cls, drug_a: str, drug_b: str) -> Optional[dict]:
        """Check a single drug pair for interaction. Returns alert dict or None."""
        names_a = cls._resolve_aliases(drug_a)
        names_b = cls._resolve_aliases(drug_b)

        for na in names_a:
            for nb in names_b:
                pair = tuple(sorted([na, nb]))
                rule = cls.INTERACTION_MATRIX.get(pair) or cls.INTERACTION_MATRIX.get((na, nb)) or cls.INTERACTION_MATRIX.get((nb, na))
                if rule:
                    return {
                        "drug_a": drug_a,
                        "drug_b": drug_b,
                        "severity": rule["severity"],
                        "clinical_warning": rule["warning"],
                        "evidence_source": rule["source"]
                    }
        return None

    @classmethod
    def check_prescriptions(cls, medications: list[str]) -> list[dict]:
        """
        Check all pairwise combinations for interactions.
        Returns list of alert dicts, sorted by severity.
        """
        alerts = []
        seen_pairs = set()

        for i in range(len(medications)):
            for j in range(i + 1, len(medications)):
                pair_key = tuple(sorted([medications[i].lower(), medications[j].lower()]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                alert = cls.check_pair(medications[i], medications[j])
                if alert:
                    alerts.append(alert)
                    logger.warning(
                        f"Drug interaction detected: {alert['drug_a']} + {alert['drug_b']} "
                        f"[{alert['severity']}]"
                    )

        # Sort by severity: CRITICAL > HIGH > MODERATE > LOW
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3}
        alerts.sort(key=lambda a: severity_order.get(a["severity"], 99))

        return alerts
