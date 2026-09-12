import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';
import '../../core/widgets/secondary_button.dart';

/// Screen 03 — Patient Consent & Privacy Notice
/// Plain-language terms with Audio Explanation CTA
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 03)
class ConsentScreen extends StatefulWidget {
  const ConsentScreen({super.key});

  @override
  State<ConsentScreen> createState() => _ConsentScreenState();
}

class _ConsentScreenState extends State<ConsentScreen> {
  bool _isPlayingAudio = false;

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();

    return MediScaffold(
      title: 'Consent & Privacy',
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              lang.translate('consent_title'),
              style: MediTypography.headlineLarge,
            ),
            const SizedBox(height: MediDimensions.space16),

            // Audio Explanation Card
            Container(
              padding: const EdgeInsets.all(MediDimensions.space16),
              decoration: BoxDecoration(
                color: MediColors.blue50,
                borderRadius: MediDimensions.borderLg,
                border: Border.all(color: MediColors.blue200),
              ),
              child: Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: const BoxDecoration(
                      color: MediColors.brandPrimary,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      _isPlayingAudio ? Icons.volume_up : Icons.play_arrow_rounded,
                      color: MediColors.white,
                      size: 28,
                    ),
                  ),
                  const SizedBox(width: MediDimensions.space16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Audio Explanation (सुनें)',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w700,
                            color: MediColors.brandPrimary,
                          ),
                        ),
                        Text(
                          _isPlayingAudio ? 'Playing notice in your language...' : 'Tap to hear privacy terms aloud',
                          style: MediTypography.bodyMedium.copyWith(fontSize: 15),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: () {
                      setState(() {
                        _isPlayingAudio = !_isPlayingAudio;
                      });
                    },
                    icon: Icon(_isPlayingAudio ? Icons.pause_circle_filled : Icons.play_circle_fill),
                    iconSize: 40,
                    color: MediColors.brandPrimary,
                  ),
                ],
              ),
            ),

            const SizedBox(height: MediDimensions.space24),

            // Consent Body Card
            Container(
              padding: const EdgeInsets.all(MediDimensions.space20),
              decoration: BoxDecoration(
                color: MediColors.surface,
                borderRadius: MediDimensions.borderLg,
                border: Border.all(color: MediColors.border),
                boxShadow: MediDimensions.elevation1,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    lang.translate('consent_body'),
                    style: MediTypography.bodyLarge.copyWith(height: 1.45),
                  ),
                  const SizedBox(height: MediDimensions.space20),
                  _buildBullet(
                    Icons.lock_rounded,
                    'Protected under Digital Personal Data Protection (DPDP) Act.',
                  ),
                  _buildBullet(
                    Icons.medical_services_rounded,
                    'Used only by your attending OPD doctor during this visit.',
                  ),
                  _buildBullet(
                    Icons.auto_delete_rounded,
                    'Audio recordings and raw documents are automatically purged.',
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
            label: lang.translate('agree_continue'),
            icon: Icons.check_circle_outline,
            onPressed: () => Navigator.of(context).pushNamed('/identity'),
          ),
          const SizedBox(height: MediDimensions.space12),
          SecondaryActionButton(
            label: 'Decline & Exit (अस्वीकार)',
            onPressed: () => Navigator.of(context).popUntil((route) => route.isFirst),
          ),
        ],
      ),
    );
  }

  Widget _buildBullet(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: MediDimensions.space12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 22, color: MediColors.emerald800),
          const SizedBox(width: MediDimensions.space12),
          Expanded(
            child: Text(
              text,
              style: MediTypography.bodyMedium.copyWith(color: MediColors.textPrimary),
            ),
          ),
        ],
      ),
    );
  }
}
