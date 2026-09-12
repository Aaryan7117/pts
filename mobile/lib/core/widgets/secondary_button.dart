import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';

/// 64dp Outline Secondary Button
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 7.6
class SecondaryActionButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  final Color? borderColor;
  final Color? textColor;
  final double height;

  const SecondaryActionButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.icon,
    this.borderColor,
    this.textColor,
    this.height = MediDimensions.secondaryCtaHeight,
  });

  @override
  Widget build(BuildContext context) {
    final bc = borderColor ?? MediColors.borderStrong;
    final tc = textColor ?? MediColors.textPrimary;

    return Semantics(
      button: true,
      enabled: onPressed != null,
      label: label,
      child: SizedBox(
        width: double.infinity,
        height: height,
        child: OutlinedButton(
          onPressed: onPressed,
          style: OutlinedButton.styleFrom(
            foregroundColor: tc,
            disabledForegroundColor: MediColors.textDisabled,
            side: BorderSide(color: bc, width: 1.5),
            shape: RoundedRectangleBorder(
              borderRadius: MediDimensions.borderMd,
            ),
            padding: const EdgeInsets.symmetric(horizontal: MediDimensions.space20),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null) ...[
                Icon(icon, size: 24, color: tc),
                const SizedBox(width: MediDimensions.space8),
              ],
              Flexible(
                child: Text(
                  label,
                  style: MediTypography.buttonMedium.copyWith(color: tc),
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
