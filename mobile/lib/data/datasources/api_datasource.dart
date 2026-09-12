import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/encounter.dart';
import '../models/call_session.dart';
import '../models/queue_status.dart';

/// FastAPI REST Client for MediKiosk
/// Connects to `http://<backend_host>:8000`
/// Ref: API_CONTRACT_AUDIT.md
class ApiDataSource {
  static String defaultBaseUrl = 'http://10.0.2.2:8000';
  final String baseUrl;
  final http.Client client;

  ApiDataSource({
    String? baseUrl,
    http.Client? client,
  })  : baseUrl = baseUrl ?? defaultBaseUrl,
        client = client ?? http.Client();

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

  /// Health Check
  Future<bool> checkHealth() async {
    try {
      final response = await client
          .get(_uri('/api/health'))
          .timeout(const Duration(seconds: 3));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Bootstrap Encounter
  Future<EncounterBootstrapResponse> bootstrapEncounter(
      EncounterBootstrapRequest request) async {
    final response = await client.post(
      _uri('/api/encounters/bootstrap'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode == 200) {
      return EncounterBootstrapResponse.fromJson(
          jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    } else {
      throw HttpException('Failed to bootstrap encounter: ${response.statusCode}');
    }
  }

  /// Start Voice Call Session
  Future<CallSessionStartResponse> startCallSession(
      CallSessionStartRequest request) async {
    final response = await client.post(
      _uri('/api/call/session/start'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode == 200) {
      return CallSessionStartResponse.fromJson(
          jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    } else {
      throw HttpException('Failed to start call session: ${response.statusCode}');
    }
  }

  /// Process Text / Symptom Turn
  Future<AudioTurnResponse> sendTextTurn({
    required String sessionId,
    required String text,
  }) async {
    final response = await client.post(
      _uri('/api/call/text-turn'),
      body: {
        'session_id': sessionId,
        'text': text,
      },
    );

    if (response.statusCode == 200) {
      return AudioTurnResponse.fromJson(
          jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    } else {
      throw HttpException('Failed to process text turn: ${response.statusCode}');
    }
  }

  /// End Voice Call Session
  Future<CallSessionEndResponse> endCallSession(String sessionId) async {
    final response = await client.post(
      _uri('/api/call/session/end'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'session_id': sessionId}),
    );

    if (response.statusCode == 200) {
      return CallSessionEndResponse.fromJson(
          jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    } else {
      throw HttpException('Failed to end call session: ${response.statusCode}');
    }
  }

  /// Get Live Queue Status
  Future<QueueStatusResponse> getQueueStatus(String token) async {
    final response = await client.get(_uri('/api/queue/status/$token'));

    if (response.statusCode == 200) {
      return QueueStatusResponse.fromJson(
          jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    } else {
      throw HttpException('Failed to fetch queue status: ${response.statusCode}');
    }
  }
}
