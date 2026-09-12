import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';

/// Tactile Choice Card with Radio / Selection Indicator
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 7.7
class LargeChoiceCard extends StatelessWidget {
  final String title;
  final String? subtitle;
  final IconData? icon;
  final bool isSelected;
  final VoidCallback onTap;
  final Widget? trailing;

  const LargeChoiceCard({
    super.key,
    required this.title,
    this.subtitle,
    this.icon,
    required this.isSelected,
    required this.onTap,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    final bgColor = isSelected ? MediColors.choiceCardSelectedBg : MediColors.surface;
    final borderColor = isSelected ? MediColors.choiceCardSelectedBorder : MediColors.border;
    final borderWidth = isSelected ? 2.5 : 1.5;

    return Semantics(
      selected: isSelected,
      button: true,
      label: '$title ${subtitle ?? ''}',
      child: Material(
        color: bgColor,
        borderRadius: MediDimensions.borderLg,
        child: InkWell(
          onTap: onTap,
          borderRadius: MediDimensions.borderLg,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 180),
            curve: Curves.easeInOut,
            constraints: const BoxConstraints(minHeight: MediDimensions.choiceCardMinHeight),
            padding: const EdgeInsets.all(MediDimensions.space20),
            decoration: BoxDecoration(
              color: bgColor,
              borderRadius: MediDimensions.borderLg,
              border: Border.all(color: borderColor, width: borderWidth),
              boxShadow: isSelected ? MediDimensions.elevation2 : MediDimensions.elevation1,
            ),
            child: Row(
              children: [
                if (icon != null) ...[
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: isSelected ? MediColors.blue100 : MediColors.slate100,
                      borderRadius: MediDimensions.borderMd,
                    ),
                    child: Icon(
                      icon,
                      size: 28,
                      color: isSelected ? MediColors.brandPrimary : MediColors.textPrimary,
                    ),
                  ),
                  const SizedBox(width: MediDimensions.space16),
                ],
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        title,
                        style: MediTypography.headlineMedium.copyWith(
                          fontSize: 20,
                          color: isSelected ? MediColors.brandPrimary : MediColors.textPrimary,
                          fontWeight: isSelected ? FontWeight.w700 : FontWeight.w600,
                        ),
                      ),
                      if (subtitle != null) ...[
                        const SizedBox(height: MediDimensions.space4),
                        Text(
                          subtitle!,
                          style: MediTypography.bodyMedium.copyWith(fontSize: 16),
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(width: MediDimensions.space12),
                trailing ??
                    Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: isSelected ? MediColors.brandPrimary : MediColors.slate400,
                          width: 2.0,
                        ),
                        color: isSelected ? MediColors.brandPrimary : Colors.transparent,
                      ),
                      child: isSelected
                          ? const Icon(Icons.check, size: 20, color: MediColors.white)
                          : null,
                    ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
