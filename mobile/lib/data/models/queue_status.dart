/// Canonical Queue models mirroring app/schemas/queue.py & app/schemas/doctor.py
class QueueStatusResponse {
  final String token;
  final String department;
  final String status; // WAITING | CALLED | IN_CONSULTATION | COMPLETED
  final int patientsAhead;
  final int estimatedWaitMinutes;
  final String? doctorRoom;

  const QueueStatusResponse({
    required this.token,
    this.department = 'General Medicine',
    required this.status,
    this.patientsAhead = 0,
    this.estimatedWaitMinutes = 0,
    this.doctorRoom,
  });

  factory QueueStatusResponse.fromJson(Map<String, dynamic> json) {
    return QueueStatusResponse(
      token: json['token'] as String? ?? '',
      department: json['department'] as String? ?? 'General Medicine',
      status: json['status'] as String? ?? 'WAITING',
      patientsAhead: json['patients_ahead'] as int? ?? 0,
      estimatedWaitMinutes: json['estimated_wait_minutes'] as int? ?? 0,
      doctorRoom: json['doctor_room'] as String?,
    );
  }
}

class PatientQueueEntry {
  final String encounterId;
  final String tokenNumber;
  final String severityBadge; // GREEN | YELLOW | RED
  final String summary30Words;
  final String channel;
  final int factCount;
  final bool hasMedicationConflict;
  final bool hasRedFlags;
  final String? createdAt;

  const PatientQueueEntry({
    required this.encounterId,
    required this.tokenNumber,
    required this.severityBadge,
    required this.summary30Words,
    required this.channel,
    this.factCount = 0,
    this.hasMedicationConflict = false,
    this.hasRedFlags = false,
    this.createdAt,
  });

  factory PatientQueueEntry.fromJson(Map<String, dynamic> json) {
    return PatientQueueEntry(
      encounterId: json['encounter_id'] as String? ?? '',
      tokenNumber: json['token_number'] as String? ?? '',
      severityBadge: json['severity_badge'] as String? ?? 'GREEN',
      summary30Words: json['summary_30_words'] as String? ?? '',
      channel: json['channel'] as String? ?? 'kiosk',
      factCount: json['fact_count'] as int? ?? 0,
      hasMedicationConflict: json['has_medication_conflict'] as bool? ?? false,
      hasRedFlags: json['has_red_flags'] as bool? ?? false,
      createdAt: json['created_at'] as String?,
    );
  }
}
