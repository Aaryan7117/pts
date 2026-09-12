/// Canonical Clinical Fact models mirroring app/schemas/clinical_fact.py
class SourceReference {
  final String type; // patient_voice | document_ocr | touch_input | explain_back_verified
  final String? documentId;
  final List<int>? lineIndices;
  final List<int>? bbox; // [x1, y1, x2, y2]
  final double? ocrConfidence;
  final String? rawText;
  final int? audioTimestampMs;

  const SourceReference({
    required this.type,
    this.documentId,
    this.lineIndices,
    this.bbox,
    this.ocrConfidence,
    this.rawText,
    this.audioTimestampMs,
  });

  factory SourceReference.fromJson(Map<String, dynamic> json) {
    return SourceReference(
      type: json['type'] as String? ?? 'touch_input',
      documentId: json['document_id'] as String?,
      lineIndices: (json['line_indices'] as List<dynamic>?)?.map((e) => e as int).toList(),
      bbox: (json['bbox'] as List<dynamic>?)?.map((e) => e as int).toList(),
      ocrConfidence: (json['ocr_confidence'] as num?)?.toDouble(),
      rawText: json['raw_text'] as String?,
      audioTimestampMs: json['audio_timestamp_ms'] as int?,
    );
  }

  Map<String, dynamic> toJson() => {
        'type': type,
        if (documentId != null) 'document_id': documentId,
        if (lineIndices != null) 'line_indices': lineIndices,
        if (bbox != null) 'bbox': bbox,
        if (ocrConfidence != null) 'ocr_confidence': ocrConfidence,
        if (rawText != null) 'raw_text': rawText,
        if (audioTimestampMs != null) 'audio_timestamp_ms': audioTimestampMs,
      };
}

class ConfidenceBreakdown {
  final double tierScore;
  final double inputQuality;
  final double completeness;

  const ConfidenceBreakdown({
    this.tierScore = 1.0,
    this.inputQuality = 1.0,
    this.completeness = 1.0,
  });

  factory ConfidenceBreakdown.fromJson(Map<String, dynamic> json) {
    return ConfidenceBreakdown(
      tierScore: (json['tier_score'] as num?)?.toDouble() ?? 1.0,
      inputQuality: (json['input_quality'] as num?)?.toDouble() ?? 1.0,
      completeness: (json['completeness'] as num?)?.toDouble() ?? 1.0,
    );
  }
}

class ClinicalFact {
  final String id;
  final String encounterId;
  final String category; // chief_complaint | symptom | medication | allergy | vital | lab_result | ayush_*
  final String field;
  final String value;
  final String? dose;
  final String? frequency;
  final String? patientWords;
  final String? normalizedConcept;
  final String? conceptCode; // SNOMED:xxxxx or NAMASTE:xxxxx
  final String provenanceTier; // TOUCH | LOOKUP | EMBEDDING | LLM | OCR
  final String? sourceType;
  final SourceReference? sourceReference;
  final double confidence;
  final ConfidenceBreakdown? confidenceBreakdown;
  final String? temporalState; // prescribed | taking | stopped | dose_changed
  final String? validFrom;
  final String? validUntil;
  final bool isNegated;
  final String status; // pending | patient_confirmed | explain_back_verified | doctor_reviewed

  const ClinicalFact({
    required this.id,
    required this.encounterId,
    required this.category,
    required this.field,
    required this.value,
    this.dose,
    this.frequency,
    this.patientWords,
    this.normalizedConcept,
    this.conceptCode,
    this.provenanceTier = 'TOUCH',
    this.sourceType = 'touch_input',
    this.sourceReference,
    this.confidence = 1.0,
    this.confidenceBreakdown,
    this.temporalState,
    this.validFrom,
    this.validUntil,
    this.isNegated = false,
    this.status = 'pending',
  });

  String get confidenceTier {
    if (confidence >= 0.85) return 'HIGH';
    if (confidence >= 0.55) return 'MEDIUM';
    return 'LOW_REFUSE';
  }

  factory ClinicalFact.fromJson(Map<String, dynamic> json) {
    return ClinicalFact(
      id: json['id'] as String? ?? '',
      encounterId: json['encounter_id'] as String? ?? '',
      category: json['category'] as String? ?? 'symptom',
      field: json['field'] as String? ?? '',
      value: json['value'] as String? ?? '',
      dose: json['dose'] as String?,
      frequency: json['frequency'] as String?,
      patientWords: json['patient_words'] as String?,
      normalizedConcept: json['normalized_concept'] as String?,
      conceptCode: json['concept_code'] as String?,
      provenanceTier: json['provenance_tier'] as String? ?? 'TOUCH',
      sourceType: json['source_type'] as String?,
      sourceReference: json['source_reference'] != null
          ? SourceReference.fromJson(json['source_reference'] as Map<String, dynamic>)
          : null,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 1.0,
      confidenceBreakdown: json['confidence_breakdown'] != null
          ? ConfidenceBreakdown.fromJson(json['confidence_breakdown'] as Map<String, dynamic>)
          : null,
      temporalState: json['temporal_state'] as String?,
      validFrom: json['valid_from'] as String?,
      validUntil: json['valid_until'] as String?,
      isNegated: json['is_negated'] as bool? ?? (json['is_negated'] == 1),
      status: json['status'] as String? ?? 'pending',
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'encounter_id': encounterId,
        'category': category,
        'field': field,
        'value': value,
        if (dose != null) 'dose': dose,
        if (frequency != null) 'frequency': frequency,
        if (patientWords != null) 'patient_words': patientWords,
        if (normalizedConcept != null) 'normalized_concept': normalizedConcept,
        if (conceptCode != null) 'concept_code': conceptCode,
        'provenance_tier': provenanceTier,
        if (sourceType != null) 'source_type': sourceType,
        if (sourceReference != null) 'source_reference': sourceReference!.toJson(),
        'confidence': confidence,
        if (temporalState != null) 'temporal_state': temporalState,
        if (validFrom != null) 'valid_from': validFrom,
        if (validUntil != null) 'valid_until': validUntil,
        'is_negated': isNegated,
        'status': status,
      };
}
