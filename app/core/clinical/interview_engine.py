"""
MediKiosk — Conversational Interview State Machine
Adaptive clinical intake flow that drives the call/kiosk conversation.

Sections (in order):
  1. Chief Complaint → 2. History of Present Illness → 3. Medications & Allergies →
  4. Past Medical History → 5. AYUSH Assessment (Agni, Prakriti) → 6. Summary & Confirm

Each section produces questions, processes answers, and transitions based on patient responses.
"""

import json
import logging
from typing import Optional
from app.core.clinical.normalizer import get_normalizer

logger = logging.getLogger("medikiosk.interview")


# Interview section definitions — each section has prompts in multiple languages
INTERVIEW_SECTIONS = [
    {
        "id": "chief_complaint",
        "order": 1,
        "prompts": {
            "hi": "आपको क्या परेशानी है? अपनी मुख्य शिकायत बताइए।",
            "en": "What is your main complaint? Please describe your primary concern.",
            "ta": "உங்கள் முக்கிய பிரச்சனை என்ன? தயவுசெய்து விவரிக்கவும்.",
            "te": "మీ ప్రధాన సమస్య ఏమిటి? దయచేసి వివరించండి.",
            "mr": "तुमची मुख्य तक्रार काय आहे? कृपया सांगा."
        },
        "fact_category": "chief_complaint",
        "max_follow_ups": 2
    },
    {
        "id": "symptom_duration",
        "order": 2,
        "prompts": {
            "hi": "यह समस्या कब से है? कितने दिन, हफ्ते, या महीने?",
            "en": "How long have you had this problem? Days, weeks, or months?",
            "ta": "இந்தப் பிரச்சனை எவ்வளவு காலமாக உள்ளது?",
            "te": "ఈ సమస్య ఎంతకాలంగా ఉంది?",
            "mr": "ही समस्या किती दिवसांपासून आहे?"
        },
        "fact_category": "symptom",
        "fact_field": "duration",
        "max_follow_ups": 1
    },
    {
        "id": "symptom_severity",
        "order": 3,
        "prompts": {
            "hi": "1 से 10 के पैमाने पर दर्द या तकलीफ कितनी है?",
            "en": "On a scale of 1 to 10, how severe is the pain or discomfort?",
            "ta": "1 முதல் 10 வரை வலி எவ்வளவு கடுமையானது?",
            "te": "1 నుండి 10 వరకు నొప్పి ఎంత తీవ్రంగా ఉంది?",
            "mr": "1 ते 10 च्या प्रमाणात वेदना किती तीव्र आहे?"
        },
        "fact_category": "symptom",
        "fact_field": "severity",
        "max_follow_ups": 0
    },
    {
        "id": "current_medications",
        "order": 4,
        "prompts": {
            "hi": "आप इस समय कोई दवाई ले रहे हैं? कौन सी दवाइयाँ?",
            "en": "Are you currently taking any medications? Which ones?",
            "ta": "தற்போது ஏதேனும் மருந்துகள் எடுத்துக்கொள்கிறீர்களா?",
            "te": "ప్రస్తుతం ఏవైనా మందులు వాడుతున్నారా?",
            "mr": "सध्या तुम्ही कोणती औषधे घेत आहात?"
        },
        "fact_category": "medication",
        "max_follow_ups": 2
    },
    {
        "id": "stopped_medications",
        "order": 5,
        "prompts": {
            "hi": "क्या आपने कोई दवाई हाल ही में बंद की है? कौन सी और कब?",
            "en": "Have you recently stopped any medications? Which ones and when?",
            "ta": "சமீபத்தில் ஏதேனும் மருந்துகளை நிறுத்தினீர்களா?",
            "te": "ఇటీవల ఏవైనా మందులు ఆపారా?",
            "mr": "तुम्ही अलीकडे कोणते औषध बंद केले आहे?"
        },
        "fact_category": "medication",
        "fact_field": "stopped_medication",
        "max_follow_ups": 1
    },
    {
        "id": "allergies",
        "order": 6,
        "prompts": {
            "hi": "आपको किसी दवाई या खाने से एलर्जी है?",
            "en": "Do you have any drug or food allergies?",
            "ta": "உங்களுக்கு ஏதேனும் ஒவ்வாமை உள்ளதா?",
            "te": "మీకు ఏవైనా అలర్జీలు ఉన్నాయా?",
            "mr": "तुम्हाला कोणत्या औषधाची किंवा अन्नाची अॅलर्जी आहे?"
        },
        "fact_category": "allergy",
        "max_follow_ups": 1
    },
    {
        "id": "past_medical_history",
        "order": 7,
        "prompts": {
            "hi": "क्या आपको पहले से कोई बीमारी है? जैसे डायबिटीज, BP, थायरॉइड?",
            "en": "Do you have any existing medical conditions? Like diabetes, hypertension, thyroid?",
            "ta": "உங்களுக்கு நீரிழிவு, இரத்த அழுத்தம் போன்ற நோய்கள் உள்ளனவா?",
            "te": "మీకు డయాబెటిస్, BP వంటి వ్యాధులు ఉన్నాయా?",
            "mr": "तुम्हाला मधुमेह, BP, थायरॉइड यांसारखा कोणता आजार आहे?"
        },
        "fact_category": "symptom",
        "fact_field": "past_medical_history",
        "max_follow_ups": 1
    },
    {
        "id": "ayush_agni",
        "order": 8,
        "prompts": {
            "hi": "आपकी भूख कैसी है? खाना खाने के बाद पेट भारी लगता है?",
            "en": "How is your appetite? Do you feel heaviness after meals?",
            "ta": "உங்கள் பசி எப்படி இருக்கிறது? சாப்பிட்ட பிறகு வயிறு கனமாக இருக்கிறதா?",
            "te": "మీ ఆకలి ఎలా ఉంది? తిన్న తర్వాత కడుపు భారంగా అనిపిస్తుందా?",
            "mr": "तुमची भूक कशी आहे? जेवणानंतर पोट जड वाटते का?"
        },
        "fact_category": "ayush_agni",
        "max_follow_ups": 1
    },
    {
        "id": "ayush_prakriti",
        "order": 9,
        "prompts": {
            "hi": "आपको ठंड ज़्यादा लगती है, गर्मी ज़्यादा, या नमी? आपकी त्वचा कैसी है — रूखी, गर्म, या चिकनी?",
            "en": "Are you more sensitive to cold, heat, or humidity? Is your skin dry, warm, or oily?",
            "ta": "குளிர், வெப்பம் அல்லது ஈரப்பதம் - எது அதிகம் பாதிக்கிறது?",
            "te": "చలి, వేడి లేదా తేమ - ఏది ఎక్కువగా ఇబ్బంది పెడుతుంది?",
            "mr": "तुम्हाला थंडी, उष्णता, किंवा ओलसरपणा — कशाचा जास्त त्रास होतो?"
        },
        "fact_category": "ayush_prakriti",
        "max_follow_ups": 1
    },
    {
        "id": "lifestyle_vihara",
        "order": 10,
        "prompts": {
            "hi": "आपकी दिनचर्या कैसी है? नींद कैसी है? व्यायाम करते हैं?",
            "en": "Tell me about your daily routine. How is your sleep? Do you exercise?",
            "ta": "உங்கள் தினசரி நடவடிக்கை எப்படி? தூக்கம் எப்படி?",
            "te": "మీ దినచర్య ఎలా ఉంటుంది? నిద్ర ఎలా ఉంది?",
            "mr": "तुमची दैनंदिन दिनचर्या कशी आहे? झोप कशी येते?"
        },
        "fact_category": "ayush_ahara",
        "max_follow_ups": 0
    },
]


class InterviewEngine:
    """
    Drives the conversational intake flow across the kiosk and call channels.

    State Machine:
      - Tracks current section index + follow-up count per section
      - Processes each patient response through the normalizer
      - Generates adaptive follow-up questions using LLM (if needed)
      - Transitions to next section when current section is complete
    """

    def __init__(self, language: str = "hi"):
        self.language = language
        self.current_section_idx = 0
        self.follow_up_count = 0
        self.captured_facts: list[dict] = []
        self.is_completed = False
        self._normalizer = get_normalizer()

    def get_current_question(self) -> Optional[dict]:
        """Get the current question to ask the patient."""
        if self.is_completed or self.current_section_idx >= len(INTERVIEW_SECTIONS):
            self.is_completed = True
            return None

        section = INTERVIEW_SECTIONS[self.current_section_idx]
        prompt = section["prompts"].get(self.language, section["prompts"]["en"])

        return {
            "section_id": section["id"],
            "section_order": section["order"],
            "question_text": prompt,
            "fact_category": section["fact_category"],
            "is_follow_up": self.follow_up_count > 0
        }

    def process_response(self, transcript: str) -> dict:
        """
        Process a patient's response and extract clinical facts.

        Args:
            transcript: Transcribed text of patient's speech

        Returns:
            Dict with extracted facts, next question info, and completion status.
        """
        if self.is_completed:
            return {
                "extracted_facts": [],
                "next_question": None,
                "is_completed": True
            }

        section = INTERVIEW_SECTIONS[self.current_section_idx]

        # Normalize the response through NegEx + Embeddings
        match = self._normalizer.normalize(transcript, self.language)

        extracted_facts = []

        if match.is_negated:
            # Patient explicitly denied — record as negated fact
            extracted_facts.append({
                "category": section["fact_category"],
                "field": section.get("fact_field", section["id"]),
                "value": transcript,
                "is_negated": True,
                "confidence": match.score,
                "provenance": "NEGEX_DENIED",
                "concept": None,
                "concept_code": None
            })
        elif match.concept:
            # Got a concept match
            extracted_facts.append({
                "category": section["fact_category"],
                "field": section.get("fact_field", section["id"]),
                "value": transcript,
                "is_negated": False,
                "confidence": match.score,
                "provenance": f"EMBEDDING_{match.status}",
                "concept": match.concept.get("name"),
                "concept_code": match.concept.get("code")
            })
        else:
            # No concept match — raw fact, escalate to LLM later
            extracted_facts.append({
                "category": section["fact_category"],
                "field": section.get("fact_field", section["id"]),
                "value": transcript,
                "is_negated": False,
                "confidence": 0.5,
                "provenance": "RAW_TRANSCRIPT",
                "concept": None,
                "concept_code": None
            })

        self.captured_facts.extend(extracted_facts)

        # Decide: follow-up or advance to next section
        max_follow = section.get("max_follow_ups", 0)

        if self.follow_up_count < max_follow and match.status == "REQUIRES_EXPLAIN_BACK":
            self.follow_up_count += 1
        else:
            # Advance to next section
            self.current_section_idx += 1
            self.follow_up_count = 0

        # Get next question
        next_question = self.get_current_question()

        return {
            "extracted_facts": extracted_facts,
            "next_question": next_question,
            "is_completed": self.is_completed,
            "total_facts_captured": len(self.captured_facts)
        }

    def get_summary(self) -> dict:
        """Generate a summary of all captured facts for explain-back."""
        return {
            "total_facts": len(self.captured_facts),
            "sections_completed": self.current_section_idx,
            "total_sections": len(INTERVIEW_SECTIONS),
            "facts": self.captured_facts,
            "is_completed": self.is_completed
        }

    def get_opening_prompt(self) -> str:
        """Get the very first opening prompt for the conversation."""
        openings = {
            "hi": "नमस्ते, मैं ऑल इंडिया इंस्टीट्यूट ऑफ आयुर्वेदा का डिजिटल सहायक हूँ। आपको क्या परेशानी है?",
            "en": "Hello, I am the digital assistant of the All India Institute of Ayurveda. What is your main concern today?",
            "ta": "வணக்கம், நான் ஆல் இந்தியா இன்ஸ்டிடியூட் ஆஃப் ஆயுர்வேதாவின் டிஜிட்டல் உதவியாளர். உங்கள் முக்கிய பிரச்சனை என்ன?",
            "te": "నమస్కారం, నేను ఆల్ ఇండియా ఇన్స్టిట్యూట్ ఆఫ్ ఆయుర్వేద డిజిటల్ సహాయకుడిని. మీ ప్రధాన సమస్య ఏమిటి?",
            "mr": "नमस्कार, मी ऑल इंडिया इन्स्टिट्यूट ऑफ आयुर्वेदाचा डिजिटल सहाय्यक आहे. तुमची मुख्य समस्या काय आहे?"
        }
        return openings.get(self.language, openings["hi"])
