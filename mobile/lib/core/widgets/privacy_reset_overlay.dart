import 'dart:async';
import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';

/// 10-Second Automatic Privacy Session Purge Modal Overlay
/// Protects sensitive patient information from the next patient in queue
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 9.3 & Screen 24
class PrivacyResetOverlay extends StatefulWidget {
  final VoidCallback onReset;
  final VoidCallback? onCancel;
  final int countdownSeconds;

  const PrivacyResetOverlay({
    super.key,
    required this.onReset,
    this.onCancel,
    this.countdownSeconds = 10,
  });

  @override
  State<PrivacyResetOverlay> createState() => _PrivacyResetOverlayState();
}

class _PrivacyResetOverlayState extends State<PrivacyResetOverlay> {
  late int _secondsRemaining;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _secondsRemaining = widget.countdownSeconds;
    _startTimer();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_secondsRemaining > 1) {
        setState(() {
          _secondsRemaining--;
        });
      } else {
        _timer?.cancel();
        widget.onReset();
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final progress = _secondsRemaining / widget.countdownSeconds;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(MediDimensions.space24),
      decoration: BoxDecoration(
        color: MediColors.surface,
        borderRadius: MediDimensions.borderLg,
        border: Border.all(color: MediColors.borderStrong, width: 2),
        boxShadow: MediDimensions.elevation3,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(MediDimensions.space16),
            decoration: BoxDecoration(
              color: MediColors.blue50,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.lock_reset, size: 40, color: MediColors.brandPrimary),
          ),
          const SizedBox(height: MediDimensions.space16),
          Text(
            'Session Privacy Auto-Reset',
            style: MediTypography.headlineMedium.copyWith(fontSize: 22),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: MediDimensions.space8),
          Text(
            'To protect your health data, all information will be cleared from this screen in $_secondsRemaining seconds.',
            style: MediTypography.bodyMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: MediDimensions.space20),
          ClipRRect(
            borderRadius: MediDimensions.borderFull,
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 8,
              backgroundColor: MediColors.slate200,
              valueColor: const AlwaysStoppedAnimation<Color>(MediColors.brandPrimary),
            ),
          ),
          const SizedBox(height: MediDimensions.space24),
          Row(
            children: [
              Expanded(
                child: SizedBox(
                  height: 52,
                  child: ElevatedButton(
                    onPressed: () {
                      _timer?.cancel();
                      widget.onReset();
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: MediColors.slate900,
                      foregroundColor: MediColors.white,
                      shape: RoundedRectangleBorder(borderRadius: MediDimensions.borderMd),
                    ),
                    child: const Text('Reset Now (समाप्त)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                  ),
                ),
              ),
              if (widget.onCancel != null) ...[
                const SizedBox(width: MediDimensions.space12),
                Expanded(
                  child: SizedBox(
                    height: 52,
                    child: OutlinedButton(
                      onPressed: () {
                        _timer?.cancel();
                        widget.onCancel!();
                      },
                      style: OutlinedButton.styleFrom(
                        foregroundColor: MediColors.textPrimary,
                        side: const BorderSide(color: MediColors.borderStrong, width: 1.5),
                        shape: RoundedRectangleBorder(borderRadius: MediDimensions.borderMd),
                      ),
                      child: const Text('Keep Open', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}
