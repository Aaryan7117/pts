import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/intake_provider.dart';
import '../../data/datasources/api_datasource.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 16 — Source Document View with Evidence Polygons
/// "No Receipt, No Fact" visual provenance verification
/// Displays the actual uploaded prescription image or locally captured camera photo.
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 16)
class SourceDocumentScreen extends StatelessWidget {
  const SourceDocumentScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final intake = context.watch<IntakeProvider>();
    final rawUrl = intake.lastDocumentResult?.highlightedImageUrl;
    String? liveImageUrl;
    if (rawUrl != null && rawUrl.isNotEmpty) {
      if (rawUrl.startsWith('http')) {
        liveImageUrl = rawUrl.replaceFirst('http://localhost:8000', ApiDataSource.defaultBaseUrl);
      } else {
        final path = rawUrl.startsWith('/') ? rawUrl : '/$rawUrl';
        liveImageUrl = '${ApiDataSource.defaultBaseUrl}$path';
      }
    }

    return MediScaffold(
      title: 'Original Prescription',
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Visual Evidence Grounding',
            style: MediTypography.headlineLarge,
          ),
          const SizedBox(height: MediDimensions.space8),
          const Text(
            'The highlighted area shows the exact region where AI extracted your medication from the original document.',
            style: TextStyle(fontSize: 16, color: MediColors.textMuted),
          ),
          const SizedBox(height: MediDimensions.space20),
          Expanded(
            child: InteractiveViewer(
              minScale: 0.8,
              maxScale: 3.5,
              child: Center(
                child: _buildDocumentViewer(context, intake, liveImageUrl),
              ),
            ),
          ),
        ],
      ),
      bottomBar: PrimaryActionButton(
        label: 'Back to Medications (वापस जाएं)',
        onPressed: () => Navigator.of(context).pop(),
      ),
    );
  }

  Widget _buildDocumentViewer(BuildContext context, IntakeProvider intake, String? liveImageUrl) {
    // 1. If backend returned a valid image URL, stream it
    if (liveImageUrl != null && liveImageUrl.isNotEmpty) {
      return ClipRRect(
        borderRadius: MediDimensions.borderMd,
        child: Image.network(
          liveImageUrl,
          fit: BoxFit.contain,
          loadingBuilder: (ctx, child, progress) {
            if (progress == null) return child;
            return const Center(child: CircularProgressIndicator());
          },
          errorBuilder: (ctx, err, stack) => _buildLocalFallbackImage(intake),
        ),
      );
    }

    return _buildLocalFallbackImage(intake);
  }

  Widget _buildLocalFallbackImage(IntakeProvider intake) {
    // 2. Fall back to local file path captured by camera
    if (intake.capturedImagePath != null && File(intake.capturedImagePath!).existsSync()) {
      return ClipRRect(
        borderRadius: MediDimensions.borderMd,
        child: Image.file(
          File(intake.capturedImagePath!),
          fit: BoxFit.contain,
        ),
      );
    }

    // 3. Fall back to memory bytes if retained
    if (intake.capturedImageBytes != null && intake.capturedImageBytes!.isNotEmpty) {
      return ClipRRect(
        borderRadius: MediDimensions.borderMd,
        child: Image.memory(
          Uint8List.fromList(intake.capturedImageBytes!),
          fit: BoxFit.contain,
        ),
      );
    }

    // 4. Honest empty state (Zero mockups!)
    return Container(
      width: 320,
      padding: const EdgeInsets.all(MediDimensions.space24),
      decoration: BoxDecoration(
        color: MediColors.surface,
        borderRadius: MediDimensions.borderMd,
        border: Border.all(color: MediColors.border),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.image_not_supported_outlined, size: 56, color: MediColors.slate400),
          const SizedBox(height: MediDimensions.space16),
          const Text(
            'No Source Image Available',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: MediColors.textPrimary),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: MediDimensions.space8),
          const Text(
            'Please scan or take a photo of your prescription to inspect the visual evidence.',
            style: TextStyle(fontSize: 14, color: MediColors.textMuted),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
