import '../datasources/api_datasource.dart';
import '../datasources/mock_datasource.dart';
import '../models/encounter.dart';
import '../models/call_session.dart';
import '../models/document_result.dart';
import '../models/queue_status.dart';

/// Repository coordinating live backend vs test mock data.
/// Fences MockDataSource strictly behind explicit `USE_MOCK=true` environment flag.
/// Production and shipped paths (USE_MOCK=false) communicate strictly with the live backend
/// and propagate network failures so the UI presents honest offline/error states (Ticket T-011).
class IntakeRepository {
  final ApiDataSource api;
  final bool useMock;

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
    return await api.bootstrapEncounter(EncounterBootstrapRequest(
      qrToken: qrToken,
      deviceChannel: channel,
      language: language,
    ));
  }

  Future<bool> updateLanguage({
    required String encounterId,
    required String language,
  }) async {
    if (useMock) return true;
    return await api.updateEncounterLanguage(encounterId, language);
  }

  Future<CallSessionStartResponse> startCallSession({
    required String encounterId,
    required String language,
    String? department,
  }) async {
    if (useMock) {
      return MockDataSource.getMockCallStart(language: language);
    }
    return await api.startCallSession(CallSessionStartRequest(
      encounterId: encounterId,
      language: language,
      department: department,
    ));
  }

  Future<AudioTurnResponse> processAudioTurn({
    required String sessionId,
    required int turnIndex,
    String? fallbackWords,
    String language = 'hi',
  }) async {
    if (useMock) {
      return MockDataSource.getMockAudioTurn(
        turnIndex: turnIndex,
        patientWords: fallbackWords,
        language: language,
      );
    }

    if (fallbackWords != null && fallbackWords.isNotEmpty) {
      return await api.sendTextTurn(
        sessionId: sessionId,
        text: fallbackWords,
        language: language,
      );
    }

    throw StateError('Cannot process voice turn without audio payload or patient transcript.');
  }

  Future<CallSessionEndResponse> endCallSession(String sessionId) async {
    if (useMock) {
      return const CallSessionEndResponse(
        encounterId: 'enc-test-001',
        status: 'COMPLETED',
        assignedToken: 'A-104',
        department: 'General Medicine',
        totalFactsCaptured: 5,
        redFlagsDetected: false,
        severityBadge: 'GREEN',
      );
    }
    return await api.endCallSession(sessionId);
  }

  Future<DocumentUploadResponse> uploadDocument(
    String encounterId, {
    List<int>? imageBytes,
    String filename = 'prescription.jpg',
  }) async {
    if (useMock) {
      return MockDataSource.getMockDocumentUpload(filename: filename);
    }
    return await api.uploadDocument(
      encounterId: encounterId,
      fileBytes: imageBytes,
      filename: filename,
    );
  }

  Future<QueueStatusResponse> getQueueStatus(String token) async {
    if (useMock) {
      return MockDataSource.getMockQueueStatus();
    }
    return await api.getQueueStatus(token);
  }
}
