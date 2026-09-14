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

    final words = patientWords?.trim() ?? '';

    if (words.isNotEmpty) {
      final List<ExtractedFactSummary> facts = [];
      final lower = words.toLowerCase();

      if (words.contains('उल्टी') || words.contains('வாந்தி') || words.contains('వాంతి') || words.contains('उलटी') || lower.contains('vomit') || lower.contains('nausea')) {
        facts.add(const ExtractedFactSummary(
          category: 'chief_complaint',
          field: 'vomiting',
          concept: 'Nausea and Vomiting (उल्टी / मिचली)',
          conceptCode: 'SNOMED:422400008',
          duration: '1-2 days',
          confidence: 0.96,
          provenance: 'EMBEDDING',
        ));
      }
      if (words.contains('पेट दर्द') || words.contains('வயிற்று வலி') || words.contains('కడుపు నొప్పి') || words.contains('पोटदुखी') || lower.contains('stomach') || lower.contains('abdominal')) {
        facts.add(const ExtractedFactSummary(
          category: 'chief_complaint',
          field: 'abdominal_pain',
          concept: 'Abdominal Pain (पेट दर्द)',
          conceptCode: 'SNOMED:21522001',
          duration: '2 days',
          confidence: 0.95,
          provenance: 'EMBEDDING',
        ));
      }
      if (words.contains('बुखार') || words.contains('காய்ச்சல்') || words.contains('జ్వరం') || words.contains('ताप') || lower.contains('fever') || lower.contains('pyrexia')) {
        facts.add(ExtractedFactSummary(
          category: 'chief_complaint',
          field: 'fever',
          concept: feverConcept[language] ?? 'Pyrexia / Fever (बुखार)',
          conceptCode: 'SNOMED:386661006',
          duration: '2 days',
          confidence: 0.93,
          provenance: 'EMBEDDING',
        ));
      }
      if (words.contains('खांसी') || words.contains('இருமல்') || words.contains('దగ్గు') || words.contains('खोकला') || lower.contains('cough')) {
        facts.add(const ExtractedFactSummary(
          category: 'chief_complaint',
          field: 'cough',
          concept: 'Cough (खांसी)',
          conceptCode: 'SNOMED:49727002',
          duration: '3 days',
          confidence: 0.94,
          provenance: 'EMBEDDING',
        ));
      }
      if (words.contains('छाती') || words.contains('நெஞ்சு') || words.contains('ఛాతీ') || words.contains('छातीत') || lower.contains('chest')) {
        facts.add(const ExtractedFactSummary(
          category: 'chief_complaint',
          field: 'chest_pain',
          concept: 'Chest Pain (छाती में दर्द)',
          conceptCode: 'SNOMED:29857009',
          duration: '1 day',
          confidence: 0.97,
          provenance: 'EMBEDDING',
        ));
      }
      if (words.contains('सिरदर्द') || words.contains('தலைவலி') || words.contains('తలనొప్పి') || words.contains('डोकेदुखी') || lower.contains('headache')) {
        facts.add(ExtractedFactSummary(
          category: 'chief_complaint',
          field: 'headache',
          concept: headacheConcept[language] ?? 'Severe Headache (तीव्र सिरदर्द)',
          conceptCode: 'SNOMED:25064002',
          duration: '2 days',
          confidence: 0.94,
          provenance: 'EMBEDDING',
        ));
      }
      if (words.contains('चक्कर') || words.contains('தலைச்சுற்றல்') || words.contains('తలతిరగడం') || lower.contains('dizziness')) {
        facts.add(const ExtractedFactSummary(
          category: 'symptom',
          field: 'dizziness',
          concept: 'Dizziness / Vertigo (चक्कर आना)',
          conceptCode: 'SNOMED:404640003',
          confidence: 0.92,
          provenance: 'EMBEDDING',
        ));
      }

      if (facts.isEmpty) {
        facts.add(ExtractedFactSummary(
          category: 'chief_complaint',
          field: 'reported_symptom',
          concept: words,
          confidence: 0.90,
          provenance: 'PATIENT_VOICE',
        ));
      }

      return AudioTurnResponse(
        sessionId: 'call-sess-live-001',
        turnIndex: turnIndex + 1,
        patientTranscript: words,
        extractedFacts: facts,
        nextQuestionText: turnIndex == 0 ? (q1[language] ?? q1['en']!) : (q2[language] ?? q2['en']!),
        isCompleted: turnIndex >= 1,
      );
    }

    // Default mock turn when patientWords is not provided
    if (turnIndex == 0) {
      return AudioTurnResponse(
        sessionId: 'call-sess-mock-001',
        turnIndex: 1,
        patientTranscript: defaultTranscript1[language] ?? defaultTranscript1['en']!,
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
        patientTranscript: defaultTranscript2[language] ?? defaultTranscript2['en']!,
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

  static DocumentUploadResponse getMockDocumentUpload({String filename = 'prescription.jpg'}) {
    final lower = filename.toLowerCase();
    if (lower.contains('rajesh')) {
      return const DocumentUploadResponse(
        documentId: 'doc-demo-rajesh-01',
        ocrStatus: 'SUCCESS',
        extractedMedications: [
          ExtractedMedication(name: 'Telmisartan', dose: '40mg', frequency: '1-0-0 (सुबह)', confidence: 0.96),
          ExtractedMedication(name: 'Amlodipine', dose: '5mg', frequency: '0-0-1 (रात)', confidence: 0.94),
          ExtractedMedication(name: 'Ecosprin', dose: '75mg', frequency: '0-1-0 (दोपहर)', confidence: 0.95),
        ],
        flaggedInteractions: [],
        highlightedImageUrl: 'http://localhost:8000/static/evidence/doc-demo-rajesh-rx-boxed.jpg',
        rawOcrText: 'Rx\nTab Telmisartan 40mg OD\nTab Amlodipine 5mg OD\nTab Ecosprin 75mg OD\nDr. V. Verma (Cardiology)',
        overallOcrConfidence: 0.95,
      );
    } else if (lower.contains('priya')) {
      return const DocumentUploadResponse(
        documentId: 'doc-demo-priya-01',
        ocrStatus: 'SUCCESS',
        extractedMedications: [
          ExtractedMedication(name: 'Pantoprazole', dose: '40mg', frequency: '1-0-0 (खाली पेट)', confidence: 0.96),
          ExtractedMedication(name: 'Domperidone', dose: '10mg', frequency: '1-0-1 (खाने से पहले)', confidence: 0.93),
        ],
        flaggedInteractions: [],
        highlightedImageUrl: 'http://localhost:8000/static/evidence/doc-demo-priya-rx-boxed.jpg',
        rawOcrText: 'Rx\nTab Pantoprazole 40mg OD\nTab Domperidone 10mg BD\nDr. P. Nair (Gastro)',
        overallOcrConfidence: 0.94,
      );
    } else if (lower.contains('sunita')) {
      return const DocumentUploadResponse(
        documentId: 'doc-demo-sunita-01',
        ocrStatus: 'SUCCESS',
        extractedMedications: [
          ExtractedMedication(name: 'Fasting Plasma Glucose', dose: '382 mg/dL', frequency: 'PANIC ALERT', confidence: 0.99),
          ExtractedMedication(name: 'HbA1c Glycated Hemoglobin', dose: '11.4 %', frequency: 'UNCONTROLLED', confidence: 0.98),
        ],
        flaggedInteractions: ['CRITICAL PANIC VALUE: Fasting Blood Glucose > 300 mg/dL'],
        highlightedImageUrl: 'http://localhost:8000/static/evidence/doc-demo-sunita-lab-boxed.jpg',
        rawOcrText: 'BIOCHEMISTRY REPORT\nFasting Blood Sugar: 382 mg/dL [REF: 70-100]\nHbA1c: 11.4 % [REF: < 5.7]\nCity Pathology Labs',
        overallOcrConfidence: 0.98,
      );
    }

    // Default to Lakshmi Devi (Diabetes OPD Rx)
    return const DocumentUploadResponse(
      documentId: 'doc-demo-lakshmi-01',
      ocrStatus: 'SUCCESS',
      extractedMedications: [
        ExtractedMedication(name: 'Metformin', dose: '500mg', frequency: '1-0-1 (सुबह-शाम)', confidence: 0.97),
        ExtractedMedication(name: 'Glimepiride', dose: '1mg', frequency: '1-0-0 (सुबह नाश्ते से पहले)', confidence: 0.95),
        ExtractedMedication(name: 'Atorvastatin', dose: '10mg', frequency: '0-0-1 (रात में)', confidence: 0.93),
      ],
      flaggedInteractions: ['Metformin + Glimepiride: Monitor for hypoglycemia'],
      highlightedImageUrl: 'http://localhost:8000/static/evidence/doc-demo-lakshmi-rx-boxed.jpg',
      rawOcrText: 'Rx\nTab Metformin 500mg BD\nTab Glimepiride 1mg OD\nTab Atorvastatin 10mg HS\nDr. S. Sharma (General Medicine)',
      overallOcrConfidence: 0.96,
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
