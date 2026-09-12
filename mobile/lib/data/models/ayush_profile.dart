/// Canonical AYUSH models mirroring app/schemas/ayush.py
class AgniAssessment {
  final String agniType; // sama | vishama | tikshna | manda
  final String appetitePattern;
  final bool postMealHeaviness;
  final String bowelRegularity;
  final String namasteCode;

  const AgniAssessment({
    required this.agniType,
    required this.appetitePattern,
    this.postMealHeaviness = false,
    required this.bowelRegularity,
    this.namasteCode = 'NAMASTE:AGNI-001',
  });

  factory AgniAssessment.fromJson(Map<String, dynamic> json) {
    return AgniAssessment(
      agniType: json['agni_type'] as String? ?? 'sama',
      appetitePattern: json['appetite_pattern'] as String? ?? 'regular',
      postMealHeaviness: json['post_meal_heaviness'] as bool? ?? false,
      bowelRegularity: json['bowel_regularity'] as String? ?? 'regular',
      namasteCode: json['namaste_code'] as String? ?? 'NAMASTE:AGNI-001',
    );
  }

  Map<String, dynamic> toJson() => {
        'agni_type': agniType,
        'appetite_pattern': appetitePattern,
        'post_meal_heaviness': postMealHeaviness,
        'bowel_regularity': bowelRegularity,
        'namaste_code': namasteCode,
      };
}

class PrakritiAssessment {
  final String dominantDosha; // vata | pitta | kapha | dvandvaja_* | tridoshaja
  final String bodyFrame;
  final String skinTexture;
  final String digestionSpeed;
  final String weatherSensitivity;
  final String sleepPattern;
  final String namasteCode;

  const PrakritiAssessment({
    required this.dominantDosha,
    required this.bodyFrame,
    required this.skinTexture,
    required this.digestionSpeed,
    required this.weatherSensitivity,
    required this.sleepPattern,
    this.namasteCode = 'NAMASTE:PRAKRITI-001',
  });

  factory PrakritiAssessment.fromJson(Map<String, dynamic> json) {
    return PrakritiAssessment(
      dominantDosha: json['dominant_dosha'] as String? ?? 'tridoshaja',
      bodyFrame: json['body_frame'] as String? ?? 'medium_muscular',
      skinTexture: json['skin_texture'] as String? ?? 'smooth_oily_cool',
      digestionSpeed: json['digestion_speed'] as String? ?? 'slow_steady',
      weatherSensitivity: json['weather_sensitivity'] as String? ?? 'intolerant_to_cold',
      sleepPattern: json['sleep_pattern'] as String? ?? 'moderate_sound',
      namasteCode: json['namaste_code'] as String? ?? 'NAMASTE:PRAKRITI-001',
    );
  }

  Map<String, dynamic> toJson() => {
        'dominant_dosha': dominantDosha,
        'body_frame': bodyFrame,
        'skin_texture': skinTexture,
        'digestion_speed': digestionSpeed,
        'weather_sensitivity': weatherSensitivity,
        'sleep_pattern': sleepPattern,
        'namaste_code': namasteCode,
      };
}

class KoshthaAssessment {
  final String koshthaType; // krura | mridu | madhyama
  final String bowelFrequency;
  final String stoolConsistency;
  final String namasteCode;

  const KoshthaAssessment({
    required this.koshthaType,
    required this.bowelFrequency,
    required this.stoolConsistency,
    this.namasteCode = 'NAMASTE:KOSHTHA-001',
  });

  factory KoshthaAssessment.fromJson(Map<String, dynamic> json) {
    return KoshthaAssessment(
      koshthaType: json['koshtha_type'] as String? ?? 'madhyama',
      bowelFrequency: json['bowel_frequency'] as String? ?? 'once_daily',
      stoolConsistency: json['stool_consistency'] as String? ?? 'soft_formed',
      namasteCode: json['namaste_code'] as String? ?? 'NAMASTE:KOSHTHA-001',
    );
  }

  Map<String, dynamic> toJson() => {
        'koshtha_type': koshthaType,
        'bowel_frequency': bowelFrequency,
        'stool_consistency': stoolConsistency,
        'namaste_code': namasteCode,
      };
}

class AyurvedicIntakeRecord {
  final AgniAssessment? agni;
  final PrakritiAssessment? prakritiBaseline;
  final KoshthaAssessment? koshtha;
  final List<String> provisionalDoshaImbalance;

  const AyurvedicIntakeRecord({
    this.agni,
    this.prakritiBaseline,
    this.koshtha,
    this.provisionalDoshaImbalance = const [],
  });

  factory AyurvedicIntakeRecord.fromJson(Map<String, dynamic> json) {
    return AyurvedicIntakeRecord(
      agni: json['agni'] != null ? AgniAssessment.fromJson(json['agni'] as Map<String, dynamic>) : null,
      prakritiBaseline: json['prakriti_baseline'] != null
          ? PrakritiAssessment.fromJson(json['prakriti_baseline'] as Map<String, dynamic>)
          : null,
      koshtha: json['koshtha'] != null ? KoshthaAssessment.fromJson(json['koshtha'] as Map<String, dynamic>) : null,
      provisionalDoshaImbalance:
          (json['provisional_dosha_imbalance'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? const [],
    );
  }
}
