import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 23 — Ambulance Live Status Tracker
/// Live ETA, vehicle ID, driver contact, with explicit simulated demo label
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 23)
class AmbulanceScreen extends StatelessWidget {
  const AmbulanceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MediScaffold(
      title: 'Ambulance Dispatch Tracker',
      backgroundColor: MediColors.red50,
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: MediColors.amber100,
              borderRadius: MediDimensions.borderSm,
            ),
            child: const Text(
              'DEMO SIMULATION — CONNECTED TO FLEET GATEWAY',
              style: TextStyle(color: MediColors.amber900, fontWeight: FontWeight.w700, fontSize: 11),
            ),
          ),
          const SizedBox(height: MediDimensions.space12),
          Text(
            'Ambulance Dispatched',
            style: MediTypography.headlineLarge.copyWith(color: MediColors.red900),
          ),
          const SizedBox(height: MediDimensions.space8),
          const Text(
            'Unit is en route to hospital emergency drop-off gate.',
            style: TextStyle(fontSize: 16),
          ),
          const SizedBox(height: MediDimensions.space24),

          // Live ETA Card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(MediDimensions.space24),
            decoration: BoxDecoration(
              color: MediColors.white,
              borderRadius: MediDimensions.borderLg,
              border: Border.all(color: MediColors.red200, width: 2),
              boxShadow: MediDimensions.elevation2,
            ),
            child: Column(
              children: [
                const Icon(Icons.airport_shuttle_rounded, color: MediColors.red800, size: 56),
                const SizedBox(height: 12),
                const Text('ESTIMATED ARRIVAL', style: TextStyle(fontSize: 14, color: MediColors.textMuted, letterSpacing: 1.2)),
                const SizedBox(height: 4),
                const Text(
                  '~6 Minutes',
                  style: TextStyle(fontSize: 40, fontWeight: FontWeight.w900, color: MediColors.red800),
                ),
                const Divider(height: 32),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Vehicle Number:', style: TextStyle(fontSize: 15, color: MediColors.textMuted)),
                    SizedBox(width: 8),
                    Flexible(
                      child: Text('DL 01 AB 4819', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold), textAlign: TextAlign.right),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Paramedic Lead:', style: TextStyle(fontSize: 15, color: MediColors.textMuted)),
                    SizedBox(width: 8),
                    Flexible(
                      child: Text('Suresh Kumar (ALS Certified)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold), textAlign: TextAlign.right),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Driver Contact:', style: TextStyle(fontSize: 15, color: MediColors.textMuted)),
                    SizedBox(width: 8),
                    Flexible(
                      child: Text('+91 98112 34567', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: MediColors.brandPrimary), textAlign: TextAlign.right),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    ),
    bottomBar: PrimaryActionButton(
        label: 'Return to Main Menu (वापस जाएं)',
        onPressed: () => Navigator.of(context).pop(),
      ),
    );
  }
}
