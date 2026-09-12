import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/summary_card.dart';
import '../../core/widgets/primary_button.dart';
import '../../core/widgets/secondary_button.dart';
import '../../data/datasources/mock_datasource.dart';

/// Screen 10 — Simple Summary Confirmation
/// Closed-loop explain-back fact verification with tactile [YES] / [NO]
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 10)
class SummaryConfirmationScreen extends StatelessWidget {
  const SummaryConfirmationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.watch<IntakeProvider>();
    final encounter = context.read<EncounterProvider>();

    final displayFacts = intake.facts.isNotEmpty ? intake.facts : MockDataSource.getMockFacts();

    return MediScaffold(
      title: 'Confirm Information',
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            lang.translate('summary_title'),
            style: MediTypography.headlineLarge,
          ),
          const SizedBox(height: MediDimensions.space8),
          Text(
            'Check each item. Tap "Correct" to confirm or "Wrong" if incorrect.',
            style: MediTypography.bodyMedium,
          ),
          const SizedBox(height: MediDimensions.space20),
          Expanded(
            child: ListView.builder(
              itemCount: displayFacts.length,
              itemBuilder: (context, index) {
                final fact = displayFacts[index];
                return SummaryCard(
                  fact: fact,
                  onConfirm: () => intake.confirmFact(fact.id),
                  onReject: () => intake.rejectFact(fact.id),
                );
              },
            ),
          ),
        ],
      ),
      bottomBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          PrimaryActionButton(
            label: 'Confirm & Next (आगे बढ़ें)',
            icon: Icons.check_circle_rounded,
            onPressed: () {
              // If patient reported chest pain or emergency symptom, route to triage
              final hasEmergencySymptom = displayFacts.any(
                (f) => f.value.toLowerCase().contains('chest') || f.value.toLowerCase().contains('heart'),
              );

              if (hasEmergencySymptom) {
                encounter.setSeverityBadge('RED');
                Navigator.of(context).pushNamed('/triage');
              } else {
                Navigator.of(context).pushNamed('/doc_intro');
              }
            },
          ),
          const SizedBox(height: MediDimensions.space8),
          SecondaryActionButton(
            label: '+ Add Another Symptom (अन्य लक्षण)',
            onPressed: () => Navigator.of(context).pushNamed('/intake'),
          ),
        ],
      ),
    );
  }
}
