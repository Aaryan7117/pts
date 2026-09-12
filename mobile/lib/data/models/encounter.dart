/// Canonical Encounter models mirroring app/schemas/encounter.py
class LanguageOption {
  final String code;
  final String label;

  const LanguageOption({required this.code, required this.label});

  factory LanguageOption.fromJson(Map<String, dynamic> json) {
    return LanguageOption(
      code: json['code'] as String? ?? 'en',
      label: json['label'] as String? ?? 'English',
    );
  }

  Map<String, dynamic> toJson() => {'code': code, 'label': label};
}

const List<LanguageOption> kSupportedLanguages = [
  LanguageOption(code: 'en', label: 'English'),
  LanguageOption(code: 'hi', label: 'हिन्दी'),
  LanguageOption(code: 'ta', label: 'தமிழ்'),
  LanguageOption(code: 'te', label: 'తెలుగు'),
  LanguageOption(code: 'mr', label: 'मराठी'),
];

class EncounterBootstrapRequest {
  final String? qrToken;
  final String deviceChannel;
  final String language;

  const EncounterBootstrapRequest({
    this.qrToken,
    this.deviceChannel = 'android_byod',
    this.language = 'hi',
  });

  Map<String, dynamic> toJson() => {
        if (qrToken != null) 'qr_token': qrToken,
        'device_channel': deviceChannel,
        'language': language,
      };
}

class EncounterBootstrapResponse {
  final String encounterId;
  final String patientId;
  final String tokenNumber;
  final String status;
  final List<LanguageOption> supportedLanguages;

  const EncounterBootstrapResponse({
    required this.encounterId,
    required this.patientId,
    required this.tokenNumber,
    required this.status,
    required this.supportedLanguages,
  });

  factory EncounterBootstrapResponse.fromJson(Map<String, dynamic> json) {
    return EncounterBootstrapResponse(
      encounterId: json['encounter_id'] as String? ?? '',
      patientId: json['patient_id'] as String? ?? '',
      tokenNumber: json['token_number'] as String? ?? '',
      status: json['status'] as String? ?? 'BOOTSTRAPPED',
      supportedLanguages: (json['supported_languages'] as List<dynamic>?)
              ?.map((e) => LanguageOption.fromJson(e as Map<String, dynamic>))
              .toList() ??
          kSupportedLanguages,
    );
  }
}

class EncounterSummary {
  final String encounterId;
  final String tokenNumber;
  final String channel;
  final String language;
  final String status;
  final String severityBadge; // GREEN | YELLOW | RED
  final String department;
  final String? createdAt;
  final int factCount;
  final bool hasRedFlags;
  final String? summaryText;

  const EncounterSummary({
    required this.encounterId,
    required this.tokenNumber,
    required this.channel,
    required this.language,
    required this.status,
    required this.severityBadge,
    required this.department,
    this.createdAt,
    this.factCount = 0,
    this.hasRedFlags = false,
    this.summaryText,
  });

  factory EncounterSummary.fromJson(Map<String, dynamic> json) {
    return EncounterSummary(
      encounterId: json['encounter_id'] as String? ?? '',
      tokenNumber: json['token_number'] as String? ?? '',
      channel: json['channel'] as String? ?? 'kiosk',
      language: json['language'] as String? ?? 'hi',
      status: json['status'] as String? ?? 'BOOTSTRAPPED',
      severityBadge: json['severity_badge'] as String? ?? 'GREEN',
      department: json['department'] as String? ?? 'General Medicine',
      createdAt: json['created_at'] as String?,
      factCount: json['fact_count'] as int? ?? 0,
      hasRedFlags: json['has_red_flags'] as bool? ?? false,
      summaryText: json['summary_text'] as String?,
    );
  }
}
