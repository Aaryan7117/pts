import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';

/// 100dp Pulsing Voice Button with Animated Ripple Halo
/// Supports Idle and Active Listening states
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 6.2 & 7.8
class VoiceButton extends StatefulWidget {
  final bool isListening;
  final VoidCallback onTap;
  final String? label;
  final double size;

  const VoiceButton({
    super.key,
    required this.isListening,
    required this.onTap,
    this.label,
    this.size = MediDimensions.voiceButtonSize,
  });

  @override
  State<VoiceButton> createState() => _VoiceButtonState();
}

class _VoiceButtonState extends State<VoiceButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _haloAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    );

    _haloAnimation = Tween<double>(begin: 1.0, end: 1.35).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutQuad),
    );

    if (widget.isListening) {
      _controller.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(VoiceButton oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isListening && !_controller.isAnimating) {
      _controller.repeat(reverse: true);
    } else if (!widget.isListening && _controller.isAnimating) {
      _controller.stop();
      _controller.reset();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final activeColor =
        widget.isListening ? MediColors.voiceBtnListening : MediColors.voiceBtnIdle;
    final haloColor =
        widget.isListening ? MediColors.voiceHaloListening : MediColors.voiceHaloIdle;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Semantics(
          button: true,
          label: widget.isListening ? 'Stop listening' : 'Start speaking',
          child: GestureDetector(
            onTap: widget.onTap,
            child: SizedBox(
              width: widget.size * 1.5,
              height: widget.size * 1.5,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Animated Pulsing Halo
                  AnimatedBuilder(
                    animation: _controller,
                    builder: (context, child) {
                      final scale = widget.isListening ? _haloAnimation.value : 1.0;
                      return Transform.scale(
                        scale: scale,
                        child: Container(
                          width: widget.size + 24,
                          height: widget.size + 24,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: haloColor,
                          ),
                        ),
                      );
                    },
                  ),
                  // Core Microphone Circle
                  Container(
                    width: widget.size,
                    height: widget.size,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: activeColor,
                      boxShadow: widget.isListening
                          ? MediDimensions.emergencyGlow
                          : MediDimensions.voiceGlow,
                    ),
                    child: Icon(
                      widget.isListening ? Icons.mic : Icons.mic_none,
                      size: 48,
                      color: MediColors.white,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        if (widget.label != null) ...[
          const SizedBox(height: MediDimensions.space12),
          Text(
            widget.label!,
            style: MediTypography.headlineMedium.copyWith(
              fontSize: 20,
              color: widget.isListening ? MediColors.triageRed : MediColors.textPrimary,
              fontWeight: FontWeight.w600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ],
    );
  }
}
