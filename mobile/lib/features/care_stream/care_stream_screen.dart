import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/choice_card.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 05 — Care Stream / Reason for Visit
/// General Medicine, AYUSH, Maternal/Child, and Emergency options
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 05)
class CareStreamScreen extends StatefulWidget {
  const CareStreamScreen({super.key});

  @override
  State<CareStreamScreen> createState() => _CareStreamScreenState();
}

class _CareStreamScreenState extends State<CareStreamScreen> {
  String _selectedStream = 'General Medicine';

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final encounter = context.read<EncounterProvider>();

    final streams = [
      {
        'title': 'General Medicine (सामान्य चिकित्सा)',
        'subtitle': 'Fever, cough, cold, weakness, diabetes, blood pressure',
        'icon': Icons.medical_services_rounded,
        'value': 'General Medicine',
      },
      {
        'title': 'AYUSH / Ayurveda (आयुष एवं आयुर्वेद)',
        'subtitle': 'Prakriti, chronic joint pain, digestive health, lifestyle',
        'icon': Icons.eco_rounded,
        'value': 'AYUSH (Ayurveda)',
      },
      {
        'title': 'Pediatrics & Child Health (बाल रोग)',
        'subtitle': 'Child immunization, growth, pediatric infections',
        'icon': Icons.child_care_rounded,
        'value': 'Pediatrics',
      },
      {
        'title': 'Urgent / Emergency Care (आपातकालीन)',
        'subtitle': 'Chest pain, acute breathlessness, bleeding, trauma',
        'icon': Icons.emergency_rounded,
        'value': 'Emergency',
      },
    ];

    return MediScaffold(
      title: lang.translate('care_stream_title'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            lang.translate('care_stream_title'),
            style: MediTypography.headlineLarge,
          ),
          const SizedBox(height: MediDimensions.space8),
          Text(
            'Select the clinic or medical department you wish to consult today.',
            style: MediTypography.bodyMedium,
          ),
          const SizedBox(height: MediDimensions.space24),
          Expanded(
            child: ListView.separated(
              itemCount: streams.length,
              separatorBuilder: (_, _) => const SizedBox(height: MediDimensions.space12),
              itemBuilder: (context, index) {
                final item = streams[index];
                final isSelected = _selectedStream == item['value'];

                return LargeChoiceCard(
                  title: item['title'] as String,
                  subtitle: item['subtitle'] as String,
                  icon: item['icon'] as IconData,
                  isSelected: isSelected,
                  onTap: () {
                    setState(() {
                      _selectedStream = item['value'] as String;
                    });
                  },
                );
              },
            ),
          ),
        ],
      ),
      bottomBar: PrimaryActionButton(
        label: 'Continue to Intake (आगे बढ़ें)',
        icon: Icons.arrow_forward_rounded,
        onPressed: () {
          encounter.setDepartment(_selectedStream);
          if (_selectedStream == 'Emergency') {
            Navigator.of(context).pushNamed('/emergency');
          } else {
            context.read<IntakeProvider>().startSession(
              encounterId: encounter.encounterId ?? 'enc-001',
              language: lang.currentLanguage,
            );
            Navigator.of(context).pushNamed('/intake');
          }
        },
      ),
    );
  }
}
