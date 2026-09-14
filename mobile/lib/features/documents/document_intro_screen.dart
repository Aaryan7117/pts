import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';
import '../../core/widgets/secondary_button.dart';

/// Screen 12 — Document Intro
/// Encourages scanning prior prescriptions and lab reports
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 12)
class DocumentIntroScreen extends StatelessWidget {
  const DocumentIntroScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();

    return MediScaffold(
      title: lang.translate('doc_scan_title'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
          Container(
            width: 96,
            height: 96,
            decoration: BoxDecoration(
              color: MediColors.blue50,
              borderRadius: MediDimensions.borderXl,
            ),
            child: const Icon(
              Icons.document_scanner_rounded,
              size: 56,
              color: MediColors.brandPrimary,
            ),
          ),
          const SizedBox(height: MediDimensions.space24),
          Text(
            lang.translate('doc_scan_title'),
            style: MediTypography.headlineLarge,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: MediDimensions.space12),
          Text(
            lang.translate('doc_scan_sub'),
            style: MediTypography.bodyMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: MediDimensions.space32),
          Container(
            padding: const EdgeInsets.all(MediDimensions.space16),
            decoration: BoxDecoration(
              color: MediColors.surface,
              borderRadius: MediDimensions.borderLg,
              border: Border.all(color: MediColors.border),
            ),
            child: Column(
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.check, color: MediColors.emerald800),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(lang.translate('doc_prescription_check'), style: const TextStyle(fontWeight: FontWeight.w600)),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.check, color: MediColors.emerald800),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(lang.translate('doc_lab_check'), style: const TextStyle(fontWeight: FontWeight.w600)),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.check, color: MediColors.emerald800),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(lang.translate('doc_discharge_check'), style: const TextStyle(fontWeight: FontWeight.w600)),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    ),
    bottomBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          PrimaryActionButton(
            label: lang.translate('scan_doc_btn'),
            icon: Icons.camera_alt_rounded,
            onPressed: () => Navigator.of(context).pushNamed('/doc_camera'),
          ),
          const SizedBox(height: MediDimensions.space12),
          SecondaryActionButton(
            label: lang.translate('no_doc_btn'),
            onPressed: () => Navigator.of(context).pushNamed('/vitals'),
          ),
        ],
      ),
    );
  }
}
