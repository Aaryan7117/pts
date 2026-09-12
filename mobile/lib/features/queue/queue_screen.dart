import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';
import '../../core/widgets/secondary_button.dart';
import '../../data/datasources/mock_datasource.dart';

/// Screen 19 — Department Routing & Queue Token Tracker
/// Large high-visibility token card with live position and wait estimate
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 19)
class QueueScreen extends StatelessWidget {
  const QueueScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final encounter = context.watch<EncounterProvider>();

    final token = encounter.tokenNumber ?? 'A-104';
    final queueData = MockDataSource.getMockQueueStatus();

    return MediScaffold(
      title: 'OPD Queue Ticket',
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
          // Oversized Token Card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(MediDimensions.space24),
            decoration: BoxDecoration(
              color: MediColors.surface,
              borderRadius: MediDimensions.borderXl,
              border: Border.all(color: MediColors.brandPrimary, width: 2.5),
              boxShadow: MediDimensions.elevation3,
            ),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                  decoration: BoxDecoration(
                    color: MediColors.blue50,
                    borderRadius: MediDimensions.borderSm,
                  ),
                  child: Text(
                    encounter.department.toUpperCase(),
                    style: const TextStyle(
                      color: MediColors.brandPrimary,
                      fontWeight: FontWeight.w800,
                      fontSize: 14,
                    ),
                  ),
                ),
                const SizedBox(height: MediDimensions.space16),
                const Text(
                  'YOUR QUEUE TOKEN',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: MediColors.textMuted,
                    letterSpacing: 1.5,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  token,
                  style: const TextStyle(
                    fontSize: 64,
                    fontWeight: FontWeight.w900,
                    color: MediColors.brandPrimary,
                    letterSpacing: 2.0,
                  ),
                ),
                const SizedBox(height: MediDimensions.space8),
                Text(
                  queueData.doctorRoom ?? 'Room 102 (Dr. Verma)',
                  style: MediTypography.headlineMedium.copyWith(fontSize: 20),
                ),
                const Divider(height: 36),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    Column(
                      children: [
                        const Text(
                          'Patients Ahead',
                          style: TextStyle(fontSize: 14, color: MediColors.textMuted),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${queueData.patientsAhead}',
                          style: const TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            color: MediColors.textPrimary,
                          ),
                        ),
                      ],
                    ),
                    Container(height: 40, width: 1, color: MediColors.border),
                    Column(
                      children: [
                        const Text(
                          'Estimated Wait',
                          style: TextStyle(fontSize: 14, color: MediColors.textMuted),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '~${queueData.estimatedWaitMinutes} min',
                          style: const TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            color: MediColors.emerald800,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: MediDimensions.space24),
          // Hospital Services & Wayfinding Shortcuts
          Row(
            children: [
              Expanded(
                child: SecondaryActionButton(
                  label: 'Hospital Services',
                  icon: Icons.local_pharmacy_rounded,
                  onPressed: () => Navigator.of(context).pushNamed('/services'),
                ),
              ),
              const SizedBox(width: MediDimensions.space12),
              Expanded(
                child: SecondaryActionButton(
                  label: 'Hospital Map',
                  icon: Icons.map_rounded,
                  onPressed: () => Navigator.of(context).pushNamed('/map'),
                ),
              ),
            ],
          ),
        ],
      ),
    ),
    bottomBar: PrimaryActionButton(
        label: 'Finish Intake & Print Ticket (समाप्त करें)',
        icon: Icons.print_rounded,
        onPressed: () => Navigator.of(context).pushNamed('/completion'),
      ),
    );
  }
}
