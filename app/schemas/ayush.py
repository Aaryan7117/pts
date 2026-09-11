"""
MediKiosk — Ministry of AYUSH Clinical Schemas
Machine-readable Pydantic models for Dashavidha Pariksha assessment.
Mapped to NAMASTE portal terminology and AIIA clinical workflows.
Ref: MediKiosk_Tech_Stack_Finalized.md Section 4
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional


class AgniAssessment(BaseModel):
    """Assessment of Digestive Fire (Agni) — Core diagnostic pillar in Ayurveda."""
    agni_type: Literal["sama", "vishama", "tikshna", "manda"] = Field(
        description="Sama: Balanced; Vishama: Irregular (Vata); Tikshna: Hyperactive (Pitta); Manda: Sluggish (Kapha)"
    )
    appetite_pattern: Literal["regular", "irregular_skips", "excessive_burning", "low_absent"]
    post_meal_heaviness: bool = Field(description="Indicates Ama (endotoxin accumulation)")
    bowel_regularity: Literal["regular", "constipated_hard", "loose_burning", "sluggish_mucus"]
    namaste_code: str = Field(default="NAMASTE:AGNI-001")


class PrakritiAssessment(BaseModel):
    """Constitutional Baseline Assessment (Prakriti vs. Vikriti)."""
    dominant_dosha: Literal[
        "vata", "pitta", "kapha",
        "dvandvaja_vp", "dvandvaja_pk", "dvandvaja_vk",
        "tridoshaja"
    ]
    body_frame: Literal["thin_light_prominent_joints", "medium_muscular", "broad_sturdy_heavy"]
    skin_texture: Literal["dry_rough_cool", "warm_reddish_sweaty", "smooth_oily_cool"]
    digestion_speed: Literal["irregular_variable", "rapid_sharp", "slow_steady"]
    weather_sensitivity: Literal["intolerant_to_cold", "intolerant_to_heat", "intolerant_to_dampness"]
    sleep_pattern: Literal["light_interrupted", "moderate_sound", "heavy_prolonged"]
    namaste_code: str = Field(default="NAMASTE:PRAKRITI-001")


class KoshthaAssessment(BaseModel):
    """Assessment of Koshtha (Bowel habit constitution)."""
    koshtha_type: Literal["krura", "mridu", "madhyama"] = Field(
        description="Krura: Hard/constipated (Vata); Mridu: Loose/easy (Pitta); Madhyama: Moderate (Kapha)"
    )
    bowel_frequency: Literal["once_or_less_daily", "once_daily", "twice_or_more_daily"]
    stool_consistency: Literal["hard_dry", "soft_formed", "loose_watery"]
    namaste_code: str = Field(default="NAMASTE:KOSHTHA-001")


class AharaViharaRecord(BaseModel):
    """Dietary and Lifestyle Causative Factors (Nidana)."""
    diet_primary_taste: list[Literal[
        "madhura", "amla", "lavana", "katu", "tikta", "kashaya"
    ]] = Field(description="Shadrasas — the six tastes predominant in patient's diet")
    packaged_junk_frequency: Literal["daily", "weekly", "rarely", "never"]
    sleep_wake_timing: Literal["brahma_muhurta", "regular_late", "night_shift_divasvapna"]
    physical_exercise: Literal["vyayama_daily", "occasional_walk", "sedentary"]
    water_intake: Optional[Literal["adequate", "low", "excessive"]] = None
    addictions: Optional[list[str]] = Field(
        default=None,
        description="Tobacco, alcohol, betel nut, etc."
    )


class AyurvedicIntakeRecord(BaseModel):
    """Complete machine-readable AYUSH intake for the Doctor Dashboard."""
    agni: Optional[AgniAssessment] = None
    prakriti_baseline: Optional[PrakritiAssessment] = None
    koshtha: Optional[KoshthaAssessment] = None
    ahara_vihara: Optional[AharaViharaRecord] = None
    provisional_dosha_imbalance: list[Literal[
        "vata_vriddhi", "pitta_vriddhi", "kapha_vriddhi"
    ]] = Field(default_factory=list)
    pending_doctor_examination: list[str] = Field(
        default=[
            "Nadi Pariksha (Pulse Examination)",
            "Jihva Pariksha (Tongue Examination)",
            "Sparsha Pariksha (Skin/Palpation)",
            "Mutra Pariksha (Urine Assessment)",
            "Mala Pariksha (Stool Assessment)"
        ],
        description="Checklist of physical pariksha requiring in-person physician assessment"
    )
