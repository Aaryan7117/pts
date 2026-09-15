"""
Verification Script for AYUSH Context-Based Questioning & 5-Language Enforcement.
"""
import sys
from app.core.clinical.interview_engine import InterviewEngine, INTERVIEW_SECTIONS

def test_multilingual_sections():
    languages = ["en", "hi", "ta", "te", "mr"]
    for lang in languages:
        engine = InterviewEngine(language=lang, department="General Medicine")
        q = engine.get_current_question()
        assert q is not None, f"Opening question missing for {lang}"
        assert len(q["question_text"]) > 5, f"Question text too short for {lang}"
        print(f"[{lang.upper()}] Opening Q: {q['question_text'][:50]}...")
    print("[PASS] Multilingual section prompts verified across all 5 languages.")

def test_ayush_department_flow():
    for lang in ["ta", "te", "mr", "hi", "en"]:
        engine = InterviewEngine(language=lang, department="AYUSH (Ayurveda)")
        assert engine.is_ayush_stream is True
        assert engine.section_sequence[2] == "ayush_agni"
        assert engine.section_sequence[3] == "ayush_koshtha"
        assert engine.section_sequence[4] == "ayush_prakriti"

        # Turn 1: Chief complaint
        res1 = engine.process_response("Severe joint pain and indigestion")
        assert res1["next_question"]["section_id"] == "symptom_duration"

        # Turn 2: Duration
        res2 = engine.process_response("3-7 days")
        assert res2["next_question"]["section_id"] == "ayush_agni"

        # Turn 3: Agni response with NAMASTE code check
        res3 = engine.process_response("Sama Agni Balanced" if lang == "en" else ("सम अग्नि" if lang == "hi" else "சம அக்னி"))
        agni_fact = [f for f in res3["extracted_facts"] if f["category"] == "ayush_agni"][0]
        assert agni_fact["concept_code"] == "NAMASTE:AGNI-SAMA-001", f"Expected NAMASTE code, got {agni_fact}"
        assert res3["next_question"]["section_id"] == "ayush_koshtha"

        # Turn 4: Koshtha response with NAMASTE code check
        res4 = engine.process_response("Krura Koshtha Constipated" if lang == "en" else ("कब्ज क्रूर कोष्ठ" if lang == "hi" else "மலச்சிக்கல் க்ரூர"))
        koshtha_fact = [f for f in res4["extracted_facts"] if f["category"] == "ayush_koshtha"][0]
        assert koshtha_fact["concept_code"] == "NAMASTE:KOSHTHA-KRURA-001", f"Expected NAMASTE code, got {koshtha_fact}"
        assert res4["next_question"]["section_id"] == "ayush_prakriti"

        # Turn 5: Prakriti response with NAMASTE code check
        res5 = engine.process_response("Vata Cold Sensitive Dry Skin" if lang == "en" else ("वात ठंड परेशानी" if lang == "hi" else "வாதம் குளிர்"))
        prakriti_fact = [f for f in res5["extracted_facts"] if f["category"] == "ayush_prakriti"][0]
        assert prakriti_fact["concept_code"] == "NAMASTE:DOSHA-VATA-001", f"Expected NAMASTE code, got {prakriti_fact}"

        print(f"[{lang.upper()}] AYUSH Care Stream & NAMASTE coding verified!")

def test_context_adaptive_switch():
    # Patient starts in General Medicine, but chief complaint has digestive/joint symptoms
    engine = InterviewEngine(language="hi", department="General Medicine")
    assert engine.section_sequence[2] == "symptom_severity" # initially severity

    # Patient speaks stomach/acidity symptom
    res = engine.process_response("मुझे बहुत एसिडिटी और पेट में गैस व दर्द हो रहा है")
    # Engine dynamically switched sequence to prioritize Agni & Koshtha!
    assert "ayush_agni" in engine.section_sequence[2:5]
    print("[PASS] Dynamic context-based shift to AYUSH assessment verified!")

if __name__ == "__main__":
    test_multilingual_sections()
    test_ayush_department_flow()
    test_context_adaptive_switch()
    print("\nALL AYUSH MULTILINGUAL CONTEXT TESTS PASSED!")
