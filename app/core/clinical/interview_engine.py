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
        "fact_field": "agni_pattern",
        "max_follow_ups": 1
    },
    {
        "id": "ayush_koshtha",
        "order": 9,
        "prompts": {
            "hi": "पेट साफ होने की क्या स्थिति है? नियमित रहता है, कब्ज है, या पतला शौच होता है?",
            "en": "How are your bowel movements? Regular once daily, constipated and hard, or loose and frequent?",
            "ta": "மலம் கழிக்கும் முறை எப்படி உள்ளது? சீரானது, மலச்சிக்கல், அல்லது தளர்வானதா?",
            "te": "మలవిసర్జన ఎలా ఉంది? సాధారణం, మలబద్ధకం/గట్టిగా, లేదా వదులుగానా?",
            "mr": "पोट साफ होण्याची काय स्थिती आहे? नियमित, बद्धकोष्ठता, किंवा पातळ शौच?"
        },
        "fact_category": "ayush_koshtha",
        "fact_field": "koshtha_rhythm",
        "max_follow_ups": 1
    },
    {
        "id": "ayush_prakriti",
        "order": 10,
        "prompts": {
            "hi": "आपको ठंड ज़्यादा लगती है, गर्मी ज़्यादा, या नमी? आपकी त्वचा कैसी है — रूखी, गर्म, या चिकनी?",
            "en": "Are you more sensitive to cold, heat, or humidity? Is your skin dry, warm, or oily?",
            "ta": "குளிர், வெப்பம் அல்லது ஈரப்பதம் - எது அதிகம் பாதிக்கிறது?",
            "te": "చలి, వేడి లేదా తేమ - ఏది ఎక్కువగా ఇబ్బంది పెడుతుంది?",
            "mr": "तुम्हाला थंडी, उष्णता, किंवा ओलसरपणा — कशाचा जास्त त्रास होतो?"
        },
        "fact_category": "ayush_prakriti",
        "fact_field": "prakriti_sensitivity",
        "max_follow_ups": 1
    },
    {
        "id": "lifestyle_vihara",
        "order": 11,
        "prompts": {
            "hi": "आपकी दिनचर्या कैसी है? नींद कैसी है? व्यायाम करते हैं?",
            "en": "Tell me about your daily routine. How is your sleep? Do you exercise?",
            "ta": "உங்கள் தினசரி நடவடிக்கை எப்படி? தூக்கம் எப்படி?",
            "te": "మీ దినచర్య ఎలా ఉంటుంది? నిద్ర ఎలా ఉంది?",
            "mr": "तुमची दैनंदिन दिनचर्या कशी आहे? झोप कशी येते?"
        },
        "fact_category": "ayush_ahara",
        "fact_field": "vihara_routine",
        "max_follow_ups": 0
    },
]

SECTIONS_BY_ID = {s["id"]: s for s in INTERVIEW_SECTIONS}


class InterviewEngine:
    """
    Drives the conversational intake flow across the kiosk and call channels.

    State Machine:
      - Tracks current section sequence + follow-up count per section
      - Dynamically adapts sequence based on department (AYUSH vs General Medicine)
        and symptom context (digestive/joint/chronic complaints)
      - Generates context-based follow-up questions tailored to the patient's reported symptoms
      - Provides localized suggested options for tactile touchscreen selection
      - Extracts NAMASTE and SNOMED-CT clinical concepts
      - Transitions smoothly to next section when current section is complete
    """

    def __init__(self, language: str = "hi", department: Optional[str] = None):
        self.language = language
        self.department = department
        self.is_ayush_stream = bool(department and "ayush" in department.lower())
        self.section_sequence = self._build_sequence()
        self.current_section_idx = 0
        self.follow_up_count = 0
        self.captured_facts: list[dict] = []
        self.is_completed = False
        self.primary_symptom_cluster: Optional[str] = None
        self.patient_reported_symptom: Optional[str] = None
        self._normalizer = get_normalizer()

    def _build_sequence(self) -> list[str]:
        if self.is_ayush_stream:
            return [
                "chief_complaint",
                "symptom_duration",
                "ayush_agni",
                "ayush_koshtha",
                "ayush_prakriti",
                "symptom_severity",
                "current_medications",
                "allergies",
                "lifestyle_vihara"
            ]
        return [
            "chief_complaint",
            "symptom_duration",
            "symptom_severity",
            "current_medications",
            "stopped_medications",
            "allergies",
            "past_medical_history",
            "ayush_agni",
            "ayush_koshtha",
            "ayush_prakriti",
            "lifestyle_vihara"
        ]

    def _detect_symptom_cluster(self, text: str) -> Optional[str]:
        """Classify patient's reported complaint into clinical symptom clusters."""
        t = text.lower()

        # 1. Cardiac / Chest Pain (Emergency red-flag priority)
        if any(k in t for k in [
            "chest", "heart", "cardiac", "angina", "छाती", "दिल", "हृदय", "நெஞ்சு", "இதயம்", "ఛాతీ", "గుండె"
        ]):
            return "cardiac"

        # 2. Febrile / Infection
        if any(k in t for k in [
            "fever", "pyrexia", "chill", "rigor", "temperature", "बुखार", "ताप", "कपकपी", "காய்ச்சல்", "நடுக்கம்", "జ్వరం", "చలి"
        ]):
            return "fever"

        # 3. Respiratory / Cough / Cold
        if any(k in t for k in [
            "cough", "cold", "breath", "wheez", "asthma", "phlegm", "sputum", "mucus",
            "खांसी", "जुकाम", "सांस", "बलगम", "कफ", "खोकला", "सर्दी", "இருமல்", "சளி", "மூச்சு", "దగ్గు", "జలుబు", "శ్వాస"
        ]):
            return "cough"

        # 4. Gastrointestinal / Abdominal / Digestion
        if any(k in t for k in [
            "stomach", "abdom", "belly", "gas", "acid", "bloat", "vomit", "nausea", "loose", "diarrhea", "constipat",
            "पेट", "गैस", "एसिडिटी", "उल्टी", "दस्त", "कब्ज", "अपच", "पोट", "जळजळ", "उलट्या", "जुलाब", "बद्धकोष्ठता",
            "வயிறு", "செரிமானம்", "வாந்தி", "வயிற்றுப்போக்கு", "மலச்சிக்கல்", "కడుపు", "జీర్ణం", "వాంతులు", "విరేచనాలు", "మలబద్ధకం"
        ]):
            return "abdominal"

        # 5. Musculoskeletal / Joint / Back Pain
        if any(k in t for k in [
            "joint", "knee", "back", "spine", "arthritis", "stiff", "swelling",
            "जोड़", "घुटने", "कमर", "पीठ", "दर्द", "सांधे", "पाठ", "कंबर", "மூட்டு", "முழங்கால்", "முதுகு", "కీళ్ల", "మోకాలు", "వెన్ను"
        ]):
            return "joint"

        # 6. Neurological / Headache / Dizziness
        if any(k in t for k in [
            "headache", "migraine", "dizz", "vertigo", "giddiness", "faint",
            "सिरदर्द", "चक्कर", "डोकेदुखी", "தலையிடி", "தலைவலி", "மயக்கம்", "తలనొప్పి", "తలతిరగడం"
        ]):
            return "headache"

        return None

    def _check_ayush_context(self, text: str):
        """If patient reports chronic/digestive/joint issues, prioritize AYUSH clinical modules."""
        detected = self._detect_symptom_cluster(text)
        if detected:
            self.primary_symptom_cluster = detected
            self.patient_reported_symptom = text.strip()

        if self.is_ayush_stream:
            return

        ayush_triggers = [
            "joint", "pain", "gas", "acid", "constipat", "digestion", "stomach", "bloat",
            "indigestion", "back pain", "arthritis", "stiff", "vomit", "nausea",
            "कब्ज", "एसिडिटी", "दर्द", "अपच", "गैस", "पेट", "जोड़", "कमर",
            "செரிமானம்", "வயிறு", "மூட்டு", "மலச்சிக்கல்",
            "జీర్ణం", "కడుపు", "కీళ్ల", "మలబద్ధకం",
            "पोट", "सांधे", "बद्धकोष्ठता", "जळजळ"
        ]
        t_low = text.lower()
        if any(trig in t_low for trig in ayush_triggers):
            remaining_ayush = [
                s for s in [
                    "symptom_duration",
                    "ayush_agni",
                    "ayush_koshtha",
                    "ayush_prakriti",
                    "symptom_severity",
                    "current_medications",
                    "allergies",
                    "lifestyle_vihara"
                ] if s not in self.section_sequence[:self.current_section_idx + 1]
            ]
            self.section_sequence = self.section_sequence[:self.current_section_idx + 1] + remaining_ayush
            logger.info("Adaptive context shift: AYUSH assessment prioritized from patient complaint")

    def _get_contextual_question_and_options(self, section_id: str) -> tuple[str, list[dict]]:
        """
        Dynamically synthesize context-based questions and localized multi-choice options
        tailored to the patient's primary complaint across all 5 supported languages.
        """
        lang = self.language
        cluster = self.primary_symptom_cluster

        # =========================================================================
        # 1. AYUSH AGNI (Appetite / Digestion Assessment)
        # =========================================================================
        if section_id == "ayush_agni":
            prompts = {
                "hi": "आपकी भूख और पाचन की क्या स्थिति है? खाना खाने के बाद पेट कैसा महसूस होता है?",
                "en": "How is your appetite and digestion? How does your stomach feel after meals?",
                "ta": "உங்கள் பசி மற்றும் செரிமானம் எப்படி உள்ளது? சாப்பிட்ட பின் வயிறு எப்படி இருக்கிறது?",
                "te": "మీ ఆకలి మరియు జీర్ణక్రియ ఎలా ఉంది? తిన్న తర్వాత కడుపు ఎలా అనిపిస్తుంది?",
                "mr": "तुमची भूक आणि पचन कसे आहे? जेवणानंतर पोटात काय त्रास जाणवतो?"
            }
            options = {
                "hi": [
                    {"title": "समय पर सामान्य भूख (Sama Agni)", "subtitle": "पाचन अच्छा है, कोई भारीपन नहीं", "val": "Sama Agni"},
                    {"title": "अनियमित भूख व गैस (Vishama Agni)", "subtitle": "कभी बहुत तेज भूख, कभी बिल्कुल नहीं, पेट फूलना", "val": "Vishama Agni"},
                    {"title": "तेज भूख व एसिडिटी (Tikshna Agni)", "subtitle": "तेज जलन, भूख न सह पाना, खट्टी डकारें", "val": "Tikshna Agni"},
                    {"title": "मंदी भूख व भारीपन (Manda Agni)", "subtitle": "बिल्कुल भूख न लगना, खाने के बाद देर तक पेट भारी", "val": "Manda Agni"}
                ],
                "en": [
                    {"title": "Normal Appetite & Digestion (Sama Agni)", "subtitle": "Regular appetite, comfortable digestion without heaviness", "val": "Sama Agni"},
                    {"title": "Irregular Appetite & Bloating (Vishama Agni)", "subtitle": "Variable hunger, gas, bloating and uneasiness", "val": "Vishama Agni"},
                    {"title": "Intense Appetite & Acidity (Tikshna Agni)", "subtitle": "Excessive burning hunger, acid reflux, heartburn", "val": "Tikshna Agni"},
                    {"title": "Poor Appetite & Heaviness (Manda Agni)", "subtitle": "Loss of appetite, sluggish digestion, prolonged fullness", "val": "Manda Agni"}
                ],
                "ta": [
                    {"title": "சீரான பசி (Sama Agni)", "subtitle": "நேரத்திற்கு பசி, இயல்பான செரிமானம்", "val": "Sama Agni"},
                    {"title": "மாறுபடும் பசி மற்றும் வாயு (Vishama Agni)", "subtitle": "சில நேரம் அதிக பசி, சில நேரம் பசியின்மை", "val": "Vishama Agni"},
                    {"title": "அதிக பசி மற்றும் நெஞ்செரிச்சல் (Tikshna Agni)", "subtitle": "தீவிர பசி, தாங்க முடியாத அமிலத்தன்மை", "val": "Tikshna Agni"},
                    {"title": "மந்தமான பசி மற்றும் பாரம் (Manda Agni)", "subtitle": "பசியின்மை, சாப்பிட்ட பின் மந்தநிலை", "val": "Manda Agni"}
                ],
                "te": [
                    {"title": "సాధారణ ఆకలి (Sama Agni)", "subtitle": "సమయానికి ఆకలి, సులభంగా జీర్ణం", "val": "Sama Agni"},
                    {"title": "అస్థిరమైన ఆకలి మరియు గ్యాస్ (Vishama Agni)", "subtitle": "ఒక్కోసారి ఎక్కువ ఆకలి, ఒక్కోసారి అసలు లేకపోవడం", "val": "Vishama Agni"},
                    {"title": "విపరీతమైన ఆకలి & మంట (Tikshna Agni)", "subtitle": "తీవ్రమైన ఆకలి, కడుపులో మంట, ఎసిడిటీ", "val": "Tikshna Agni"},
                    {"title": "తక్కువ ఆకలి & బరువుగా ఉండటం (Manda Agni)", "subtitle": "ఆకలి లేకపోవడం, తిన్న తర్వాత కడుపు భారంగా ఉండటం", "val": "Manda Agni"}
                ],
                "mr": [
                    {"title": "वेळेवर सामान्य भूक (Sama Agni)", "subtitle": "पचन व्यवस्थित, कोणताही जडपणा नाही", "val": "Sama Agni"},
                    {"title": "अनियमित भूक आणि गॅस (Vishama Agni)", "subtitle": "कधी खूप भूक, कधी अजिबात नाही, पोट फुगणे", "val": "Vishama Agni"},
                    {"title": "तीव्र भूक आणि जळजळ (Tikshna Agni)", "subtitle": "तीक्ष्ण भूक, ॲसिडिटी, छातीत जळजळ", "val": "Tikshna Agni"},
                    {"title": "मंद भूक आणि जडपणा (Manda Agni)", "subtitle": "भूक न लागणे, जेवणानंतर खूप वेळ पोट जड राहणे", "val": "Manda Agni"}
                ]
            }
            return prompts.get(lang, prompts["en"]), options.get(lang, options["en"])

        # =========================================================================
        # 2. AYUSH KOSHTHA (Bowel Rhythm Assessment)
        # =========================================================================
        if section_id == "ayush_koshtha":
            prompts = {
                "hi": "पेट साफ होने (शौच) की क्या स्थिति रहती है?",
                "en": "How are your bowel movements and evacuation patterns?",
                "ta": "மலம் கழிக்கும் முறை எப்படி உள்ளது?",
                "te": "మలవిసర్జన విధానం ఎలా ఉంది?",
                "mr": "पोट साफ होण्याची (शौचाची) काय स्थिती असते?"
            }
            options = {
                "hi": [
                    {"title": "प्रतिदिन सामान्य (Madhyama Koshtha)", "subtitle": "रोज 1-2 बार आसानी से पेट साफ होता है", "val": "Madhyama Koshtha"},
                    {"title": "कब्ज व कड़ा मल (Krura Koshtha)", "subtitle": "2-3 दिन में एक बार, बहुत जोर लगाना पड़ता है", "val": "Krura Koshtha"},
                    {"title": "ढीला व बार-बार (Mridu Koshtha)", "subtitle": "दिन में 3-4 बार पतला शौच, तुरंत जाना पड़ता है", "val": "Mridu Koshtha"}
                ],
                "en": [
                    {"title": "Regular Daily (Madhyama Koshtha)", "subtitle": "1-2 smooth, comfortable bowel motions daily", "val": "Madhyama Koshtha"},
                    {"title": "Hard & Constipated (Krura Koshtha)", "subtitle": "Evacuation once in 2-3 days, difficult straining", "val": "Krura Koshtha"},
                    {"title": "Loose & Frequent (Mridu Koshtha)", "subtitle": "Loose watery stools 3-4 times daily with urgency", "val": "Mridu Koshtha"}
                ],
                "ta": [
                    {"title": "சீரானது (Madhyama Koshtha)", "subtitle": "தினமும் 1-2 முறை இயல்பான மலம்", "val": "Madhyama Koshtha"},
                    {"title": "மலச்சிக்கல் (Krura Koshtha)", "subtitle": "2-3 நாட்களுக்கு ஒரு முறை, அதிக சிரமம்", "val": "Krura Koshtha"},
                    {"title": "தளர்வானது (Mridu Koshtha)", "subtitle": "நாளுக்கு 3-4 முறை நீர்த்துப் போதல்", "val": "Mridu Koshtha"}
                ],
                "te": [
                    {"title": "సాధారణం (Madhyama Koshtha)", "subtitle": "రోజుకు 1-2 సార్లు సాఫీగా విసర్జన", "val": "Madhyama Koshtha"},
                    {"title": "మలబద్ధకం (Krura Koshtha)", "subtitle": "2-3 రోజులకు ఒకసారి, విసర్జన కష్టం", "val": "Krura Koshtha"},
                    {"title": "వదులుగా (Mridu Koshtha)", "subtitle": "రోజుకు 3-4 సార్లు పల్చగా విసర్జన", "val": "Mridu Koshtha"}
                ],
                "mr": [
                    {"title": "नियमित (Madhyama Koshtha)", "subtitle": "दररोज 1-2 वेळा सहज पोट साफ", "val": "Madhyama Koshtha"},
                    {"title": "बद्धकोष्ठता (Krura Koshtha)", "subtitle": "2-3 दिवसांतून एकदा, कठीण शौच", "val": "Krura Koshtha"},
                    {"title": "पातळ शौच (Mridu Koshtha)", "subtitle": "दिवसातून 3-4 वेळा पातळ जुलाब", "val": "Mridu Koshtha"}
                ]
            }
            return prompts.get(lang, prompts["en"]), options.get(lang, options["en"])

        # =========================================================================
        # 3. AYUSH PRAKRITI (Thermal & Dosha Sensitivity)
        # =========================================================================
        if section_id == "ayush_prakriti":
            prompts = {
                "hi": "आपको मौसम में किस चीज़ से अधिक असुविधा होती है — ठंड, गर्मी या नमी?",
                "en": "What weather conditions cause you the most discomfort — cold, heat, or humidity?",
                "ta": "எந்த வானிலை உங்களுக்கு அதிக அசௌகரியத்தை ஏற்படுத்துகிறது — குளிர், வெப்பம் அல்லது ஈரப்பதம்?",
                "te": "వాతావరణంలో మీకు ఏది ఎక్కువ ఇబ్బంది కలిగిస్తుంది — చలి, వేడి లేదా తేమ?",
                "mr": "हवामानात तुम्हाला कशाचा जास्त त्रास होतो — थंडी, उष्णता की ओलसरपणा?"
            }
            options = {
                "hi": [
                    {"title": "ठंड व रूखापन (Vata Sensitivity)", "subtitle": "ठंड सहन नहीं होती, जोड़ों में दर्द व त्वचा रूखी रहती है", "val": "Vata Sensitivity"},
                    {"title": "गर्मी व धूप (Pitta Sensitivity)", "subtitle": "गर्मी बिल्कुल बर्दाश्त नहीं, अधिक पसीना व जलन", "val": "Pitta Sensitivity"},
                    {"title": "नमी व सर्द मौसम (Kapha Sensitivity)", "subtitle": "सर्द मौसम में भारीपन, कफ व आलस बढ़ता है", "val": "Kapha Sensitivity"}
                ],
                "en": [
                    {"title": "Sensitive to Cold & Dryness (Vata)", "subtitle": "Intolerant to cold weather, dry skin, joint ache", "val": "Vata Sensitivity"},
                    {"title": "Sensitive to Heat & Sun (Pitta)", "subtitle": "Intolerant to hot weather, profuse sweating, skin flushing", "val": "Pitta Sensitivity"},
                    {"title": "Sensitive to Cold & Damp (Kapha)", "subtitle": "Sluggish in rainy/damp weather, heavy congestion", "val": "Kapha Sensitivity"}
                ],
                "ta": [
                    {"title": "குளிர் மற்றும் வறட்சி (Vata)", "subtitle": "குளிர் தாங்க முடியாது, மூட்டு வலி மற்றும் வறண்ட தோல்", "val": "Vata Sensitivity"},
                    {"title": "வெப்பம் மற்றும் வெயில் (Pitta)", "subtitle": "வெப்பம் தாங்க இயலாது, அதிக வியர்வை", "val": "Pitta Sensitivity"},
                    {"title": "ஈரப்பதம் மற்றும் பனி (Kapha)", "subtitle": "மழைக்காலத்தில் மந்தநிலை, அதிக சளி", "val": "Kapha Sensitivity"}
                ],
                "te": [
                    {"title": "చలి మరియు పొడిదనం (Vata)", "subtitle": "చలిని తట్టుకోలేకపోవడం, కీళ్ల నొప్పులు, పొడి చర్మం", "val": "Vata Sensitivity"},
                    {"title": "వేడి మరియు ఎండ (Pitta)", "subtitle": "ఎండ వేడిని భరించలేకపోవడం, అధిక చెమట", "val": "Pitta Sensitivity"},
                    {"title": "తేమ మరియు చల్లని వాతావరణం (Kapha)", "subtitle": "వర్షపు కాలంలో బద్ధకం, ఎక్కువ కఫం", "val": "Kapha Sensitivity"}
                ],
                "mr": [
                    {"title": "थंडी आणि कोरडेपणा (Vata)", "subtitle": "थंडी सहन होत नाही, सांधेदुखी आणि कोरडी त्वचा", "val": "Vata Sensitivity"},
                    {"title": "उष्णता आणि ऊन (Pitta)", "subtitle": "उष्णता अजिबात सहन होत नाही, जास्त घाम", "val": "Pitta Sensitivity"},
                    {"title": "दमट आणि थंड हवामान (Kapha)", "subtitle": "थंड हवेत आळस, कफ आणि जडपणा", "val": "Kapha Sensitivity"}
                ]
            }
            return prompts.get(lang, prompts["en"]), options.get(lang, options["en"])

        # =========================================================================
        # 4. CONTEXTUAL FOLLOW-UP FOR SYMPTOM DURATION / CLINICAL SPECIFICATION
        # =========================================================================
        if section_id in ["symptom_duration", "chief_complaint", "symptom_severity"]:
            if cluster == "cardiac":
                prompts = {
                    "hi": "छाती में दर्द या भारीपन किस तरह का है? क्या यह बाएं हाथ, गर्दन में जा रहा है या सांस लेने में तकलीफ है?",
                    "en": "How does the chest pain feel? Does it radiate to your left arm or jaw, or cause breathlessness?",
                    "ta": "நெஞ்சு வலி எவ்வாறு உள்ளது? இடது கைக்கு பரவுகிறதா அல்லது மூச்சுத்திணறல் உள்ளதா?",
                    "te": "ఛాతీ నొప్పి ఎలా ఉంది? ఎడమ చేతికి పాకుతోందా లేదా శ్వాస తీసుకోవడంలో ఇబ్బంది ఉందా?",
                    "mr": "छातीतील वेदना कशी आहे? डाव्या हातात पसरते आहे का किंवा श्वास घेण्यास त्रास होतोय?"
                }
                options = {
                    "hi": [
                        {"title": "तेज जकड़न व बाएं हाथ में फैलाव [आपातकालीन]", "subtitle": "छाती पर भारी पत्थर जैसा दबाव, पसीना आना", "val": "Severe Crushing Chest Pain"},
                        {"title": "चलने या मेहनत करने पर भारीपन", "subtitle": "सीढ़ियां चढ़ने या चलने पर सांस फूलना", "val": "Exertional Angina Discomfort"},
                        {"title": "हल्की जलन या चुभन (एसिडिटी जैसी)", "subtitle": "खाने के बाद हल्की जलन, आराम करने पर सामान्य", "val": "Mild Burning Discomfort"},
                        {"title": "खांसने या हिलने पर दर्द", "subtitle": "हड्डी या मांसपेशी का खिंचाव", "val": "Musculoskeletal Chest Discomfort"}
                    ],
                    "en": [
                        {"title": "Crushing Pressure Radiating to Arm [EMERGENCY]", "subtitle": "Severe tight band around chest with sweating & nausea", "val": "Severe Crushing Chest Pain"},
                        {"title": "Heaviness on Exertion / Walking", "subtitle": "Chest tightness when walking or climbing stairs", "val": "Exertional Angina Discomfort"},
                        {"title": "Mild Burning / Acidity Discomfort", "subtitle": "Retrosternal burning after meals, relieves with rest", "val": "Mild Burning Discomfort"},
                        {"title": "Pain on Deep Breathing or Coughing", "subtitle": "Muscular or rib ache aggravated by movement", "val": "Musculoskeletal Chest Discomfort"}
                    ],
                    "ta": [
                        {"title": "கடுமையான அழுத்தம், இடது கைக்கு பரவுதல் [அவசரம்]", "subtitle": "நெஞ்சில் பாரமான அழுத்தம், அதிக வியர்வை", "val": "Severe Crushing Chest Pain"},
                        {"title": "நடக்கும்போது மூச்சுத்திணறல்", "subtitle": "மாடி ஏறும்போது அல்லது நடக்கும்போது நெஞ்சு வலி", "val": "Exertional Angina Discomfort"},
                        {"title": "லேசான நெஞ்செரிச்சல்", "subtitle": "சாப்பிட்ட பிறகு ஏற்படும் அமிலத்தன்மை", "val": "Mild Burning Discomfort"},
                        {"title": "மூச்சுவிடும்போது தசை வலி", "subtitle": "அசைவுகளின் போது ஏற்படும் வலி", "val": "Musculoskeletal Chest Discomfort"}
                    ],
                    "te": [
                        {"title": "తీవ్రమైన నొప్పి, ఎడమ చేతికి పాకడం [అత్యవసరం]", "subtitle": "ఛాతీపై తీవ్రమైన ఒత్తిడి, చెమటలు పట్టడం", "val": "Severe Crushing Chest Pain"},
                        {"title": "నడిచినప్పుడు ఛాతీ పట్టేయడం", "subtitle": "మెట్లు ఎక్కినప్పుడు లేదా నడిచినప్పుడు శ్వాసలో ఇబ్బంది", "val": "Exertional Angina Discomfort"},
                        {"title": "తేలికపాటి మంట (ఎసిడిటీ లాంటిది)", "subtitle": "తిన్న తర్వాత ఛాతీలో మంట", "val": "Mild Burning Discomfort"},
                        {"title": "ఊపిరి పీల్చినప్పుడు నొప్పి", "subtitle": "కండరాల లేదా పక్కటెముకల నొప్పి", "val": "Musculoskeletal Chest Discomfort"}
                    ],
                    "mr": [
                        {"title": "तीव्र दाब व डाव्या हातात पसरणे [तातडीचे]", "subtitle": "छातीवर जड भार, घाम येणे आणि अस्वस्थता", "val": "Severe Crushing Chest Pain"},
                        {"title": "चालताना छातीत भरून येणे", "subtitle": "जिने चढताना किंवा चालताना धाप लागणे", "val": "Exertional Angina Discomfort"},
                        {"title": "हलकी जळजळ किंवा ॲसिडिटी", "subtitle": "जेवणानंतर होणारी जळजळ", "val": "Mild Burning Discomfort"},
                        {"title": "खोकताना किंवा श्वास घेताना चमक मारणे", "subtitle": "स्नायू किंवा बरगडीतील ताण", "val": "Musculoskeletal Chest Discomfort"}
                    ]
                }
                return prompts.get(lang, prompts["en"]), options.get(lang, options["en"])

            elif cluster == "fever":
                prompts = {
                    "hi": "यह बुखार कितने दिनों से है और क्या इसके साथ ठंड, कंपकंपी या सिरदर्द भी है?",
                    "en": "How long have you had this fever, and is it accompanied by chills, shivering, or headache?",
                    "ta": "இந்த காய்ச்சல் எத்தனை நாட்களாக உள்ளது? நடுக்கம் அல்லது தலைவலியும் உள்ளதா?",
                    "te": "ఈ జ్వరం ఎన్ని రోజులుగా ఉంది? వణుకు లేదా తలనొప్పి కూడా ఉందా?",
                    "mr": "हा ताप किती दिवसांपासून आहे? थंडी वाजून ताप येतो का किंवा डोकेदुखी आहे?"
                }
                options = {
                    "hi": [
                        {"title": "तेज बुखार (>102°F) कंपकंपी के साथ", "subtitle": "अचानक तेज बुखार और ठंड लगना (1-3 दिन)", "val": "High Fever with Chills (1-3 Days)"},
                        {"title": "हल्का बुखार और बदन दर्द", "subtitle": "दिन भर हल्का हरारत व मांसपेशियों में दर्द", "val": "Mild Fever with Body Ache"},
                        {"title": "रुक-रुक कर आने वाला बुखार (1 हफ्ते से)", "subtitle": "सुबह ठीक, शाम या रात को बुखार चढ़ना", "val": "Intermittent Evening Fever"},
                        {"title": "लगातार तेज बुखार (1 हफ्ते से अधिक)", "subtitle": "दवाई के बाद भी बुखार कम न होना", "val": "Continuous Fever >1 Week"}
                    ],
                    "en": [
                        {"title": "High Fever (>102°F) with Chills", "subtitle": "Sudden onset high temperature with shivering (1-3 days)", "val": "High Fever with Chills (1-3 Days)"},
                        {"title": "Low-grade Fever with Body Ache", "subtitle": "Mild persistent warmth (99-100°F) with muscle soreness", "val": "Mild Fever with Body Ache"},
                        {"title": "Intermittent Evening Fever (1 Week)", "subtitle": "Normal in mornings, fever spikes every afternoon/evening", "val": "Intermittent Evening Fever"},
                        {"title": "Continuous High Fever (>1 Week)", "subtitle": "Sustained high pyrexia unresponsive to antipyretics", "val": "Continuous Fever >1 Week"}
                    ],
                    "ta": [
                        {"title": "அதி தீவிர காய்ச்சல் நடுக்கத்துடன்", "subtitle": "திடீர் காய்ச்சல், நடுக்கம் (1-3 நாட்கள்)", "val": "High Fever with Chills (1-3 Days)"},
                        {"title": "மிதமான காய்ச்சல் மற்றும் உடல் வலி", "subtitle": "தொடர்ச்சியான அசௌகரியம் மற்றும் வலி", "val": "Mild Fever with Body Ache"},
                        {"title": "மாலையில் மட்டும் வரும் காய்ச்சல்", "subtitle": "காலையில் இயல்பு, இரவில் காய்ச்சல் ஏறுதல்", "val": "Intermittent Evening Fever"},
                        {"title": "நீண்டகால காய்ச்சல் (1 வாரத்திற்கு மேல்)", "subtitle": "மருந்து எடுத்தும் குறையாத காய்ச்சல்", "val": "Continuous Fever >1 Week"}
                    ],
                    "te": [
                        {"title": "తీవ్రమైన జ్వరం వణుకుతో (>102°F)", "subtitle": "అకస్మాత్తుగా తీవ్ర జ్వరం, చలి (1-3 రోజులు)", "val": "High Fever with Chills (1-3 Days)"},
                        {"title": "తేలికపాటి జ్వరం మరియు ఒళ్ళు నొప్పులు", "subtitle": "రోజంతా నలత, కండరాల నొప్పులు", "val": "Mild Fever with Body Ache"},
                        {"title": "సాయంత్రం మాత్రమే వచ్చే జ్వరం", "subtitle": "ఉదయం సాధారణం, సాయంత్రం జ్వరం రావడం", "val": "Intermittent Evening Fever"},
                        {"title": "వారానికి పైగా తగ్గేని జ్వరం", "subtitle": "మందులు వేసుకున్నా తగ్గకపోవడం", "val": "Continuous Fever >1 Week"}
                    ],
                    "mr": [
                        {"title": "तीव्र ताप थंडी वाजून (>102°F)", "subtitle": "अचानक भरलेला ताप, हुडहुडी (1-3 दिवस)", "val": "High Fever with Chills (1-3 Days)"},
                        {"title": "बारीक ताप आणि अंगदुखी", "subtitle": "दिवसभर कणकण आणि स्नायूंमध्ये वेदना", "val": "Mild Fever with Body Ache"},
                        {"title": "संध्याकाळी भरून येणारा ताप", "subtitle": "सकाळी सामान्य, संध्याकाळी ताप वाढणे", "val": "Intermittent Evening Fever"},
                        {"title": "आठवड्यापेक्षा जास्त काळ सतत ताप", "subtitle": "औषध घेऊनही ताप न उतरणे", "val": "Continuous Fever >1 Week"}
                    ]
                }
                return prompts.get(lang, prompts["en"]), options.get(lang, options["en"])

            elif cluster == "cough":
                prompts = {
                    "hi": "खांसी किस तरह की है? क्या सूखी खांसी है या बलगम/कफ आ रहा है? सांस लेने में तकलीफ तो नहीं?",
                    "en": "What type of cough do you have? Is it dry or productive with phlegm, and is there any breathlessness?",
                    "ta": "இருமல் எப்படி உள்ளது? வறட்டு இருமலா அல்லது சளியுடன் வருகிறதா? மூச்சுத்திணறல் உள்ளதா?",
                    "te": "దగ్గు ఎలా ఉంది? పొడి దగ్గా లేదా కఫంతో వస్తోందా? శ్వాస తీసుకోవడంలో ఇబ్బంది ఉందా?",
                    "mr": "खोकला कसा आहे? कोरडा खोकला आहे की कफ पडतोय? श्वास घेण्यास अडचण होते का?"
                }
                options = {
                    "hi": [
                        {"title": "लगातार सूखी खांसी (Dry Cough)", "subtitle": "गले में खराश, बिना बलगम की सूखी खांसी", "val": "Dry Irritating Cough"},
                        {"title": "गाढ़ा बलगम/कफ के साथ", "subtitle": "पीला या हरा बलगम, सीने में जमाव", "val": "Productive Phlegm Cough"},
                        {"title": "सांस फूलना व सीटी की आवाज (Wheeze)", "subtitle": "सांस लेने में जोर लगना और सीने में घरघराहट", "val": "Cough with Breathlessness"},
                        {"title": "रात में या ठंड में बढ़ने वाली खांसी", "subtitle": "सोते समय या ठंडी हवा में खांसी का दौरा", "val": "Nocturnal Cold Cough"}
                    ],
                    "en": [
                        {"title": "Persistent Dry Cough", "subtitle": "Throat tickling, non-productive irritating cough", "val": "Dry Irritating Cough"},
                        {"title": "Productive Cough with Phlegm", "subtitle": "Thick yellow/green mucus, chest congestion", "val": "Productive Phlegm Cough"},
                        {"title": "Cough with Shortness of Breath", "subtitle": "Wheezing, chest tightness, struggle to breathe", "val": "Cough with Breathlessness"},
                        {"title": "Night-time / Cold-induced Cough", "subtitle": "Worse when lying down or in air conditioning", "val": "Nocturnal Cold Cough"}
                    ],
                    "ta": [
                        {"title": "வறட்டு இருமல்", "subtitle": "தொண்டை வறட்சி, சளி இல்லாமல் வரும் இருமல்", "val": "Dry Irritating Cough"},
                        {"title": "சளியுடன் கூடிய இருமல்", "subtitle": "மஞ்சள் அல்லது பச்சை நிற சளி வருதல்", "val": "Productive Phlegm Cough"},
                        {"title": "மூச்சுத்திணறலுடன் இருமல்", "subtitle": "மூச்சு வாங்கும்போது விசில் போன்ற சத்தம்", "val": "Cough with Breathlessness"},
                        {"title": "இரவில் அதிகமாகும் இருமல்", "subtitle": "படுக்கும்போது அல்லது குளிர் காற்றில் அதிகரித்தல்", "val": "Nocturnal Cold Cough"}
                    ],
                    "te": [
                        {"title": "పొడి దగ్గు", "subtitle": "గొంతులో గరగర, కఫం లేని దగ్గు", "val": "Dry Irritating Cough"},
                        {"title": "కఫంతో కూడిన దగ్గు", "subtitle": "చిక్కని తెమడ, ఛాతీలో పట్టేయడం", "val": "Productive Phlegm Cough"},
                        {"title": "శ్వాసలో ఇబ్బందితో దగ్గు", "subtitle": "ఆయాసం, శ్వాస తీసుకున్నప్పుడు ఈల లాంటి శబ్దం", "val": "Cough with Breathlessness"},
                        {"title": "రాత్రి పూట ఎక్కువయ్యే దగ్గు", "subtitle": "పడుకున్నప్పుడు లేదా చలిగాలికి ఎక్కువ కావడం", "val": "Nocturnal Cold Cough"}
                    ],
                    "mr": [
                        {"title": "कोरडा खोकला", "subtitle": "घशात खवखव, कफ न पडणारा खोकला", "val": "Dry Irritating Cough"},
                        {"title": "कफयुक्त खोकला", "subtitle": "पिवळसर-हिरवा कफ, छातीत भरल्यासारखे वाटणे", "val": "Productive Phlegm Cough"},
                        {"title": "धाप लागणे आणि घरघर", "subtitle": "श्वास घेताना त्रास आणि शिटीसारखा आवाज", "val": "Cough with Breathlessness"},
                        {"title": "रात्री किंवा थंडीत वाढणारा खोकला", "subtitle": "झोपल्यावर किंवा थंड हवेत खोकल्याची उबळ", "val": "Nocturnal Cold Cough"}
                    ]
                }
                return prompts.get(lang, prompts["en"]), options.get(lang, options["en"])

            elif cluster == "abdominal":
                prompts = {
                    "hi": "पेट में दर्द किस जगह है और क्या उल्टी, एसिडिटी या दस्त की शिकायत भी है?",
                    "en": "Where is the stomach pain located, and do you also have nausea, acidity, or loose motions?",
                    "ta": "வயிற்று வலி எங்குள்ளது? வாந்தி, நெஞ்செரிச்சல் அல்லது வயிற்றுப்போக்கு உள்ளதா?",
                    "te": "కడుపు నొప్పి ఎక్కడ ఉంది? వాంతులు, ఎసిడిటీ లేదా విరేచనాలు ఉన్నాయా?",
                    "mr": "पोटात दुखणे कोणत्या भागात आहे? उलट्या, ॲसिडिटी किंवा जुलाबाचा त्रास आहे का?"
                }
                options = {
                    "hi": [
                        {"title": "ऊपरी पेट में तेज जलन और गैस", "subtitle": "सीने के ठीक नीचे जलन, खट्टी डकारें", "val": "Upper Abdominal Acidity"},
                        {"title": "पेट में तेज मरोड़ (Cramping)", "subtitle": "नाभि के पास या नीचे रुक-रुक कर ऐंठन", "val": "Abdominal Cramping"},
                        {"title": "उल्टी और पतले दस्त के साथ", "subtitle": "दिन में कई बार दस्त, कमजोरी व चक्कर", "val": "Vomiting and Diarrhea"},
                        {"title": "कब्ज और भारीपन (पेट साफ न होना)", "subtitle": "कई दिनों से शौच न होना, पेट फूला हुआ", "val": "Constipation and Bloating"}
                    ],
                    "en": [
                        {"title": "Upper Stomach Burning & Acidity", "subtitle": "Heartburn, acid reflux, gnawing pain after meals", "val": "Upper Abdominal Acidity"},
                        {"title": "Severe Cramping Spasms", "subtitle": "Colicky abdominal pain coming in waves", "val": "Abdominal Cramping"},
                        {"title": "Nausea, Vomiting & Loose Stools", "subtitle": "Food poisoning / gastroenteritis symptoms", "val": "Vomiting and Diarrhea"},
                        {"title": "Severe Constipation & Bloating", "subtitle": "No bowel movement for multiple days, distension", "val": "Constipation and Bloating"}
                    ],
                    "ta": [
                        {"title": "மேல் வயிற்றில் எரியும் வலி & வாயு", "subtitle": "நெஞ்செரிச்சல், சாப்பிட்ட பின் அமிலத்தன்மை", "val": "Upper Abdominal Acidity"},
                        {"title": "வயிற்றில் பிடிப்பு வலி (Cramps)", "subtitle": "விட்டு விட்டு வரும் கடும் வயிற்றுப் பிடிப்பு", "val": "Abdominal Cramping"},
                        {"title": "வாந்தி மற்றும் வயிற்றுப்போக்கு", "subtitle": "நீரிழப்பு மற்றும் உடல் சோர்வு", "val": "Vomiting and Diarrhea"},
                        {"title": "மலச்சிக்கல் மற்றும் உப்புசம்", "subtitle": "பல நாட்களாக மலம் கழிக்க இயலாமை", "val": "Constipation and Bloating"}
                    ],
                    "te": [
                        {"title": "పై కడుపులో తీవ్రమైన మంట & గ్యాస్", "subtitle": "ఛాతీ కింద మంట, పుల్లని తేన్పులు", "val": "Upper Abdominal Acidity"},
                        {"title": "కడుపులో తిప్పడం & నొప్పి (Cramps)", "subtitle": "కడుపు పట్టేసినట్లు మెలిపెట్టే నొప్పి", "val": "Abdominal Cramping"},
                        {"title": "వాంతులు మరియు విరేచనాలు", "subtitle": "అతిసారం, నీరసం మరియు కళ్లు తిరగడం", "val": "Vomiting and Diarrhea"},
                        {"title": "మలబద్ధకం మరియు కడుపు ఉబ్బరం", "subtitle": "కొన్ని రోజులుగా విసర్జన సాఫీగా లేకపోవడం", "val": "Constipation and Bloating"}
                    ],
                    "mr": [
                        {"title": "वरच्या पोटात जळजळ आणि गॅस", "subtitle": "छातीखाली जळजळ, आंबट ढेकर", "val": "Upper Abdominal Acidity"},
                        {"title": "पोटात पिळवटून दुखणे (Cramps)", "subtitle": "थांबून थांबून पोटात येणाऱ्या कळा", "val": "Abdominal Cramping"},
                        {"title": "उलट्या आणि पातळ जुलाब", "subtitle": "वारंवार जुलाब, अशक्तपणा आणि चक्कर", "val": "Vomiting and Diarrhea"},
                        {"title": "बद्धकोष्ठता आणि पोट फुगणे", "subtitle": "काही दिवसांपासून शौचास साफ न होणे", "val": "Constipation and Bloating"}
                    ]
                }
                return prompts.get(lang, prompts["en"]), options.get(lang, options["en"])

            elif cluster == "joint":
                prompts = {
                    "hi": "दर्द किन जोड़ों में है और क्या सुबह सोकर उठने पर जोड़ों में जकड़न (Stiffness) रहती है?",
                    "en": "Which joints are painful, and do you experience morning stiffness or swelling in the joints?",
                    "ta": "எந்த மூட்டுகளில் வலி உள்ளது? காலையில் எழுந்தவுடன் மூட்டுகளில் விறைப்பு உள்ளதா?",
                    "te": "ఏ కీళ్లలో నొప్పి ఉంది? ఉదయం లేవగానే కీళ్లలో బిగుతుదనం లేదా వాపు ఉందా?",
                    "mr": "कोणत्या सांध्यांमध्ये वेदना आहेत आणि सकाळी उठल्यावर सांधे आखडतात का?"
                }
                options = {
                    "hi": [
                        {"title": "घुटनों में दर्द और चलने में परेशानी", "subtitle": "सीढ़ियां चढ़ने व बैठने-उठने में कटकट की आवाज", "val": "Knee Joint Pain"},
                        {"title": "कमर और रीढ़ में जकड़न (Lower Back)", "subtitle": "झुकने में असमर्थ, सुबह कमर में अकड़न", "val": "Lower Back Stiffness"},
                        {"title": "हाथ-पैर के छोटे जोड़ों में सूजन", "subtitle": "सुबह 30 मिनट से अधिक जकड़न (संधिवाता)", "val": "Small Joint Swelling"},
                        {"title": "गर्दन और कंधे में दर्द", "subtitle": "सिर घुमाने में परेशानी, सर्वाइकल खिंचाव", "val": "Neck and Shoulder Pain"}
                    ],
                    "en": [
                        {"title": "Knee Joint Pain & Difficulty Walking", "subtitle": "Creaking sound, worse on climbing stairs", "val": "Knee Joint Pain"},
                        {"title": "Lower Back Pain & Spine Stiffness", "subtitle": "Difficulty bending, severe morning back tightness", "val": "Lower Back Stiffness"},
                        {"title": "Small Joint Swelling (Hands & Feet)", "subtitle": "Morning stiffness lasting >30 mins (Arthritis pattern)", "val": "Small Joint Swelling"},
                        {"title": "Neck & Shoulder Radiating Ache", "subtitle": "Restricted neck movement, cervical strain", "val": "Neck and Shoulder Pain"}
                    ],
                    "ta": [
                        {"title": "முழங்கால் வலி & நடக்க சிரமம்", "subtitle": "மாடி ஏறும்போது வலி, சத்தம் வருதல்", "val": "Knee Joint Pain"},
                        {"title": "இடுப்பு மற்றும் முதுகுத்தண்டு விறைப்பு", "subtitle": "குனிய இயலாமை, காலையில் அதிக வலி", "val": "Lower Back Stiffness"},
                        {"title": "கை, கால் மூட்டுகளில் வீக்கம்", "subtitle": "காலையில் 30 நிமிடங்களுக்கு மேல் விறைப்பு", "val": "Small Joint Swelling"},
                        {"title": "கழுத்து மற்றும் தோள்பட்டை வலி", "subtitle": "கழுத்தை திருப்ப முடியாமை", "val": "Neck and Shoulder Pain"}
                    ],
                    "te": [
                        {"title": "మోకాళ్ల నొప్పులు & నడవడం కష్టం", "subtitle": "మెట్లు ఎక్కేటప్పుడు శబ్దాలు రావడం, తీవ్రమైన నొప్పి", "val": "Knee Joint Pain"},
                        {"title": "నడుము మరియు వెన్నెముక బిగుతుదనం", "subtitle": "వంగడం కష్టం, ఉదయం నడుము పట్టేయడం", "val": "Lower Back Stiffness"},
                        {"title": "చేతులు, కాళ్ల కీళ్లలో వాపులు", "subtitle": "ఉదయం 30 నిమిషాలకు పైగా కీళ్లు బిగుసుకోవడం", "val": "Small Joint Swelling"},
                        {"title": "మెడ మరియు భుజం నొప్పి", "subtitle": "మెడ తిప్పడం కష్టం, నరం పట్టేయడం", "val": "Neck and Shoulder Pain"}
                    ],
                    "mr": [
                        {"title": "गुडघेदुखी आणि चालण्यास त्रास", "subtitle": "जिने चढताना किंवा खाली बसताना आवाज येणे", "val": "Knee Joint Pain"},
                        {"title": "कंबरदुखी आणि पाठीचा कडकपणा", "subtitle": "वाकण्यास त्रास, सकाळी पाठ आखडणे", "val": "Lower Back Stiffness"},
                        {"title": "हात-पायांच्या बोटांमध्ये सूज व वेदना", "subtitle": "सकाळी 30 मिनिटांपेक्षा जास्त वेळ सांधे आखडणे", "val": "Small Joint Swelling"},
                        {"title": "मान आणि खांदेदुखी", "subtitle": "मान हलवण्यास अडचण, स्पॉन्डिलायटिसचा ताण", "val": "Neck and Shoulder Pain"}
                    ]
                }
                return prompts.get(lang, prompts["en"]), options.get(lang, options["en"])

            elif cluster == "headache":
                prompts = {
                    "hi": "सिरदर्द किस तरह का है? क्या आधे सिर में धड़कन जैसा दर्द है, चक्कर या आंखों के आगे अंधेरा आ रहा है?",
                    "en": "What type of headache is it? Is it one-sided throbbing, or with dizziness and visual changes?",
                    "ta": "தலைவலி எப்படி உள்ளது? ஒரு பக்கத்தில் துடிக்கும் வலியா, அல்லது தலைசுற்றல் உள்ளதா?",
                    "te": "తలనొప్పి ఎలా ఉంది? ఒకవైపు విపరీతమైన నొప్పా, లేదా తలతిరగడం ఉందా?",
                    "mr": "डोकेदुखी कशी आहे? अर्ध्या डोक्यात ठणकणारी वेदना आहे का किंवा चक्कर येतेय?"
                }
                options = {
                    "hi": [
                        {"title": "आधे सिर में तेज धड़कन (Migraine)", "subtitle": "रोशनी या आवाज से चिढ़, उल्टी का मन", "val": "Migraine Throbbing Headache"},
                        {"title": "माथे और दोनों तरफ दबाव (Tension)", "subtitle": "सिर पर पट्टी जैसा भारी दबाव, तनाव के कारण", "val": "Tension Band Headache"},
                        {"title": "सिर के पीछे व गर्दन में दर्द (BP Check)", "subtitle": "गर्दन की नसों में खिंचाव, भारीपन", "val": "Occipital Neck Headache"},
                        {"title": "चक्कर और आंखों के आगे अंधेरा", "subtitle": "खड़े होने पर संतुलन बिगड़ना, कमजोरी", "val": "Headache with Dizziness"}
                    ],
                    "en": [
                        {"title": "One-sided Throbbing Ache (Migraine)", "subtitle": "Pulsating pain, light/sound sensitivity, nausea", "val": "Migraine Throbbing Headache"},
                        {"title": "Forehead Band Tightness (Tension)", "subtitle": "Constant dull ache pressing across both temples", "val": "Tension Band Headache"},
                        {"title": "Back of Head & Neck Stiffness", "subtitle": "Tight occipital ache, recommended blood pressure check", "val": "Occipital Neck Headache"},
                        {"title": "Headache with Severe Dizziness", "subtitle": "Spinning sensation (vertigo) and visual blurriness", "val": "Headache with Dizziness"}
                    ],
                    "ta": [
                        {"title": "ஒரு பக்க தலைவலி (Migraine)", "subtitle": "வெளிச்சம் பார்த்தால் வலி, வாந்தி உணர்வு", "val": "Migraine Throbbing Headache"},
                        {"title": "நெற்றி மற்றும் இருபுறமும் அழுத்தம்", "subtitle": "விடாத மந்தமான வலி, மன அழுத்தம்", "val": "Tension Band Headache"},
                        {"title": "தலையின் பின்பகுதி மற்றும் கழுத்து வலி", "subtitle": "இரத்த அழுத்தம் பரிசோதிக்க பரிந்துரை", "val": "Occipital Neck Headache"},
                        {"title": "தலைச்சுற்றலுடன் தலைவலி", "subtitle": "நிலைகொள்ளாமை, கண்கள் இருண்டு போதல்", "val": "Headache with Dizziness"}
                    ],
                    "te": [
                        {"title": "ఒకవైపు తీవ్రమైన తలనొప్పి (మైగ్రేన్)", "subtitle": "వెలుతురు చూస్తే నొప్పి, వాంతి వచ్చినట్లు ఉండటం", "val": "Migraine Throbbing Headache"},
                        {"title": "నుదుటిపై ఒత్తిడి (టెన్షన్ తలనొప్పి)", "subtitle": "తలకు పట్టీ వేసినట్లు బిగుతుగా ఉండటం", "val": "Tension Band Headache"},
                        {"title": "తల వెనుక భాగం & మెడ నొప్పి", "subtitle": "మెడ నరాలు పట్టేయడం, BP తనిఖీ అవసరం", "val": "Occipital Neck Headache"},
                        {"title": "తలతిరగడం మరియు కళ్లు తిరగడం", "subtitle": "నిలబడలేకపోవడం, బలహీనత", "val": "Headache with Dizziness"}
                    ],
                    "mr": [
                        {"title": "अर्धशिशी - एका बाजूला ठणक (Migraine)", "subtitle": "प्रकाशाचा त्रास, मळमळ आणि ठणक", "val": "Migraine Throbbing Headache"},
                        {"title": "कपाळावर पट्टा बांधल्यासारखा दाब (Tension)", "subtitle": "सतत जाणवणारी जड डोकेदुखी", "val": "Tension Band Headache"},
                        {"title": "डोक्याच्या मागच्या भागात व मानेत वेदना", "subtitle": "रक्तदाब (BP) तपासण्याची गरज", "val": "Occipital Neck Headache"},
                        {"title": "डोकेदुखीसोबत चक्कर व अंधारी", "subtitle": "उभे राहिल्यावर तोल जाणे, अशक्तपणा", "val": "Headache with Dizziness"}
                    ]
                }
                return prompts.get(lang, prompts["en"]), options.get(lang, options["en"])

        # =========================================================================
        # 5. DEFAULT DURATION / SEVERITY (General Fallback with localized choices)
        # =========================================================================
        if section_id == "symptom_severity":
            prompts = {
                "hi": "1 से 10 के पैमाने पर तकलीफ या दर्द कितना तेज है?",
                "en": "On a scale of 1 to 10, how severe is your discomfort or pain?",
                "ta": "1 முதல் 10 வரை வலி அல்லது அசௌகரியம் எவ்வளவு கடுமையானது?",
                "te": "1 నుండి 10 వరకు నొప్పి లేదా ఇబ్బంది ఎంత తీవ్రంగా ఉంది?",
                "mr": "1 ते 10 च्या प्रमाणात वेदना किंवा त्रास किती तीव्र आहे?"
            }
            options = {
                "hi": [
                    {"title": "1 - 3 : हल्का दर्द", "subtitle": "सामान्य दिनचर्या में कोई रुकावट नहीं", "val": "1-3 Mild"},
                    {"title": "4 - 6 : मध्यम दर्द", "subtitle": "दैनिक कार्यों में परेशानी हो रही है", "val": "4-6 Moderate"},
                    {"title": "7 - 10 : तेज / असहनीय दर्द", "subtitle": "असहनीय दर्द, तुरंत डॉक्टर को दिखाना जरूरी", "val": "7-10 Severe"}
                ],
                "en": [
                    {"title": "1 - 3 : Mild Discomfort", "subtitle": "Noticeable but able to carry on regular activities", "val": "1-3 Mild"},
                    {"title": "4 - 6 : Moderate Pain", "subtitle": "Significant discomfort interfering with routine work", "val": "4-6 Moderate"},
                    {"title": "7 - 10 : Severe / Unbearable Pain", "subtitle": "Intense pain requiring immediate clinical evaluation", "val": "7-10 Severe"}
                ],
                "ta": [
                    {"title": "1 - 3 : லேசான வலி", "subtitle": "வழக்கமான வேலைகளில் பெரிய பாதிப்பு இல்லை", "val": "1-3 Mild"},
                    {"title": "4 - 6 : மிதமான வலி", "subtitle": "தினசரி பணிகளில் குறிப்பிடத்தக்க அசௌகரியம்", "val": "4-6 Moderate"},
                    {"title": "7 - 10 : கடுமையான வலி", "subtitle": "தாங்க முடியாத வலி, உடனடி சிகிச்சை தேவை", "val": "7-10 Severe"}
                ],
                "te": [
                    {"title": "1 - 3 : తేలికపాటి నొప్పి", "subtitle": "సాధారణ పనులకు పెద్దగా అంతరాయం కలగదు", "val": "1-3 Mild"},
                    {"title": "4 - 6 : మోస్తరు నొప్పి", "subtitle": "రోజువారీ పనులకు ఇబ్బందిగా ఉంది", "val": "4-6 Moderate"},
                    {"title": "7 - 10 : తీవ్రమైన నొప్పి", "subtitle": "భరించలేని నొప్పి, వెంటనే డాక్టరును సంప్రదించాలి", "val": "7-10 Severe"}
                ],
                "mr": [
                    {"title": "1 - 3 : सौम्य वेदना", "subtitle": "दैनंदिन कामात फारसा अडथळा नाही", "val": "1-3 Mild"},
                    {"title": "4 - 6 : मध्यम वेदना", "subtitle": "रोजच्या कामांमध्ये लक्षणीय त्रास होतो", "val": "4-6 Moderate"},
                    {"title": "7 - 10 : तीव्र असह्य वेदना", "subtitle": "असहनीय त्रास, तातडीने तपासणी आवश्यक", "val": "7-10 Severe"}
                ]
            }
            return prompts.get(lang, prompts["en"]), options.get(lang, options["en"])

        # Default Duration
        duration_prompts = {
            "hi": "यह समस्या कब से है? कितने दिन, हफ्ते, या महीने?",
            "en": "How long have you had this problem? Days, weeks, or months?",
            "ta": "இந்தப் பிரச்சனை எவ்வளவு காலமாக உள்ளது?",
            "te": "ఈ సమస్య ఎంతకాలంగా ఉంది?",
            "mr": "ही समस्या किती दिवसांपासून आहे?"
        }
        duration_options = {
            "hi": [
                {"title": "1 - 2 दिन (हाल ही में)", "subtitle": "कल या आज से शुरू हुआ", "val": "1-2 Days"},
                {"title": "3 - 7 दिन (लगभग 1 हफ्ता)", "subtitle": "पिछले कुछ दिनों से बना हुआ है", "val": "3-7 Days"},
                {"title": "2 - 4 हफ्ते", "subtitle": "कई हफ्तों से लगातार परेशानी", "val": "2-4 Weeks"},
                {"title": "1 महीने से अधिक", "subtitle": "लंबे समय से चली आ रही पुरानी बीमारी", "val": "Over 1 Month"}
            ],
            "en": [
                {"title": "1 - 2 Days (Recent onset)", "subtitle": "Started today or yesterday", "val": "1-2 Days"},
                {"title": "3 - 7 Days (~1 Week)", "subtitle": "Ongoing for nearly a week", "val": "3-7 Days"},
                {"title": "2 - 4 Weeks", "subtitle": "Persistent for a few weeks", "val": "2-4 Weeks"},
                {"title": "Over 1 Month", "subtitle": "Long-standing chronic issue", "val": "Over 1 Month"}
            ],
            "ta": [
                {"title": "1 - 2 நாட்கள்", "subtitle": "நேற்று அல்லது இன்று தொடங்கியது", "val": "1-2 Days"},
                {"title": "3 - 7 நாட்கள்", "subtitle": "சுமார் ஒரு வாரமாக உள்ளது", "val": "3-7 Days"},
                {"title": "2 - 4 வாரங்கள்", "subtitle": "பல வாரங்களாகத் தொடர்கிறது", "val": "2-4 Weeks"},
                {"title": "1 மாதத்திற்கும் மேல்", "subtitle": "நீண்டகால நாள்பட்ட பிரச்சனை", "val": "Over 1 Month"}
            ],
            "te": [
                {"title": "1 - 2 రోజులు", "subtitle": "నిన్న లేదా ఈరోజు ప్రారంభమైంది", "val": "1-2 Days"},
                {"title": "3 - 7 రోజులు", "subtitle": "సుమారు ఒక వారం నుండి ఉంది", "val": "3-7 Days"},
                {"title": "2 - 4 వారాలు", "subtitle": "కొన్ని వారాలుగా కొనసాగుతోంది", "val": "2-4 Weeks"},
                {"title": "1 నెలకు పైగా", "subtitle": "చాలా కాలంగా ఉన్న దీర్ఘకాలిక సమస్య", "val": "Over 1 Month"}
            ],
            "mr": [
                {"title": "1 - 2 दिवस", "subtitle": "काल किंवा आजपासून सुरू झाले", "val": "1-2 Days"},
                {"title": "3 - 7 दिवस", "subtitle": "सुमारे एका आठवड्यापासून त्रास", "val": "3-7 Days"},
                {"title": "2 - 4 आठवडे", "subtitle": "काही आठवड्यांपासून सुरू आहे", "val": "2-4 Weeks"},
                {"title": "1 महिन्यापेक्षा जास्त", "subtitle": "दीर्घकालीन जुनाट आजार", "val": "Over 1 Month"}
            ]
        }
        return duration_prompts.get(lang, duration_prompts["en"]), duration_options.get(lang, duration_options["en"])

    def get_current_question(self) -> Optional[dict]:
        """Get the current question to ask the patient with context-based formulation and options."""
        if self.is_completed or self.current_section_idx >= len(self.section_sequence):
            self.is_completed = True
            return None

        section_id = self.section_sequence[self.current_section_idx]
        section = SECTIONS_BY_ID.get(section_id)
        if not section:
            self.is_completed = True
            return None

        # Dynamically get context-formulated question text and suggested multi-choice options
        prompt, suggested_options = self._get_contextual_question_and_options(section_id)

        # If it's a static section prompt with no specific override
        if not prompt:
            prompt = section["prompts"].get(self.language, section["prompts"].get("en", ""))

        return {
            "section_id": section["id"],
            "section_order": section["order"],
            "question_text": prompt,
            "fact_category": section["fact_category"],
            "is_follow_up": self.follow_up_count > 0,
            "suggested_options": suggested_options
        }

    def process_response(self, transcript: str) -> dict:
        """
        Process a patient's response and extract clinical facts.

        Args:
            transcript: Transcribed text of patient's speech

        Returns:
            Dict with extracted facts, next question info, and completion status.
        """
        if self.is_completed or self.current_section_idx >= len(self.section_sequence):
            return {
                "extracted_facts": [],
                "next_question": None,
                "is_completed": True
            }

        section_id = self.section_sequence[self.current_section_idx]
        section = SECTIONS_BY_ID[section_id]

        if section_id == "chief_complaint":
            self._check_ayush_context(transcript)

        # Normalize the response through NegEx + Embeddings
        match = self._normalizer.normalize(transcript, self.language)

        extracted_facts = []

        # Check for AYUSH concepts first with NAMASTE codes
        t_low = transcript.lower()
        ayush_concept = None
        ayush_code = None

        if section_id == "ayush_agni":
            if any(k in t_low for k in ["sama", "balanced", "सम", "संतुलित", "सामान्य", "சம", "సమ"]):
                ayush_concept = "Sama Agni (Balanced Digestion)"
                ayush_code = "NAMASTE:AGNI-SAMA-001"
            elif any(k in t_low for k in ["vishama", "variable", "gas", "bloat", "विषम", "अनियमित", "गैस", "விஷம", "విషమ"]):
                ayush_concept = "Vishama Agni (Irregular/Vata Digestion)"
                ayush_code = "NAMASTE:AGNI-VISHAMA-001"
            elif any(k in t_low for k in ["tikshna", "sharp", "burn", "acid", "तीक्ष्ण", "तेज", "जलन", "एसिडिटी", "தீக்ஷ்ண", "தீவிர", "తీక్షణ", "మంట"]):
                ayush_concept = "Tikshna Agni (Hyperactive/Pitta Digestion)"
                ayush_code = "NAMASTE:AGNI-TIKSHNA-001"
            elif any(k in t_low for k in ["manda", "sluggish", "heavy", "मंद", "भारी", "மந்த", "பாரம்", "మంద", "భారం"]):
                ayush_concept = "Manda Agni (Sluggish/Kapha Digestion)"
                ayush_code = "NAMASTE:AGNI-MANDA-001"

        elif section_id == "ayush_koshtha":
            if any(k in t_low for k in ["madhyama", "regular", "मध्यम", "नियमित", "சீரான", "மத்யம", "సాధారణ", "మధ్యమ"]):
                ayush_concept = "Madhyama Koshtha (Regular Bowel)"
                ayush_code = "NAMASTE:KOSHTHA-MADHYAMA-001"
            elif any(k in t_low for k in ["krura", "constipat", "hard", "कब्ज", "क्रूर", "कड़ा", "மலச்சிக்கல்", "க்ரூர", "మలబద్ధకం", "క్రూర", "बद्धकोष्ठता"]):
                ayush_concept = "Krura Koshtha (Hard/Constipated Bowel)"
                ayush_code = "NAMASTE:KOSHTHA-KRURA-001"
            elif any(k in t_low for k in ["mridu", "loose", "soft", "मृदु", "ढीला", "पतला", "மிருது", "தளர்வான", "మృదు", "వదులుగా", "पातळ"]):
                ayush_concept = "Mridu Koshtha (Loose/Frequent Bowel)"
                ayush_code = "NAMASTE:KOSHTHA-MRIDU-001"

        elif section_id == "ayush_prakriti":
            if any(k in t_low for k in ["cold", "vata", "dry", "ठंड", "वात", "रूखी", "कोरडी", "குளிர்", "வாதம்", "வறண்ட", "చలి", "వాతం", "పొడి"]):
                ayush_concept = "Vata Prakriti Sensitivity (Cold/Dry)"
                ayush_code = "NAMASTE:DOSHA-VATA-001"
            elif any(k in t_low for k in ["heat", "pitta", "warm", "गर्मी", "पित्त", "गर्म", "வெப்பம்", "பித்தம்", "వేడి", "పిత్తం", "उष्णता"]):
                ayush_concept = "Pitta Prakriti Sensitivity (Heat/Warm)"
                ayush_code = "NAMASTE:DOSHA-PITTA-001"
            elif any(k in t_low for k in ["damp", "kapha", "oily", "नमी", "कफ", "चिकनी", "तेलकट", "ஈரப்பதம்", "கபம்", "తేమ", "కఫం", "दमट"]):
                ayush_concept = "Kapha Prakriti Sensitivity (Damp/Cool)"
                ayush_code = "NAMASTE:DOSHA-KAPHA-001"

        if ayush_concept and ayush_code:
            extracted_facts.append({
                "category": section["fact_category"],
                "field": section.get("fact_field", section["id"]),
                "value": transcript,
                "is_negated": False,
                "confidence": 0.95,
                "provenance": "NAMASTE_RULE_MATCH",
                "concept": ayush_concept,
                "concept_code": ayush_code
            })
        elif match.is_negated:
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

        # Advance to next clinical section on every turn
        self.current_section_idx += 1
        self.follow_up_count = 0

        # Get next question
        next_question = self.get_current_question()
        suggested_opts = next_question.get("suggested_options", []) if next_question else []

        return {
            "extracted_facts": extracted_facts,
            "next_question": next_question,
            "suggested_options": suggested_opts,
            "is_completed": self.is_completed,
            "total_facts_captured": len(self.captured_facts)
        }

    def get_summary(self) -> dict:
        """Generate a summary of all captured facts for explain-back."""
        return {
            "total_facts": len(self.captured_facts),
            "sections_completed": self.current_section_idx,
            "total_sections": len(self.section_sequence),
            "facts": self.captured_facts,
            "is_completed": self.is_completed
        }

    def get_opening_prompt(self) -> str:
        """Get the very first opening prompt for the conversation."""
        openings = {
            "hi": "नमस्ते, मैं अखिल भारतीय आयुर्वेद संस्थान का डिजिटल सहायक हूँ। आपको क्या परेशानी है?",
            "en": "Hello, I am the digital assistant of the All India Institute of Ayurveda. What is your main concern today?",
            "ta": "வணக்கம், நான் அகில இந்திய ஆயுர்வேத நிறுவனத்தின் டிஜிட்டல் உதவியாளர். உங்கள் முக்கிய பிரச்சனை என்ன?",
            "te": "నమస్కారం, నేను అఖిల భారత ఆయుర్వేద సంస్థ డిజిటల్ సహాయకుడిని. మీ ప్రధాన సమస్య ఏమిటి?",
            "mr": "नमस्कार, मी अखिल भारतीय आयुर्वेद संस्थेचा डिजिटल सहाय्यक आहे. तुमची मुख्य समस्या काय आहे?"
        }
        return openings.get(self.language, openings["hi"])
