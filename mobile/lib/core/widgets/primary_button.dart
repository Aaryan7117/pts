import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';

/// 72dp Oversized Primary CTA Button
/// Meets WCAG AAA 7:1 contrast ratio
/// High tactile target for elderly and low-literacy users
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 7.5
class PrimaryActionButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  final bool isLoading;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final double height;

  const PrimaryActionButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.icon,
    this.isLoading = false,
    this.backgroundColor,
    this.foregroundColor,
    this.height = MediDimensions.primaryCtaHeight,
  });

  @override
  Widget build(BuildContext context) {
    final bg = backgroundColor ?? MediColors.brandPrimary;
    final fg = foregroundColor ?? MediColors.white;

    return Semantics(
      button: true,
      enabled: onPressed != null && !isLoading,
      label: label,
      child: SizedBox(
        width: double.infinity,
        height: height,
        child: ElevatedButton(
          onPressed: isLoading ? null : onPressed,
          style: ElevatedButton.styleFrom(
            backgroundColor: bg,
            foregroundColor: fg,
            disabledBackgroundColor: MediColors.slate200,
            disabledForegroundColor: MediColors.slate400,
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: MediDimensions.borderXl,
            ),
            padding: const EdgeInsets.symmetric(horizontal: MediDimensions.space24),
          ),
          child: isLoading
              ? SizedBox(
                  width: 28,
                  height: 28,
                  child: CircularProgressIndicator(
                    strokeWidth: 3.0,
                    valueColor: AlwaysStoppedAnimation<Color>(fg),
                  ),
                )
              : Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (icon != null) ...[
                      Icon(icon, size: 28, color: fg),
                      const SizedBox(width: MediDimensions.space12),
                    ],
                    Flexible(
                      child: Text(
                        label,
                        style: MediTypography.buttonLarge.copyWith(color: fg),
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
