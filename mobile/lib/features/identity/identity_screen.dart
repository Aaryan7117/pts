import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';
import '../../core/widgets/secondary_button.dart';

/// Screen 04 — Patient Identification
/// ABHA QR Scan, 10-Digit Mobile, or Guest Bypass
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 04)
class IdentityScreen extends StatefulWidget {
  const IdentityScreen({super.key});

  @override
  State<IdentityScreen> createState() => _IdentityScreenState();
}

class _IdentityScreenState extends State<IdentityScreen> {
  final TextEditingController _phoneController = TextEditingController();

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();

    return MediScaffold(
      title: lang.translate('identify_title'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              lang.translate('identify_title'),
              style: MediTypography.headlineLarge,
            ),
            const SizedBox(height: MediDimensions.space8),
            Text(
              lang.translate('identify_sub'),
              style: MediTypography.bodyMedium,
            ),
            const SizedBox(height: MediDimensions.space24),

            // Option 1: ABHA QR Scan Card
            Container(
              padding: const EdgeInsets.all(MediDimensions.space20),
              decoration: BoxDecoration(
                color: MediColors.surface,
                borderRadius: MediDimensions.borderLg,
                border: Border.all(color: MediColors.border, width: 1.5),
                boxShadow: MediDimensions.elevation1,
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          color: MediColors.blue50,
                          borderRadius: MediDimensions.borderMd,
                        ),
                        child: const Icon(Icons.qr_code_scanner, size: 28, color: MediColors.brandPrimary),
                      ),
                      const SizedBox(width: MediDimensions.space16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              lang.translate('scan_abha'),
                              style: MediTypography.headlineMedium.copyWith(fontSize: 19),
                            ),
                            Text(
                              lang.translate('hold_card_camera'),
                              style: const TextStyle(fontSize: 14, color: MediColors.textMuted),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: MediDimensions.space16),
                  SizedBox(
                    height: 52,
                    child: OutlinedButton.icon(
                      onPressed: () {
                        // Simulated QR Scan Success
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('ABHA Card Recognized: 91-4821-3910-4819')),
                        );
                        Navigator.of(context).pushNamed('/care_stream');
                      },
                      icon: const Icon(Icons.camera_alt),
                      label: Text(lang.translate('open_qr_scanner')),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: MediDimensions.space20),

            // Option 2: Mobile Number Input Card
            Container(
              padding: const EdgeInsets.all(MediDimensions.space20),
              decoration: BoxDecoration(
                color: MediColors.surface,
                borderRadius: MediDimensions.borderLg,
                border: Border.all(color: MediColors.border, width: 1.5),
                boxShadow: MediDimensions.elevation1,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    lang.translate('enter_mobile'),
                    style: MediTypography.headlineMedium.copyWith(fontSize: 18),
                  ),
                  const SizedBox(height: MediDimensions.space12),
                  TextField(
                    controller: _phoneController,
                    keyboardType: TextInputType.phone,
                    maxLength: 10,
                    style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w600, letterSpacing: 2.0),
                    decoration: InputDecoration(
                      prefixText: '+91 ',
                      prefixStyle: const TextStyle(fontSize: 22, fontWeight: FontWeight.w600, color: MediColors.textMuted),
                      hintText: '98765 43210',
                      border: OutlineInputBorder(
                        borderRadius: MediDimensions.borderMd,
                        borderSide: const BorderSide(color: MediColors.borderStrong),
                      ),
                      filled: true,
                      fillColor: MediColors.slate100,
                    ),
                  ),
                  const SizedBox(height: MediDimensions.space8),
                  PrimaryActionButton(
                    label: lang.translate('verify_phone'),
                    height: 54,
                    onPressed: () => Navigator.of(context).pushNamed('/care_stream'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomBar: SecondaryActionButton(
        label: lang.translate('skip_identify'),
        icon: Icons.person_off_outlined,
        onPressed: () => Navigator.of(context).pushNamed('/care_stream'),
      ),
    );
  }
}
