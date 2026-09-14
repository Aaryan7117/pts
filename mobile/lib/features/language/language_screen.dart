import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';
import '../../core/widgets/choice_card.dart';
import '../../data/models/encounter.dart';

/// Screen 02 — Language Selection
/// 5 Indian Languages in Native Scripts with Tactile Selection
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 02)
class LanguageScreen extends StatelessWidget {
  const LanguageScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();

    return MediScaffold(
      title: lang.translate('select_language'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) {
        lang.setLanguage(l);
        context.read<EncounterProvider>().updateLanguage(l);
        context.read<IntakeProvider>().setLanguage(l);
      },
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            lang.translate('select_language'),
            style: MediTypography.headlineLarge,
          ),
          const SizedBox(height: MediDimensions.space8),
          Text(
            lang.translate('choose_language_sub'),
            style: MediTypography.bodyMedium,
          ),
          const SizedBox(height: MediDimensions.space24),
          Expanded(
            child: ListView.separated(
              itemCount: kSupportedLanguages.length,
              separatorBuilder: (_, _) => const SizedBox(height: MediDimensions.space12),
              itemBuilder: (context, index) {
                final item = kSupportedLanguages[index];
                final isSelected = lang.currentLanguage == item.code;

                return LargeChoiceCard(
                  title: item.label,
                  subtitle: item.code.toUpperCase(),
                  icon: Icons.language,
                  isSelected: isSelected,
                  onTap: () {
                    lang.setLanguage(item.code);
                    context.read<EncounterProvider>().updateLanguage(item.code);
                    context.read<IntakeProvider>().setLanguage(item.code);
                  },
                );
              },
            ),
          ),
        ],
      ),
      bottomBar: PrimaryActionButton(
        label: lang.translate('agree_continue'),
        icon: Icons.arrow_forward_rounded,
        onPressed: () {
          context.read<EncounterProvider>().updateLanguage(lang.currentLanguage);
          context.read<IntakeProvider>().setLanguage(lang.currentLanguage);
          Navigator.of(context).pushNamed('/consent');
        },
      ),
    );
  }
}
