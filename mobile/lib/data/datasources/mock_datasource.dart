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
    if (turnIndex == 0) {
      return AudioTurnResponse(
        sessionId: 'call-sess-mock-001',
        turnIndex: 1,
        patientTranscript: patientWords ?? 'मुझे दो दिन से तेज सिरदर्द और हल्का बुखार है',
        extractedFacts: [
          const ExtractedFactSummary(
            category: 'chief_complaint',
            field: 'headache',
            concept: 'Severe Headache (तीव्र सिरदर्द)',
            conceptCode: 'SNOMED:25064002',
            duration: '2 days',
            confidence: 0.94,
            provenance: 'EMBEDDING',
          ),
          const ExtractedFactSummary(
            category: 'symptom',
            field: 'fever',
            concept: 'Mild Pyrexia (हल्का बुखार)',
            conceptCode: 'SNOMED:386661006',
            duration: '2 days',
            confidence: 0.91,
            provenance: 'EMBEDDING',
          ),
        ],
        nextQuestionText: 'क्या आपको सिरदर्द के साथ चक्कर या उल्टी जैसा भी लग रहा है?',
        isCompleted: false,
      );
    } else {
      return AudioTurnResponse(
        sessionId: 'call-sess-mock-001',
        turnIndex: 2,
        patientTranscript: patientWords ?? 'नहीं, कोई चक्कर नहीं आ रहा है',
        extractedFacts: [
          const ExtractedFactSummary(
            category: 'symptom',
            field: 'dizziness',
            concept: 'Dizziness Denied (चक्कर नहीं)',
            conceptCode: 'SNOMED:404640003',
            confidence: 0.96,
            provenance: 'TOUCH',
          ),
        ],
        nextQuestionText: 'क्या आप पहले से कोई नियमित दवा ले रहे हैं?',
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
