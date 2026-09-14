import '../models/encounter.dart';
import '../models/clinical_fact.dart';
import '../models/call_session.dart';
import '../models/document_result.dart';
import '../models/queue_status.dart';
import '../models/ayush_profile.dart';

/// 100% Offline Deterministic Mock Data Provider for MediKiosk
/// Guarantees that all 24 screens can navigate cleanly without network
/// Ref: MEDIKIOSK_DEVELOPMENT_FLOW_MASTER.md Phase 3
class MockDataSource {
  static EncounterBootstrapResponse getMockBootstrap({String language = 'hi'}) {
    return const EncounterBootstrapResponse(
      encounterId: 'enc-mock-001',
      patientId: 'pat-mock-001',
      tokenNumber: 'A-104',
      status: 'BOOTSTRAPPED',
      supportedLanguages: kSupportedLanguages,
    );
  }

  static CallSessionStartResponse getMockCallStart({String language = 'hi'}) {
    final Map<String, String> openings = {
      'hi': 'नमस्ते, मैं मेडीकिओस्क हूँ। आज आपको क्या परेशानी महसूस हो रही है?',
      'en': 'Hello, I am MediKiosk. What symptoms are you experiencing today?',
      'ta': 'வணக்கம், நான் மெடிகியோஸ்க். இன்று உங்களுக்கு என்ன பிரச்சனை?',
      'te': 'నమస్కారం, నేను మెడికియోస్క్. ఈరోజు మీకు ఎలాంటి సమస్య ఉంది?',
      'mr': 'नमस्कार, मी मेडीकिओस्क आहे. आज तुम्हाला काय त्रास होत आहे?',
    };

    return CallSessionStartResponse(
      sessionId: 'call-sess-mock-001',
      status: 'CALL_ACTIVE',
      openingText: openings[language] ?? openings['en']!,
      openingAudioBase64: null,
    );
  }

  static AudioTurnResponse getMockAudioTurn({
    required int turnIndex,
    String? patientWords,
    String language = 'hi',
  }) {
    final Map<String, String> q1 = {
      'hi': 'क्या आपको सिरदर्द के साथ चक्कर या उल्टी जैसा भी लग रहा है?',
      'en': 'Do you also have dizziness or nausea along with your headache?',
      'ta': 'தலைவலியுடன் தலைச்சுற்றல் அல்லது வாந்தி போன்ற உணர்வு உள்ளதா?',
      'te': 'తలనొప్పితో పాటు తలతిరగడం లేదా వాంతి వచ్చినట్లు అనిపిస్తుందా?',
      'mr': 'डोकेदुखीसोबत चक्कर किंवा मळमळ जाणवत आहे का?',
    };
    final Map<String, String> q2 = {
      'hi': 'क्या आप पहले से कोई नियमित दवा ले रहे हैं?',
      'en': 'Are you currently taking any regular medications?',
      'ta': 'நீங்கள் தொடர்ந்து ஏதேனும் மருந்துகளை உட்கொள்கிறீர்களா?',
      'te': 'మీరు క్రమం తప్పకుండా ఏవైనా మందులు వాడుతున్నారా?',
      'mr': 'तुम्ही आधीपासून कोणती नियमित औषधे घेत आहात का?',
    };
    final Map<String, String> defaultTranscript1 = {
      'hi': 'मुझे दो दिन से तेज सिरदर्द और हल्का बुखार है',
      'en': 'I have had a severe headache and mild fever for two days',
      'ta': 'எனக்கு இரண்டு நாட்களாக கடுமையான தலைவலி மற்றும் லேசான காய்ச்சல் உள்ளது',
      'te': 'నాకు రెండు రోజులుగా తీవ్రమైన తలనొప్పి మరియు తేలికపాటి జ్వరం ఉంది',
      'mr': 'मला दोन दिवसांपासून तीव्र डोकेदुखी आणि हलका ताप आहे',
    };
    final Map<String, String> defaultTranscript2 = {
      'hi': 'नहीं, कोई चक्कर नहीं आ रहा है',
      'en': 'No, I do not have any dizziness',
      'ta': 'இல்லை, தலைச்சுற்றல் எதுவும் இல்லை',
      'te': 'లేదు, ఎలాంటి తలతిరగడం లేదు',
      'mr': 'नाही, कोणतीही चक्कर येत नाही आहे',
    };
    final Map<String, String> headacheConcept = {
      'hi': 'तीव्र सिरदर्द (Severe Headache)',
      'en': 'Severe Headache',
      'ta': 'கடுமையான தலைவலி (Severe Headache)',
      'te': 'తీవ్రమైన తలనొప్పి (Severe Headache)',
      'mr': 'तीव्र डोकेदुखी (Severe Headache)',
    };
    final Map<String, String> feverConcept = {
      'hi': 'हल्का बुखार (Mild Pyrexia)',
      'en': 'Mild Pyrexia',
      'ta': 'லேசான காய்ச்சல் (Mild Pyrexia)',
      'te': 'తేలికపాటి జ్వరం (Mild Pyrexia)',
      'mr': 'हलका ताप (Mild Pyrexia)',
    };
    final Map<String, String> dizzinessDeniedConcept = {
      'hi': 'चक्कर नहीं (Dizziness Denied)',
      'en': 'Dizziness Denied',
      'ta': 'தலைச்சுற்றல் இல்லை (Dizziness Denied)',
      'te': 'తలతిరగడం లేదు (Dizziness Denied)',
      'mr': 'चक्कर नाही (Dizziness Denied)',
    };

    if (turnIndex == 0) {
      return AudioTurnResponse(
        sessionId: 'call-sess-mock-001',
        turnIndex: 1,
        patientTranscript: patientWords ?? (defaultTranscript1[language] ?? defaultTranscript1['en']!),
        extractedFacts: [
          ExtractedFactSummary(
            category: 'chief_complaint',
            field: 'headache',
            concept: headacheConcept[language] ?? headacheConcept['en']!,
            conceptCode: 'SNOMED:25064002',
            duration: '2 days',
            confidence: 0.94,
            provenance: 'EMBEDDING',
          ),
          ExtractedFactSummary(
            category: 'symptom',
            field: 'fever',
            concept: feverConcept[language] ?? feverConcept['en']!,
            conceptCode: 'SNOMED:386661006',
            duration: '2 days',
            confidence: 0.91,
            provenance: 'EMBEDDING',
          ),
        ],
        nextQuestionText: q1[language] ?? q1['en']!,
        isCompleted: false,
      );
    } else {
      return AudioTurnResponse(
        sessionId: 'call-sess-mock-001',
        turnIndex: 2,
        patientTranscript: patientWords ?? (defaultTranscript2[language] ?? defaultTranscript2['en']!),
        extractedFacts: [
          ExtractedFactSummary(
            category: 'symptom',
            field: 'dizziness',
            concept: dizzinessDeniedConcept[language] ?? dizzinessDeniedConcept['en']!,
            conceptCode: 'SNOMED:404640003',
            confidence: 0.96,
            provenance: 'TOUCH',
          ),
        ],
        nextQuestionText: q2[language] ?? q2['en']!,
        isCompleted: true,
      );
    }
  }

  static List<ClinicalFact> getMockFacts() {
    return [
      const ClinicalFact(
        id: 'fact-001',
        encounterId: 'enc-mock-001',
        category: 'chief_complaint',
        field: 'headache',
        value: 'Severe frontal headache for 2 days',
        normalizedConcept: 'Severe Headache (तीव्र सिरदर्द)',
        conceptCode: 'SNOMED:25064002',
        patientWords: 'मुझे दो दिन से बहुत तेज सिरदर्द है',
        provenanceTier: 'EMBEDDING',
        confidence: 0.94,
        status: 'patient_confirmed',
      ),
      const ClinicalFact(
        id: 'fact-002',
        encounterId: 'enc-mock-001',
        category: 'symptom',
        field: 'fever',
        value: 'Mild fever ~99.5°F',
        normalizedConcept: 'Mild Pyrexia (हल्का बुखार)',
        conceptCode: 'SNOMED:386661006',
        patientWords: 'हल्का गर्म शरीर लग रहा है',
        provenanceTier: 'EMBEDDING',
        confidence: 0.91,
        status: 'patient_confirmed',
      ),
      const ClinicalFact(
        id: 'fact-003',
        encounterId: 'enc-mock-001',
        category: 'medication',
        field: 'paracetamol',
        value: 'Paracetamol 650mg as needed',
        dose: '650mg',
        frequency: '1-0-1',
        normalizedConcept: 'Paracetamol 650mg',
        conceptCode: 'SNOMED:387517004',
        patientWords: 'घर पर रखी डोलो गोली ली थी कल रात',
        provenanceTier: 'LOOKUP',
        confidence: 0.96,
        status: 'explain_back_verified',
      ),
    ];
  }

  static DocumentUploadResponse getMockDocumentUpload() {
    return const DocumentUploadResponse(
      documentId: 'doc-mock-001',
      ocrStatus: 'SUCCESS',
      extractedMedications: [
        ExtractedMedication(
          name: 'Paracetamol',
          dose: '650mg',
          frequency: '1-0-1 (सुबह-शाम)',
          sourceLines: [2, 3],
          box2d: [150, 45, 185, 320],
          confidence: 0.95,
        ),
        ExtractedMedication(
          name: 'Cetirizine',
          dose: '10mg',
          frequency: '0-0-1 (रात में)',
          sourceLines: [5],
          box2d: [220, 50, 255, 290],
          confidence: 0.92,
        ),
      ],
      flaggedInteractions: [],
      highlightedImageUrl: null,
      rawOcrText: 'Rx\nParacetamol 650mg BD\nCetirizine 10mg HS\nDr. S. Sharma',
      overallOcrConfidence: 0.93,
    );
  }

  static QueueStatusResponse getMockQueueStatus() {
    return const QueueStatusResponse(
      token: 'A-104',
      department: 'General Medicine',
      status: 'WAITING',
      patientsAhead: 3,
      estimatedWaitMinutes: 9,
      doctorRoom: 'Room 102 (Dr. Verma)',
    );
  }

  static AyurvedicIntakeRecord getMockAyush() {
    return const AyurvedicIntakeRecord(
      agni: AgniAssessment(
        agniType: 'sama',
        appetitePattern: 'regular',
        bowelRegularity: 'regular',
      ),
      prakritiBaseline: PrakritiAssessment(
        dominantDosha: 'tridoshaja',
        bodyFrame: 'medium_muscular',
        skinTexture: 'smooth_oily_cool',
        digestionSpeed: 'slow_steady',
        weatherSensitivity: 'intolerant_to_cold',
        sleepPattern: 'moderate_sound',
      ),
      koshtha: KoshthaAssessment(
        koshthaType: 'madhyama',
        bowelFrequency: 'once_daily',
        stoolConsistency: 'soft_formed',
      ),
      provisionalDoshaImbalance: ['pitta_vriddhi'],
    );
  }
}
