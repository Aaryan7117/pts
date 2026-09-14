import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/encounter.dart';
import '../models/call_session.dart';
import '../models/queue_status.dart';
import '../models/document_result.dart';

/// FastAPI REST Client for MediKiosk
/// Connects to `http://<backend_host>:8000`
/// Ref: API_CONTRACT_AUDIT.md
class ApiDataSource {
  /// Default base URL. When testing on physical Android devices via `adb reverse tcp:8000 tcp:8000`,
  /// `http://localhost:8000` routes directly over USB to the development machine.
  /// Can be overridden via --dart-define=BACKEND_URL=... or --dart-define=API_BASE_URL=...
  static const String defaultBaseUrl = String.fromEnvironment(
    'BACKEND_URL',
    defaultValue: String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://localhost:8000',
    ),
  );
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

  /// Update Encounter Preferred Language
  Future<bool> updateEncounterLanguage(String encounterId, String language) async {
    final response = await client.patch(
      _uri('/api/encounters/$encounterId/language'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'language': language}),
    );
    return response.statusCode == 200;
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

  /// Calculate AYUSH Prakriti and Agni Scoring
  Future<Map<String, dynamic>> calculateAyushAssessment(
      Map<String, dynamic> ayushData) async {
    final response = await client.post(
      _uri('/api/ayush/calculate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(ayushData),
    );

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } else {
      throw HttpException('Failed to calculate AYUSH assessment: ${response.statusCode}');
    }
  }

  /// Save AYUSH Assessment for an Encounter
  Future<Map<String, dynamic>> saveAyushAssessment({
    required String encounterId,
    required Map<String, dynamic> intakeData,
  }) async {
    final response = await client.post(
      _uri('/api/ayush/encounter/$encounterId'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(intakeData),
    );

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } else {
      throw HttpException('Failed to save AYUSH assessment: ${response.statusCode}');
    }
  }

  /// Fetch AYUSH Assessment for an Encounter
  Future<Map<String, dynamic>> getAyushAssessment(String encounterId) async {
    final response = await client.get(_uri('/api/ayush/encounter/$encounterId'));

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } else {
      throw HttpException('Failed to fetch AYUSH assessment: ${response.statusCode}');
    }
  }

  /// Upload Prescription / Lab Document for OCR
  Future<DocumentUploadResponse> uploadDocument({
    required String encounterId,
    List<int>? fileBytes,
    String filename = 'prescription.jpg',
  }) async {
    final request = http.MultipartRequest('POST', _uri('/api/documents/upload'));
    request.fields['encounter_id'] = encounterId;

    final bytes = fileBytes ?? _minimalSampleJpeg;
    request.files.add(http.MultipartFile.fromBytes(
      'document',
      bytes,
      filename: filename,
    ));

    final streamedResponse = await client.send(request);
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      return DocumentUploadResponse.fromJson(
          jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>);
    } else {
      throw HttpException('Failed to upload document: ${response.statusCode}');
    }
  }

  /// Batch Upload Clinical Documents (Prescription, Lab Report, Discharge Summary)
  Future<Map<String, dynamic>> batchUploadDocuments({
    required String encounterId,
    required List<File> files,
    String documentType = 'prescription',
    String? patientId,
    String? documentDate,
  }) async {
    final request = http.MultipartRequest('POST', _uri('/api/documents/batch-upload'));
    request.fields['encounter_id'] = encounterId;
    request.fields['document_type'] = documentType;
    if (patientId != null) request.fields['patient_id'] = patientId;
    if (documentDate != null) request.fields['document_date'] = documentDate;

    for (final file in files) {
      final stream = http.ByteStream(file.openRead());
      final length = await file.length();
      final multipartFile = http.MultipartFile(
        'files',
        stream,
        length,
        filename: file.path.split(Platform.pathSeparator).last,
      );
      request.files.add(multipartFile);
    }

    final streamedResponse = await client.send(request);
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } else {
      throw HttpException('Failed to upload documents: ${response.statusCode}');
    }
  }

  /// Fetch Longitudinal Document Timeline with Lab Panic Checks
  Future<Map<String, dynamic>> getEncounterTimeline(String encounterId) async {
    final response = await client.get(_uri('/api/documents/encounter/$encounterId/timeline'));

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } else {
      throw HttpException('Failed to fetch document timeline: ${response.statusCode}');
    }
  }

  /// Patient Portal: Fetch Personal Dashboard & ABHA Card
  Future<Map<String, dynamic>> getPatientDashboard(String patientId) async {
    final response = await client.get(_uri('/api/patient/dashboard/$patientId'));

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } else {
      throw HttpException('Failed to fetch patient dashboard: ${response.statusCode}');
    }
  }

  /// Doctor Verification Sign-off
  Future<Map<String, dynamic>> verifyEncounter({
    required String encounterId,
    required String doctorId,
    required String doctorNotes,
    String status = 'VERIFIED',
  }) async {
    final response = await client.post(
      _uri('/api/doctor/encounter/$encounterId/verify'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'doctor_id': doctorId,
        'doctor_notes': doctorNotes,
        'status': status,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } else {
      throw HttpException('Failed to verify encounter: ${response.statusCode}');
    }
  }

  /// Doctor ABHA Lookup: Retrieve Longitudinal Patient History
  Future<Map<String, dynamic>> lookupPatientByAbha(String abhaId) async {
    final response = await client.get(_uri('/api/doctor/patient/by-abha/$abhaId'));

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } else {
      throw HttpException('Failed to lookup patient by ABHA: ${response.statusCode}');
    }
  }

  /// OPD Hospital Directory with Phone Numbers and Room Numbers
  Future<List<dynamic>> getHospitalDirectory() async {
    final response = await client.get(_uri('/api/auth/directory'));

    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      return (data['doctors'] as List<dynamic>?) ?? [];
    } else {
      throw HttpException('Failed to fetch hospital directory: ${response.statusCode}');
    }
  }

  // 1x1 valid JPEG byte payload fallback for simulated camera capture
  static const List<int> _minimalSampleJpeg = [
    0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x01, 0x00, 0x48,
    0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43, 0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
    0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
    0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20, 0x24, 0x2E, 0x27, 0x20,
    0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29, 0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27,
    0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
    0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00, 0x01, 0x05, 0x01, 0x01,
    0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04,
    0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F,
    0x00, 0xBF, 0x80, 0xFF, 0xD9,
  ];
}

