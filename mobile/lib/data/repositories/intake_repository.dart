import '../datasources/api_datasource.dart';
import '../datasources/mock_datasource.dart';
import '../models/encounter.dart';
import '../models/call_session.dart';
import '../models/document_result.dart';
import '../models/queue_status.dart';

/// Repository coordinating live backend vs offline mock data
/// Automatically provides mock fallbacks during network interruptions
class IntakeRepository {
  final ApiDataSource api;
  bool useMock;

  IntakeRepository({
    ApiDataSource? api,
    this.useMock = const bool.fromEnvironment('USE_MOCK', defaultValue: false),
  }) : api = api ?? ApiDataSource();

  Future<EncounterBootstrapResponse> bootstrap({
    String? qrToken,
    String channel = 'android_byod',
    String language = 'hi',
  }) async {
    if (useMock) {
      return MockDataSource.getMockBootstrap(language: language);
    }
    try {
      return await api.bootstrapEncounter(EncounterBootstrapRequest(
        qrToken: qrToken,
        deviceChannel: channel,
        language: language,
      ));
    } catch (_) {
      return MockDataSource.getMockBootstrap(language: language);
    }
  }

  Future<bool> updateLanguage({
    required String encounterId,
    required String language,
  }) async {
    if (useMock) return true;
    try {
      return await api.updateEncounterLanguage(encounterId, language);
    } catch (_) {
      return false;
    }
  }

  Future<CallSessionStartResponse> startCallSession({
    required String encounterId,
    required String language,
  }) async {
    if (useMock) {
      return MockDataSource.getMockCallStart(language: language);
    }
    try {
      return await api.startCallSession(CallSessionStartRequest(
        encounterId: encounterId,
        language: language,
      ));
    } catch (_) {
      return MockDataSource.getMockCallStart(language: language);
    }
  }

  Future<AudioTurnResponse> processAudioTurn({
    required String sessionId,
    required int turnIndex,
    String? fallbackWords,
    String language = 'hi',
  }) async {
    if (!useMock && fallbackWords != null && fallbackWords.isNotEmpty) {
      try {
        return await api.sendTextTurn(
          sessionId: sessionId,
          text: fallbackWords,
        );
      } catch (_) {
        // Fall back gracefully to mock if network fails
      }
    }
    // In mock mode or fallback, returns simulated SOCRATES adaptive turn
    return MockDataSource.getMockAudioTurn(
      turnIndex: turnIndex,
      patientWords: fallbackWords,
      language: language,
    );
  }

  Future<CallSessionEndResponse> endCallSession(String sessionId) async {
    if (useMock) {
      return const CallSessionEndResponse(
        encounterId: 'enc-mock-001',
        status: 'COMPLETED',
        assignedToken: 'A-104',
        department: 'General Medicine',
        totalFactsCaptured: 5,
        redFlagsDetected: false,
        severityBadge: 'GREEN',
      );
    }
    try {
      return await api.endCallSession(sessionId);
    } catch (_) {
      return const CallSessionEndResponse(
        encounterId: 'enc-mock-001',
        status: 'COMPLETED',
        assignedToken: 'A-104',
        department: 'General Medicine',
        totalFactsCaptured: 5,
        redFlagsDetected: false,
        severityBadge: 'GREEN',
      );
    }
  }

  Future<DocumentUploadResponse> uploadDocument(
    String encounterId, {
    List<int>? imageBytes,
    String filename = 'prescription.jpg',
  }) async {
    if (useMock) {
      return MockDataSource.getMockDocumentUpload(filename: filename);
    }
    try {
      return await api.uploadDocument(
        encounterId: encounterId,
        fileBytes: imageBytes,
        filename: filename,
      );
    } catch (_) {
      return MockDataSource.getMockDocumentUpload(filename: filename);
    }
  }

  Future<QueueStatusResponse> getQueueStatus(String token) async {
    if (useMock) {
      return MockDataSource.getMockQueueStatus();
    }
    try {
      return await api.getQueueStatus(token);
    } catch (_) {
      return MockDataSource.getMockQueueStatus();
    }
  }
}
