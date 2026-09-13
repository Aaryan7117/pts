"""
MediKiosk — AYUSH Dashavidha Pariksha Clinical Evaluation Engine
Implements authentic Ayurvedic clinical diagnostic logic:
- Prakriti Scoring (Constitutional Dosha)
- Agni Pariksha (Digestive Fire & Ama State)
- Koshtha Assessment (Bowel Rhythm)
- Ahara-Vihara Causative Factor (Nidana) Analysis
- NAMASTE / Morbidity Code Mapping
Ref: Charaka Samhita Vimanashthana 8 (Dashavidha Pariksha)
"""

from typing import Dict, Any, List
from app.schemas.ayush import (
    AgniAssessment,
    PrakritiAssessment,
    KoshthaAssessment,
    AharaViharaRecord,
    AyurvedicIntakeRecord
)


class AyushEngine:
    """Deterministic, rule-based diagnostic engine for AYUSH OPD triage."""

    @staticmethod
    def evaluate_prakriti(responses: Dict[str, Any]) -> PrakritiAssessment:
        """
        Evaluate patient's Prakriti (constitutional Dosha) from physical and physiological markers.
        """
        vata_score = 0
        pitta_score = 0
        kapha_score = 0

        # 1. Body Frame
        frame = responses.get("body_frame", "medium_muscular")
        if frame == "thin_light_prominent_joints":
            vata_score += 2
        elif frame == "medium_muscular":
            pitta_score += 2
        elif frame == "broad_sturdy_heavy":
            kapha_score += 2

        # 2. Skin Texture
        skin = responses.get("skin_texture", "warm_reddish_sweaty")
        if skin == "dry_rough_cool":
            vata_score += 2
        elif skin == "warm_reddish_sweaty":
            pitta_score += 2
        elif skin == "smooth_oily_cool":
            kapha_score += 2

        # 3. Digestion Speed
        digestion = responses.get("digestion_speed", "rapid_sharp")
        if digestion == "irregular_variable":
            vata_score += 2
        elif digestion == "rapid_sharp":
            pitta_score += 2
        elif digestion == "slow_steady":
            kapha_score += 2

        # 4. Weather Sensitivity
        weather = responses.get("weather_sensitivity", "intolerant_to_cold")
        if weather == "intolerant_to_cold":
            vata_score += 2
        elif weather == "intolerant_to_heat":
            pitta_score += 2
        elif weather == "intolerant_to_dampness":
            kapha_score += 2

        # 5. Sleep Pattern
        sleep = responses.get("sleep_pattern", "moderate_sound")
        if sleep == "light_interrupted":
            vata_score += 2
        elif sleep == "moderate_sound":
            pitta_score += 2
        elif sleep == "heavy_prolonged":
            kapha_score += 2

        # Compute Dominant Dosha
        scores_list = [("vata", vata_score), ("pitta", pitta_score), ("kapha", kapha_score)]
        scores_list.sort(key=lambda x: x[1], reverse=True)
        top1, s1 = scores_list[0]
        top2, s2 = scores_list[1]

        if s1 == s2 == scores_list[2][1]:
            dominant = "tridoshaja"
            code = "NAMASTE:DOSHA-TRIDOSHA-001"
        elif s1 - s2 <= 2:
            # Dual (Dvandvaja)
            pair = sorted([top1, top2])
            if pair == ["pitta", "vata"]:
                dominant = "dvandvaja_vp"
                code = "NAMASTE:DOSHA-VP-001"
            elif pair == ["kapha", "pitta"]:
                dominant = "dvandvaja_pk"
                code = "NAMASTE:DOSHA-PK-001"
            else:
                dominant = "dvandvaja_vk"
                code = "NAMASTE:DOSHA-VK-001"
        else:
            dominant = top1
            code = f"NAMASTE:DOSHA-{top1.upper()}-001"

        return PrakritiAssessment(
            dominant_dosha=dominant,
            body_frame=frame,
            skin_texture=skin,
            digestion_speed=digestion,
            weather_sensitivity=weather,
            sleep_pattern=sleep,
            namaste_code=code,
            scores={"vata": vata_score, "pitta": pitta_score, "kapha": kapha_score}
        )

    @staticmethod
    def evaluate_agni(responses: Dict[str, Any]) -> AgniAssessment:
        """
        Evaluate Agni (digestive capacity) and Ama (metabolic endotoxin) indicators.
        """
        appetite = responses.get("appetite_pattern", "regular")
        heaviness = bool(responses.get("post_meal_heaviness", False))
        bowel = responses.get("bowel_regularity", "regular")

        if appetite == "irregular_skips" or bowel == "constipated_hard":
            agni_type = "vishama"
            code = "NAMASTE:AGNI-VISHAMA-001"
        elif appetite == "excessive_burning" or bowel == "loose_burning":
            agni_type = "tikshna"
            code = "NAMASTE:AGNI-TIKSHNA-001"
        elif appetite == "low_absent" or bowel == "sluggish_mucus" or heaviness:
            agni_type = "manda"
            code = "NAMASTE:AGNI-MANDA-001"
        else:
            agni_type = "sama"
            code = "NAMASTE:AGNI-SAMA-001"

        return AgniAssessment(
            agni_type=agni_type,
            appetite_pattern=appetite,
            post_meal_heaviness=heaviness,
            bowel_regularity=bowel,
            namaste_code=code
        )

    @staticmethod
    def evaluate_koshtha(responses: Dict[str, Any]) -> KoshthaAssessment:
        """
        Evaluate Koshtha (bowel movement character).
        """
        frequency = responses.get("bowel_frequency", "once_daily")
        consistency = responses.get("stool_consistency", "soft_formed")

        if consistency in ("loose_watery", "soft_loose", "watery"):
            koshtha = "mridu"
            code = "NAMASTE:KOSHTHA-MRIDU-001"
        elif consistency in ("hard_dry", "hard", "constipated") or frequency == "once_or_less_daily":
            koshtha = "krura"
            code = "NAMASTE:KOSHTHA-KRURA-001"
        elif frequency == "twice_or_more_daily":
            koshtha = "mridu"
            code = "NAMASTE:KOSHTHA-MRIDU-001"
        else:
            koshtha = "madhyama"
            code = "NAMASTE:KOSHTHA-MADHYAMA-001"

        # Normalize to literal values
        if consistency in ("hard_dry", "hard", "constipated"):
            norm_consistency = "hard_dry"
        elif consistency in ("soft_loose", "loose_watery", "watery"):
            norm_consistency = "soft_loose"
        else:
            norm_consistency = "soft_formed"

        norm_freq = frequency if frequency in ("once_or_less_daily", "once_daily", "twice_or_more_daily") else "once_daily"

        return KoshthaAssessment(
            koshtha_type=koshtha,
            bowel_frequency=norm_freq,
            stool_consistency=norm_consistency,
            namaste_code=code
        )

    @staticmethod
    def detect_dosha_imbalance(
        symptoms: List[str],
        agni: str,
        prakriti: str
    ) -> List[str]:
        """
        Detect active Vikriti (pathological Dosha aggravation) from symptoms and digestive state.
        """
        imbalances = set()
        symptoms_str = " ".join(symptoms).lower()

        # Vata Vriddhi indicators (pain, dryness, stiffness, tremor, variable digestion)
        if any(w in symptoms_str for w in ["joint pain", "dry", "stiff", "ache", "constipation", "gas", "insomnia", "anxiety"]) or agni == "vishama":
            imbalances.add("vata_vriddhi")

        # Pitta Vriddhi indicators (burning, inflammation, acidity, heat, reddish, loose stool)
        if any(w in symptoms_str for w in ["burning", "acid", "heartburn", "fever", "rash", "red", "loose motion", "inflammation"]) or agni == "tikshna":
            imbalances.add("pitta_vriddhi")

        # Kapha Vriddhi indicators (mucus, heaviness, sluggishness, congestion, swelling)
        if any(w in symptoms_str for w in ["cough", "mucus", "heaviness", "swelling", "cold", "congestion", "lethargy", "sluggish"]) or agni == "manda":
            imbalances.add("kapha_vriddhi")

        if not imbalances:
            if "vata" in prakriti:
                imbalances.add("vata_vriddhi")
            else:
                imbalances.add("pitta_vriddhi")

        return list(imbalances)
