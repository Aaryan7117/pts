import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import 'listening_wave.dart';

/// Screen A-06B Active Conversational Voice Call Surface
/// Simulation card for voice-session intake loop
/// Ref: MEDIKIOSK_SINGLE_DEVELOPER_FULL_ANTIGRAVITY_MASTER Section 62
class ActiveCallCard extends StatelessWidget {
  final String durationText;
  final String transcript;
  final List<String> activeSymptoms;
  final bool isListening;
  final VoidCallback onEndCall;
  final VoidCallback? onToggleMute;
  final VoidCallback? onToggleSpeaker;
  final bool isMuted;
  final bool isSpeakerOn;

  const ActiveCallCard({
    super.key,
    required this.durationText,
    required this.transcript,
    this.activeSymptoms = const [],
    this.isListening = true,
    required this.onEndCall,
    this.onToggleMute,
    this.onToggleSpeaker,
    this.isMuted = false,
    this.isSpeakerOn = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(MediDimensions.space24),
      decoration: BoxDecoration(
        color: MediColors.brandDark,
        borderRadius: MediDimensions.borderXl,
        boxShadow: MediDimensions.elevation3,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Header: Avatar & Timer
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: const BoxDecoration(
                      color: MediColors.blue800,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.support_agent, color: MediColors.white, size: 26),
                  ),
                  const SizedBox(width: MediDimensions.space12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'AI Clinical Intake',
                        style: TextStyle(
                          color: MediColors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      Text(
                        'Secure Intake Loop',
                        style: TextStyle(
                          color: MediColors.slate400,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: MediColors.slate800,
                  borderRadius: MediDimensions.borderFull,
                ),
                child: Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: MediColors.emerald600,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      durationText,
                      style: const TextStyle(
                        color: MediColors.white,
                        fontWeight: FontWeight.w600,
                        fontSize: 15,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: MediDimensions.space32),

          // Audio Waveform
          ListeningWave(
            isActive: isListening,
            color: MediColors.blue600,
            height: 56,
          ),

          const SizedBox(height: MediDimensions.space24),

          // Rolling Live Transcript Box
          Container(
            width: double.infinity,
            constraints: const BoxConstraints(minHeight: 80),
            padding: const EdgeInsets.all(MediDimensions.space16),
            decoration: BoxDecoration(
              color: MediColors.slate800,
              borderRadius: MediDimensions.borderLg,
              border: Border.all(color: MediColors.slate700),
            ),
            child: Text(
              transcript.isNotEmpty ? transcript : 'Listening to your symptoms... बोलिए, हम सुन रहे हैं...',
              style: const TextStyle(
                color: MediColors.white,
                fontSize: 18,
                height: 1.4,
              ),
              textAlign: TextAlign.center,
            ),
          ),

          if (activeSymptoms.isNotEmpty) ...[
            const SizedBox(height: MediDimensions.space16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              alignment: WrapAlignment.center,
              children: activeSymptoms.map((symptom) {
                return Chip(
                  label: Text(
                    symptom,
                    style: const TextStyle(color: MediColors.blue100, fontWeight: FontWeight.w600),
                  ),
                  backgroundColor: MediColors.blue900,
                  side: BorderSide.none,
                );
              }).toList(),
            ),
          ],

          const SizedBox(height: MediDimensions.space32),

          // Call Action Controls
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              // Mute Button
              IconButton.filled(
                onPressed: onToggleMute,
                icon: Icon(isMuted ? Icons.mic_off : Icons.mic),
                style: IconButton.styleFrom(
                  backgroundColor: isMuted ? MediColors.red700 : MediColors.slate800,
                  foregroundColor: MediColors.white,
                  padding: const EdgeInsets.all(16),
                ),
              ),
              // Large Red End Call Button
              GestureDetector(
                onTap: onEndCall,
                child: Container(
                  width: 72,
                  height: 72,
                  decoration: const BoxDecoration(
                    color: MediColors.red600,
                    shape: BoxShape.circle,
                    boxShadow: MediDimensions.emergencyGlow,
                  ),
                  child: const Icon(Icons.call_end, color: MediColors.white, size: 36),
                ),
              ),
              // Speaker Button
              IconButton.filled(
                onPressed: onToggleSpeaker,
                icon: Icon(isSpeakerOn ? Icons.volume_up : Icons.volume_off),
                style: IconButton.styleFrom(
                  backgroundColor: isSpeakerOn ? MediColors.blue700 : MediColors.slate800,
                  foregroundColor: MediColors.white,
                  padding: const EdgeInsets.all(16),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
