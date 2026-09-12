/// Canonical Call Session models mirroring app/schemas/call_session.py
class CallSessionStartRequest {
  final String encounterId;
  final String language;

  const CallSessionStartRequest({
    required this.encounterId,
    this.language = 'hi',
  });

  Map<String, dynamic> toJson() => {
        'encounter_id': encounterId,
        'language': language,
      };
}

class CallSessionStartResponse {
  final String sessionId;
  final String status;
  final String openingText;
  final String? openingAudioBase64;

  const CallSessionStartResponse({
    required this.sessionId,
    required this.status,
    required this.openingText,
    this.openingAudioBase64,
  });

  factory CallSessionStartResponse.fromJson(Map<String, dynamic> json) {
    return CallSessionStartResponse(
      sessionId: json['session_id'] as String? ?? '',
      status: json['status'] as String? ?? 'CALL_ACTIVE',
      openingText: json['opening_text'] as String? ?? '',
      openingAudioBase64: json['opening_audio_base64'] as String?,
    );
  }
}

class ExtractedFactSummary {
  final String category;
  final String field;
  final String concept;
  final String? conceptCode;
  final String? duration;
  final double confidence;
  final String provenance;

  const ExtractedFactSummary({
    required this.category,
    required this.field,
    required this.concept,
    this.conceptCode,
    this.duration,
    required this.confidence,
    required this.provenance,
  });

  factory ExtractedFactSummary.fromJson(Map<String, dynamic> json) {
    return ExtractedFactSummary(
      category: json['category'] as String? ?? '',
      field: json['field'] as String? ?? '',
      concept: json['concept'] as String? ?? '',
      conceptCode: json['concept_code'] as String?,
      duration: json['duration'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      provenance: json['provenance'] as String? ?? 'EMBEDDING',
    );
  }
}

class AudioTurnResponse {
  final String sessionId;
  final int turnIndex;
  final String patientTranscript;
  final List<ExtractedFactSummary> extractedFacts;
  final String? nextQuestionText;
  final String? nextQuestionAudioBase64;
  final bool isCompleted;

  const AudioTurnResponse({
    required this.sessionId,
    required this.turnIndex,
    required this.patientTranscript,
    required this.extractedFacts,
    this.nextQuestionText,
    this.nextQuestionAudioBase64,
    this.isCompleted = false,
  });

  factory AudioTurnResponse.fromJson(Map<String, dynamic> json) {
    return AudioTurnResponse(
      sessionId: json['session_id'] as String? ?? '',
      turnIndex: json['turn_index'] as int? ?? 0,
      patientTranscript: json['patient_transcript'] as String? ?? '',
      extractedFacts: (json['extracted_facts'] as List<dynamic>?)
              ?.map((e) => ExtractedFactSummary.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      nextQuestionText: json['next_question_text'] as String?,
      nextQuestionAudioBase64: json['next_question_audio_base64'] as String?,
      isCompleted: json['is_completed'] as bool? ?? false,
    );
  }
}

class CallSessionEndResponse {
  final String encounterId;
  final String status;
  final String assignedToken;
  final String department;
  final int totalFactsCaptured;
  final bool redFlagsDetected;
  final String severityBadge;

  const CallSessionEndResponse({
    required this.encounterId,
    required this.status,
    required this.assignedToken,
    required this.department,
    required this.totalFactsCaptured,
    required this.redFlagsDetected,
    required this.severityBadge,
  });

  factory CallSessionEndResponse.fromJson(Map<String, dynamic> json) {
    return CallSessionEndResponse(
      encounterId: json['encounter_id'] as String? ?? '',
      status: json['status'] as String? ?? 'COMPLETED',
      assignedToken: json['assigned_token'] as String? ?? '',
      department: json['department'] as String? ?? 'General Medicine',
      totalFactsCaptured: json['total_facts_captured'] as int? ?? 0,
      redFlagsDetected: json['red_flags_detected'] as bool? ?? false,
      severityBadge: json['severity_badge'] as String? ?? 'GREEN',
    );
  }
}
