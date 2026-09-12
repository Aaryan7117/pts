import 'package:flutter/material.dart';
import '../../data/models/clinical_fact.dart';
import '../../data/models/document_result.dart';
import '../../data/models/ayush_profile.dart';
import '../../data/repositories/intake_repository.dart';

/// Intake state provider coordinating voice loops, SOCRATES questions, and clinical facts
class IntakeProvider extends ChangeNotifier {
  final IntakeRepository _repository;

  String? _sessionId;
  int _turnCount = 0;
  bool _isListening = false;
  String _currentTranscript = '';
  String _activeQuestion = 'नमस्ते, मैं मेडीकिओस्क हूँ। आज आपको क्या परेशानी महसूस हो रही है?';
  bool _isInterviewCompleted = false;

  final List<ClinicalFact> _facts = [];
  final List<ExtractedMedication> _extractedMedications = [];
  final Map<String, String> _vitals = {
    'Blood Pressure': '120/80 mmHg',
    'Heart Rate': '72 bpm',
    'SpO2': '98%',
    'Temperature': '98.6 °F',
    'Blood Sugar': '110 mg/dL',
  };
  AyurvedicIntakeRecord? _ayushRecord;

  IntakeProvider({IntakeRepository? repository})
      : _repository = repository ?? IntakeRepository();

  String? get sessionId => _sessionId;
  int get turnCount => _turnCount;
  bool get isListening => _isListening;
  String get currentTranscript => _currentTranscript;
  String get activeQuestion => _activeQuestion;
  bool get isInterviewCompleted => _isInterviewCompleted;
  List<ClinicalFact> get facts => List.unmodifiable(_facts);
  List<ExtractedMedication> get extractedMedications => List.unmodifiable(_extractedMedications);
  Map<String, String> get vitals => Map.unmodifiable(_vitals);
  AyurvedicIntakeRecord? get ayushRecord => _ayushRecord;

  void toggleListening({String? simulatedTranscript}) {
    _isListening = !_isListening;
    if (!_isListening && simulatedTranscript != null) {
      _currentTranscript = simulatedTranscript;
    }
    notifyListeners();
  }

  Future<void> startSession({required String encounterId, required String language}) async {
    final res = await _repository.startCallSession(
      encounterId: encounterId,
      language: language,
    );
    _sessionId = res.sessionId;
    _activeQuestion = res.openingText;
    _turnCount = 0;
    _isInterviewCompleted = false;
    notifyListeners();
  }

  Future<void> submitTurn({String? patientSpeech}) async {
    _isListening = false;
    final res = await _repository.processAudioTurn(
      sessionId: _sessionId ?? 'mock-session',
      turnIndex: _turnCount,
      fallbackWords: patientSpeech ?? _currentTranscript,
    );

    _turnCount++;
    _currentTranscript = res.patientTranscript;
    if (res.nextQuestionText != null) {
      _activeQuestion = res.nextQuestionText!;
    }
    _isInterviewCompleted = res.isCompleted;

    // Convert summaries to full ClinicalFact objects
    for (var s in res.extractedFacts) {
      _facts.add(ClinicalFact(
        id: 'fact-${DateTime.now().millisecondsSinceEpoch}-${_facts.length}',
        encounterId: 'active-encounter',
        category: s.category,
        field: s.field,
        value: s.concept,
        normalizedConcept: s.concept,
        conceptCode: s.conceptCode,
        patientWords: _currentTranscript,
        provenanceTier: s.provenance,
        confidence: s.confidence,
        status: 'pending',
      ));
    }
    notifyListeners();
  }

  void confirmFact(String factId) {
    final index = _facts.indexWhere((f) => f.id == factId);
    if (index != -1) {
      final old = _facts[index];
      _facts[index] = ClinicalFact(
        id: old.id,
        encounterId: old.encounterId,
        category: old.category,
        field: old.field,
        value: old.value,
        dose: old.dose,
        frequency: old.frequency,
        patientWords: old.patientWords,
        normalizedConcept: old.normalizedConcept,
        conceptCode: old.conceptCode,
        provenanceTier: old.provenanceTier,
        confidence: old.confidence,
        status: 'patient_confirmed',
      );
      notifyListeners();
    }
  }

  void rejectFact(String factId) {
    _facts.removeWhere((f) => f.id == factId);
    notifyListeners();
  }

  Future<void> processDocument(String encounterId) async {
    final result = await _repository.uploadDocument(encounterId);
    _extractedMedications.clear();
    _extractedMedications.addAll(result.extractedMedications);

    for (var med in result.extractedMedications) {
      _facts.add(ClinicalFact(
        id: 'doc-fact-${DateTime.now().millisecondsSinceEpoch}',
        encounterId: encounterId,
        category: 'medication',
        field: med.name.toLowerCase(),
        value: '${med.name} ${med.dose ?? ''}',
        dose: med.dose,
        frequency: med.frequency,
        normalizedConcept: med.name,
        provenanceTier: 'OCR',
        sourceType: 'document_ocr',
        confidence: med.confidence,
        status: 'pending',
      ));
    }
    notifyListeners();
  }

  void setVital(String key, String value) {
    _vitals[key] = value;
    notifyListeners();
  }

  void setAyushRecord(AyurvedicIntakeRecord record) {
    _ayushRecord = record;
    notifyListeners();
  }

  void clearIntake() {
    _sessionId = null;
    _turnCount = 0;
    _isListening = false;
    _currentTranscript = '';
    _activeQuestion = '';
    _isInterviewCompleted = false;
    _facts.clear();
    _extractedMedications.clear();
    _ayushRecord = null;
    notifyListeners();
  }
}
