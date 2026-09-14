import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 21 — Hospital Map & Indoor Wayfinding
/// High-contrast indoor schematic wayfinding map
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 21)
class MapScreen extends StatelessWidget {
  const MapScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();

    return MediScaffold(
      title: lang.translate('hospital_map_title'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            lang.translate('hospital_map_title'),
            style: MediTypography.headlineLarge,
          ),
          const SizedBox(height: MediDimensions.space8),
          Row(
            children: [
              Container(
                width: 12,
                height: 12,
                decoration: const BoxDecoration(
                  color: MediColors.brandInteractive,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  'Follow Blue Path to Room 102 (General Medicine)',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: MediColors.brandPrimary),
                ),
              ),
            ],
          ),
          const SizedBox(height: MediDimensions.space20),
          Expanded(
            child: InteractiveViewer(
              child: Center(
                child: Container(
                  width: 360,
                  height: 380,
                  padding: const EdgeInsets.all(MediDimensions.space16),
                  decoration: BoxDecoration(
                    color: MediColors.surface,
                    borderRadius: MediDimensions.borderLg,
                    border: Border.all(color: MediColors.borderStrong, width: 2),
                    boxShadow: MediDimensions.elevation2,
                  ),
                  child: Stack(
                    children: [
                      // Floor grid blueprint
                      Column(
                        children: [
                          Row(
                            children: [
                              _buildRoom('Room 101', 'Registration', Colors.teal.shade50),
                              const SizedBox(width: 12),
                              _buildRoom('Room 102', 'Dr. Verma (You)', MediColors.blue100, isTarget: true),
                            ],
                          ),
                          const SizedBox(height: 20),
                          // Corridor
                          Container(
                            height: 60,
                            width: double.infinity,
                            decoration: BoxDecoration(
                              color: MediColors.slate100,
                              borderRadius: MediDimensions.borderSm,
                            ),
                            alignment: Alignment.center,
                            child: const Text('CENTRAL OPD CORRIDOR', style: TextStyle(color: MediColors.slate400, fontWeight: FontWeight.bold)),
                          ),
                          const SizedBox(height: 20),
                          Row(
                            children: [
                              _buildRoom('Pharmacy', 'Counter 3', MediColors.emerald50),
                              const SizedBox(width: 12),
                              _buildRoom('Path Lab', 'Blood / Urine', Colors.orange.shade50),
                            ],
                          ),
                        ],
                      ),
                      // "You Are Here" Marker
                      Positioned(
                        bottom: 80,
                        left: 40,
                        child: Column(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: MediColors.red800,
                                borderRadius: MediDimensions.borderSm,
                              ),
                              child: const Text('YOU ARE HERE', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                            ),
                            const Icon(Icons.location_on, color: MediColors.red800, size: 28),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
      bottomBar: PrimaryActionButton(
        label: lang.translate('return_to_intake'),
        icon: Icons.arrow_back_rounded,
        onPressed: () => Navigator.of(context).pop(),
      ),
    );
  }

  Widget _buildRoom(String name, String desc, Color bg, {bool isTarget = false}) {
    return Expanded(
      child: Container(
        height: 100,
        padding: const EdgeInsets.all(MediDimensions.space12),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: MediDimensions.borderMd,
          border: Border.all(
            color: isTarget ? MediColors.brandPrimary : MediColors.border,
            width: isTarget ? 2.5 : 1.0,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(name, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: isTarget ? MediColors.brandPrimary : MediColors.textPrimary)),
            const SizedBox(height: 4),
            Text(desc, style: const TextStyle(fontSize: 12, color: MediColors.textMuted)),
          ],
        ),
      ),
    );
  }
}
