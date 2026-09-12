import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';

enum NetworkStatus { online, edgeMode, offline }

/// Non-intrusive Offline / Edge Connectivity Banner
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 9.1
class OfflineBanner extends StatelessWidget {
  final NetworkStatus status;
  final VoidCallback? onRetry;

  const OfflineBanner({
    super.key,
    required this.status,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    if (status == NetworkStatus.online) return const SizedBox.shrink();

    final isEdge = status == NetworkStatus.edgeMode;
    final bgColor = isEdge ? MediColors.offlineBannerEdgeBg : MediColors.offlineBannerFullBg;
    final textColor = isEdge ? MediColors.offlineBannerEdgeText : MediColors.offlineBannerFullText;
    final icon = isEdge ? Icons.laptop_chromebook : Icons.cloud_off;
    final message = isEdge
        ? 'Edge Mode: Running on Local Hospital Station (Full Privacy)'
        : 'Offline Mode: Inputs are saved locally. Cloud features paused.';

    return Container(
      width: double.infinity,
      color: bgColor,
      padding: const EdgeInsets.symmetric(
        horizontal: MediDimensions.space16,
        vertical: MediDimensions.space8,
      ),
      child: Row(
        children: [
          Icon(icon, size: 20, color: textColor),
          const SizedBox(width: MediDimensions.space8),
          Expanded(
            child: Text(
              message,
              style: MediTypography.caption.copyWith(color: textColor, fontWeight: FontWeight.w600),
            ),
          ),
          if (onRetry != null && !isEdge)
            TextButton(
              onPressed: onRetry,
              style: TextButton.styleFrom(
                foregroundColor: textColor,
                padding: const EdgeInsets.symmetric(horizontal: 8),
              ),
              child: const Text('RETRY', style: TextStyle(fontWeight: FontWeight.w700)),
            ),
        ],
      ),
    );
  }
}
