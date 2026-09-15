import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../data/models/encounter.dart';

/// Unified Hospital Header for Patient and Kiosk Screens
/// Features Medical Cross mark, Language Switcher, and SOS Shortcut
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 5.2 & 7.2
class MediHeader extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final bool showBack;
  final VoidCallback? onBack;
  final String currentLanguage;
  final ValueChanged<String>? onLanguageChanged;
  final VoidCallback? onEmergencyTap;
  final String? tokenNumber;

  const MediHeader({
    super.key,
    this.title = 'MediKiosk',
    this.showBack = true,
    this.onBack,
    this.currentLanguage = 'hi',
    this.onLanguageChanged,
    this.onEmergencyTap,
    this.tokenNumber,
  });

  @override
  Size get preferredSize => const Size.fromHeight(68.0);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 68.0,
      decoration: const BoxDecoration(
        color: MediColors.surface,
        border: Border(bottom: BorderSide(color: MediColors.border, width: 1.0)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: MediDimensions.space16),
      child: Row(
        children: [
          if (showBack && onBack != null)
            IconButton(
              icon: const Icon(Icons.arrow_back, size: 28, color: MediColors.textPrimary),
              onPressed: onBack,
              tooltip: 'Back',
            )
          else ...[
            // MediKiosk Brand Mark (Official Website Logo)
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: MediColors.white,
                borderRadius: MediDimensions.borderMd,
                border: Border.all(color: MediColors.border, width: 1.0),
              ),
              padding: const EdgeInsets.all(4.0),
              child: Image.asset(
                'assets/images/medikiosk-mark.png',
                fit: BoxFit.contain,
                errorBuilder: (context, error, stackTrace) => const Icon(
                  Icons.local_hospital_rounded,
                  color: MediColors.brandPrimary,
                  size: 24,
                ),
              ),
            ),
            const SizedBox(width: MediDimensions.space12),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  title,
                  style: MediTypography.headlineMedium.copyWith(fontSize: 20, fontWeight: FontWeight.w700),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                if (tokenNumber != null)
                  Text(
                    'Token: $tokenNumber',
                    style: const TextStyle(
                      color: MediColors.brandPrimary,
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
              ],
            ),
          ),
          // Language Switcher Dropdown
          if (onLanguageChanged != null)
            Container(
              height: 40,
              padding: const EdgeInsets.symmetric(horizontal: 10),
              decoration: BoxDecoration(
                color: MediColors.slate100,
                borderRadius: MediDimensions.borderMd,
                border: Border.all(color: MediColors.border),
              ),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  value: currentLanguage,
                  icon: const Icon(Icons.language, size: 20, color: MediColors.textPrimary),
                  items: kSupportedLanguages.map((lang) {
                    return DropdownMenuItem<String>(
                      value: lang.code,
                      child: Text(
                        lang.label,
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: MediColors.textPrimary,
                        ),
                      ),
                    );
                  }).toList(),
                  onChanged: (val) {
                    if (val != null) onLanguageChanged!(val);
                  },
                ),
              ),
            ),
          const SizedBox(width: MediDimensions.space8),
          // SOS Emergency Shortcut
          if (onEmergencyTap != null)
            IconButton.filled(
              onPressed: onEmergencyTap,
              icon: const Icon(Icons.emergency, color: MediColors.white, size: 22),
              style: IconButton.styleFrom(
                backgroundColor: MediColors.triageRed,
                padding: const EdgeInsets.all(8),
              ),
              tooltip: 'Emergency SOS',
            ),
        ],
      ),
    );
  }
}
