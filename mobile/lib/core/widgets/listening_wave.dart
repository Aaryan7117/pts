import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';

/// 9-Bar Animated Audio Waveform Visualizer
/// Strictly constrained bounding box to prevent parent layout shifts/jitter
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 6.2 & 7.9 & Screen 07
class ListeningWave extends StatefulWidget {
  final bool isActive;
  final Color color;
  final double height;
  final int barCount;

  const ListeningWave({
    super.key,
    this.isActive = true,
    this.color = MediColors.brandPrimary,
    this.height = 56.0,
    this.barCount = 9,
  });

  @override
  State<ListeningWave> createState() => _ListeningWaveState();
}

class _ListeningWaveState extends State<ListeningWave>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  // 9-Bar relative height profiles per clinical spec
  static const List<double> _baseMultipliers = [
    0.35, 0.55, 0.8, 0.95, 1.0, 0.9, 0.75, 0.5, 0.35
  ];

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );

    if (widget.isActive) {
      _controller.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(ListeningWave oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isActive && !_controller.isAnimating) {
      _controller.repeat(reverse: true);
    } else if (!widget.isActive && _controller.isAnimating) {
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
    return SizedBox(
      height: widget.height,
      width: double.infinity,
      child: Center(
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            final count = widget.barCount.clamp(5, 9);
            return Row(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: List.generate(count, (index) {
                final offset = index / count;
                final t = (_controller.value + offset) % 1.0;
                final sine = math.sin(t * math.pi);
                final dynamicMultiplier = widget.isActive ? (0.25 + 0.75 * sine) : 0.2;
                final multiplier = _baseMultipliers[index % _baseMultipliers.length];
                final barHeight = (widget.height * multiplier * dynamicMultiplier)
                    .clamp(8.0, widget.height);

                return Container(
                  margin: const EdgeInsets.symmetric(horizontal: MediDimensions.space4),
                  width: 6.0,
                  height: barHeight,
                  decoration: BoxDecoration(
                    color: widget.color,
                    borderRadius: MediDimensions.borderFull,
                  ),
                );
              }),
            );
          },
        ),
      ),
    );
  }
}
