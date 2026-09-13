"""
Tests for MediKiosk AYUSH Dashavidha Pariksha Module.
Covers deterministic clinical scoring engines, NAMASTE ontology codes, and FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.clinical.ayush_engine import AyushEngine
from app.schemas.ayush import AyurvedicIntakeRecord


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ============================================================
#  CLINICAL ENGINE UNIT TESTS
# ============================================================

def test_prakriti_evaluation():
    """Verify constitutional scoring (Vata, Pitta, Kapha, Dvandvaja)."""
    # Pitta dominant profile
    pitta_inputs = {
        "body_frame": "medium_muscular",
        "skin_texture": "warm_reddish_sweaty",
        "digestion_speed": "rapid_sharp",
        "weather_sensitivity": "intolerant_to_heat",
        "sleep_pattern": "moderate_sound"
    }
    p_pitta = AyushEngine.evaluate_prakriti(pitta_inputs)
    assert p_pitta.dominant_dosha in ("pitta", "dvandvaja_vp", "dvandvaja_pk")
    assert "NAMASTE:" in p_pitta.namaste_code
    assert p_pitta.scores["pitta"] >= 3

    # Vata dominant profile
    vata_inputs = {
        "body_frame": "thin_light_prominent_joints",
        "skin_texture": "dry_rough_cool",
        "digestion_speed": "irregular_variable",
        "weather_sensitivity": "intolerant_to_cold",
        "sleep_pattern": "light_interrupted"
    }
    p_vata = AyushEngine.evaluate_prakriti(vata_inputs)
    assert p_vata.dominant_dosha == "vata"
    assert p_vata.namaste_code == "NAMASTE:DOSHA-VATA-001"
    assert p_vata.scores["vata"] == 10

    # Kapha dominant profile
    kapha_inputs = {
        "body_frame": "broad_sturdy_heavy",
        "skin_texture": "smooth_oily_cool",
        "digestion_speed": "slow_steady",
        "weather_sensitivity": "intolerant_to_dampness",
        "sleep_pattern": "heavy_prolonged"
    }
    p_kapha = AyushEngine.evaluate_prakriti(kapha_inputs)
    assert p_kapha.dominant_dosha == "kapha"
    assert p_kapha.namaste_code == "NAMASTE:DOSHA-KAPHA-001"
    assert p_kapha.scores["kapha"] == 10


def test_agni_and_ama_evaluation():
    """Verify digestive fire and metabolic toxin detection."""
    # Sama Agni (Nirama)
    sama_agni = AyushEngine.evaluate_agni({
        "appetite_pattern": "regular",
        "post_meal_heaviness": False,
        "bowel_regularity": "regular"
    })
    assert sama_agni.agni_type == "sama"
    assert sama_agni.post_meal_heaviness is False
    assert sama_agni.namaste_code == "NAMASTE:AGNI-SAMA-001"

    # Vishama Agni with Ama
    vishama_agni = AyushEngine.evaluate_agni({
        "appetite_pattern": "irregular_skips",
        "post_meal_heaviness": True,
        "bowel_regularity": "irregular"
    })
    assert vishama_agni.agni_type == "vishama"
    assert vishama_agni.post_meal_heaviness is True
    assert vishama_agni.namaste_code == "NAMASTE:AGNI-VISHAMA-001"

    # Tikshna Agni
    tikshna_agni = AyushEngine.evaluate_agni({
        "appetite_pattern": "excessive_burning"
    })
    assert tikshna_agni.agni_type == "tikshna"
    assert tikshna_agni.namaste_code == "NAMASTE:AGNI-TIKSHNA-001"


def test_koshtha_evaluation():
    """Verify bowel evacuation classification (Krura, Mridu, Madhyama)."""
    krura = AyushEngine.evaluate_koshtha({
        "bowel_frequency": "once_or_less_daily",
        "stool_consistency": "hard_dry"
    })
    assert krura.koshtha_type == "krura"
    assert krura.namaste_code == "NAMASTE:KOSHTHA-KRURA-001"

    mridu = AyushEngine.evaluate_koshtha({
        "stool_consistency": "soft_loose"
    })
    assert mridu.koshtha_type == "mridu"
    assert mridu.namaste_code == "NAMASTE:KOSHTHA-MRIDU-001"


def test_dosha_imbalance_detection():
    """Verify symptomatic Vikriti detection."""
    symptoms = ["constipation", "gas and bloating", "joint pain"]
    imbalances = AyushEngine.detect_dosha_imbalance(symptoms, agni="vishama", prakriti="vata")
    assert "vata_vriddhi" in imbalances


# ============================================================
#  FASTAPI ENDPOINT INTEGRATION TESTS
# ============================================================

def test_ayush_calculate_endpoint(client):
    """Verify POST /api/ayush/calculate real-time scoring."""
    payload = {
        "prakriti": {
            "body_frame": "thin_light_prominent_joints",
            "skin_texture": "dry_rough_cool",
            "weather_sensitivity": "intolerant_to_cold",
            "sleep_pattern": "light_interrupted"
        },
        "agni": {
            "appetite_pattern": "irregular_skips",
            "post_meal_heaviness": True,
            "bowel_regularity": "irregular"
        },
        "koshtha": {
            "bowel_frequency": "once_or_less_daily",
            "stool_consistency": "hard_dry"
        },
        "ahara_vihara": {
            "diet_primary_taste": ["katu", "lavana"],
            "packaged_junk_frequency": "frequent",
            "sleep_wake_timing": "late_night",
            "physical_exercise": "sedentary"
        },
        "symptoms": ["headache", "gas and bloating", "back pain"]
    }
    res = client.post("/api/ayush/calculate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["prakriti_baseline"]["dominant_dosha"] == "vata"
    assert data["prakriti_baseline"]["namaste_code"] == "NAMASTE:DOSHA-VATA-001"
    assert data["agni"]["agni_type"] == "vishama"
    assert data["agni"]["post_meal_heaviness"] is True
    assert data["koshtha"]["koshtha_type"] == "krura"
    assert "vata_vriddhi" in data["provisional_dosha_imbalance"]


def test_save_and_get_ayush_assessment(client):
    """Verify persisting Pariksha assessment for an encounter and reading it back."""
    # 1. Bootstrap an encounter
    b_res = client.post("/api/encounters/bootstrap", json={
        "patient_name": "Deepak Joshi",
        "preferred_language": "hi",
        "department": "Kayachikitsa (AYUSH)"
    })
    enc_id = b_res.json()["encounter_id"]

    # 2. Calculate and save assessment
    calculate_payload = {
        "prakriti": {
            "body_frame": "medium_muscular",
            "skin_texture": "warm_reddish_sweaty",
            "weather_sensitivity": "intolerant_to_heat",
            "sleep_pattern": "moderate_sound"
        },
        "agni": {
            "appetite_pattern": "excessive_burning",
            "post_meal_heaviness": False
        },
        "koshtha": {
            "stool_consistency": "soft_loose"
        },
        "ahara_vihara": {
            "diet_primary_taste": ["amla", "lavana"]
        }
    }
    calc_res = client.post("/api/ayush/calculate", json=calculate_payload)
    assert calc_res.status_code == 200
    assessment_record = calc_res.json()

    # 3. Save to encounter
    save_res = client.post(f"/api/ayush/encounter/{enc_id}/assessment", json=assessment_record)
    assert save_res.status_code == 200
    saved_data = save_res.json()
    assert saved_data["agni"]["agni_type"] == "tikshna"
    assert saved_data["koshtha"]["koshtha_type"] == "mridu"

    # 4. Get from encounter
    get_res = client.get(f"/api/ayush/encounter/{enc_id}/assessment")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["agni"]["agni_type"] == "tikshna"
    assert retrieved["koshtha"]["koshtha_type"] == "mridu"

    # 5. Check Doctor Patient Detail includes the saved AYUSH intake
    doc_res = client.get(f"/api/doctor/patient/{enc_id}")
    assert doc_res.status_code == 200
    doc_data = doc_res.json()
    assert doc_data["ayush_intake"] is not None
    assert doc_data["ayush_intake"]["agni"]["agni_type"] == "tikshna"
    assert doc_data["ayush_intake"]["koshtha"]["koshtha_type"] == "mridu"
