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
    final opening = language == 'hi'
        ? 'नमस्ते, मैं मेडीकिओस्क हूँ। आज आपको क्या परेशानी महसूस हो रही है?'
        : 'Hello, I am MediKiosk. What symptoms are you experiencing today?';

    return CallSessionStartResponse(
      sessionId: 'call-sess-mock-001',
      status: 'CALL_ACTIVE',
      openingText: opening,
      openingAudioBase64: null,
    );
  }

  static AudioTurnResponse getMockAudioTurn({
    required int turnIndex,
    String? patientWords,
  }) {
    final words = patientWords?.trim() ?? '';
    final List<ExtractedFactSummary> facts = [];

    if (words.contains('उल्टी') || words.toLowerCase().contains('vomit') || words.toLowerCase().contains('nausea')) {
      facts.add(const ExtractedFactSummary(
        category: 'chief_complaint',
        field: 'vomiting',
        concept: 'Nausea and Vomiting (उल्टी / मिचली)',
        conceptCode: 'SNOMED:422400008',
        duration: '1-2 days',
        confidence: 0.96,
        provenance: 'EMBEDDING',
      ));
    } else if (words.contains('पेट दर्द') || words.toLowerCase().contains('stomach') || words.toLowerCase().contains('abdominal')) {
      facts.add(const ExtractedFactSummary(
        category: 'chief_complaint',
        field: 'abdominal_pain',
        concept: 'Abdominal Pain (पेट दर्द)',
        conceptCode: 'SNOMED:21522001',
        duration: '2 days',
        confidence: 0.95,
        provenance: 'EMBEDDING',
      ));
    } else if (words.contains('बुखार') || words.toLowerCase().contains('fever')) {
      facts.add(const ExtractedFactSummary(
        category: 'chief_complaint',
        field: 'fever',
        concept: 'Pyrexia / Fever (बुखार)',
        conceptCode: 'SNOMED:386661006',
        duration: '2 days',
        confidence: 0.93,
        provenance: 'EMBEDDING',
      ));
    } else if (words.contains('खांसी') || words.toLowerCase().contains('cough')) {
      facts.add(const ExtractedFactSummary(
        category: 'chief_complaint',
        field: 'cough',
        concept: 'Cough (खांसी)',
        conceptCode: 'SNOMED:49727002',
        duration: '3 days',
        confidence: 0.94,
        provenance: 'EMBEDDING',
      ));
    } else if (words.contains('छाती') || words.toLowerCase().contains('chest')) {
      facts.add(const ExtractedFactSummary(
        category: 'chief_complaint',
        field: 'chest_pain',
        concept: 'Chest Pain (छाती में दर्द)',
        conceptCode: 'SNOMED:29857009',
        duration: '1 day',
        confidence: 0.97,
        provenance: 'EMBEDDING',
      ));
    } else if (words.contains('चक्कर') || words.toLowerCase().contains('dizziness')) {
      facts.add(const ExtractedFactSummary(
        category: 'symptom',
        field: 'dizziness',
        concept: 'Dizziness / Vertigo (चक्कर आना)',
        conceptCode: 'SNOMED:404640003',
        confidence: 0.92,
        provenance: 'EMBEDDING',
      ));
    } else if (words.contains('सिरदर्द') || words.toLowerCase().contains('headache')) {
      facts.add(const ExtractedFactSummary(
        category: 'chief_complaint',
        field: 'headache',
        concept: 'Severe Headache (तीव्र सिरदर्द)',
        conceptCode: 'SNOMED:25064002',
        duration: '2 days',
        confidence: 0.94,
        provenance: 'EMBEDDING',
      ));
    } else if (words.isNotEmpty) {
      facts.add(ExtractedFactSummary(
        category: 'chief_complaint',
        field: 'reported_symptom',
        concept: words,
        confidence: 0.90,
        provenance: 'PATIENT_VOICE',
      ));
    } else {
      facts.add(const ExtractedFactSummary(
        category: 'chief_complaint',
        field: 'general_complaint',
        concept: 'General Consultation (सामान्य परामर्श)',
        confidence: 0.90,
        provenance: 'PATIENT_VOICE',
      ));
    }

    return AudioTurnResponse(
      sessionId: 'call-sess-live-001',
      turnIndex: turnIndex + 1,
      patientTranscript: words.isNotEmpty ? words : 'सामान्य परामर्श',
      extractedFacts: facts,
      nextQuestionText: 'क्या आप पहले से कोई नियमित दवा ले रहे हैं या कोई पर्ची है?',
      isCompleted: turnIndex >= 1,
    );
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
