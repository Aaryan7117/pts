/// Canonical Document & OCR models mirroring app/schemas/document.py
class ExtractedMedication {
  final String name;
  final String? dose;
  final String? frequency;
  final List<int> sourceLines;
  final List<int>? box2d; // [ymin, xmin, ymax, xmax] normalized 0-1000
  final double confidence;

  const ExtractedMedication({
    required this.name,
    this.dose,
    this.frequency,
    this.sourceLines = const [],
    this.box2d,
    this.confidence = 0.9,
  });

  factory ExtractedMedication.fromJson(Map<String, dynamic> json) {
    return ExtractedMedication(
      name: json['name'] as String? ?? '',
      dose: json['dose'] as String?,
      frequency: json['frequency'] as String?,
      sourceLines: (json['source_lines'] as List<dynamic>?)?.map((e) => e as int).toList() ?? const [],
      box2d: (json['box_2d'] as List<dynamic>?)?.map((e) => e as int).toList(),
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.9,
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        if (dose != null) 'dose': dose,
        if (frequency != null) 'frequency': frequency,
        'source_lines': sourceLines,
        if (box2d != null) 'box_2d': box2d,
        'confidence': confidence,
      };
}

class DocumentUploadResponse {
  final String documentId;
  final String ocrStatus; // SUCCESS | LOW_CONFIDENCE | FAILED
  final List<ExtractedMedication> extractedMedications;
  final List<String> flaggedInteractions;
  final String? highlightedImageUrl;
  final String? rawOcrText;
  final double overallOcrConfidence;

  const DocumentUploadResponse({
    required this.documentId,
    required this.ocrStatus,
    this.extractedMedications = const [],
    this.flaggedInteractions = const [],
    this.highlightedImageUrl,
    this.rawOcrText,
    this.overallOcrConfidence = 0.0,
  });

  factory DocumentUploadResponse.fromJson(Map<String, dynamic> json) {
    return DocumentUploadResponse(
      documentId: json['document_id'] as String? ?? '',
      ocrStatus: json['ocr_status'] as String? ?? 'SUCCESS',
      extractedMedications: (json['extracted_medications'] as List<dynamic>?)
              ?.map((e) => ExtractedMedication.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      flaggedInteractions: (json['flagged_interactions'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
      highlightedImageUrl: json['highlighted_image_url'] as String?,
      rawOcrText: json['raw_ocr_text'] as String?,
      overallOcrConfidence: (json['overall_ocr_confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class OCRLine {
  final int lineIndex;
  final String text;
  final List<int> bbox; // [x1, y1, x2, y2]
  final double confidence;

  const OCRLine({
    required this.lineIndex,
    required this.text,
    required this.bbox,
    required this.confidence,
  });

  factory OCRLine.fromJson(Map<String, dynamic> json) {
    return OCRLine(
      lineIndex: json['line_index'] as int? ?? 0,
      text: json['text'] as String? ?? '',
      bbox: (json['bbox'] as List<dynamic>?)?.map((e) => e as int).toList() ?? const [0, 0, 0, 0],
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
