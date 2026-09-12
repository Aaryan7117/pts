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
      title: 'Scan Medical Documents',
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
            'Scanning your previous prescriptions allows our AI to extract medication history and alert your doctor of drug interactions.',
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
            child: const Column(
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.check, color: MediColors.emerald800),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text('Doctor prescriptions (डॉक्टर की पर्ची)', style: TextStyle(fontWeight: FontWeight.w600)),
                    ),
                  ],
                ),
                SizedBox(height: 10),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.check, color: MediColors.emerald800),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text('Blood & urine lab reports (जाँच रिपोर्ट)', style: TextStyle(fontWeight: FontWeight.w600)),
                    ),
                  ],
                ),
                SizedBox(height: 10),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.check, color: MediColors.emerald800),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text('Hospital discharge summaries (डिस्चार्ज समरी)', style: TextStyle(fontWeight: FontWeight.w600)),
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
            label: 'Scan Document (पर्ची स्कैन करें)',
            icon: Icons.camera_alt_rounded,
            onPressed: () => Navigator.of(context).pushNamed('/doc_camera'),
          ),
          const SizedBox(height: MediDimensions.space12),
          SecondaryActionButton(
            label: "I Don't Have Documents (पर्ची नहीं है / आगे बढ़ें)",
            onPressed: () => Navigator.of(context).pushNamed('/vitals'),
          ),
        ],
      ),
    );
  }
}
