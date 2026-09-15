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
        'title': lang.translate('general_medicine_title'),
        'subtitle': lang.translate('general_medicine_sub'),
        'icon': Icons.medical_services_rounded,
        'value': 'General Medicine',
      },
      {
        'title': lang.translate('ayush_dept_title'),
        'subtitle': lang.translate('ayush_dept_sub'),
        'icon': Icons.eco_rounded,
        'value': 'AYUSH (Ayurveda)',
      },
      {
        'title': lang.translate('pediatrics_dept_title'),
        'subtitle': lang.translate('pediatrics_dept_sub'),
        'icon': Icons.child_care_rounded,
        'value': 'Pediatrics',
      },
      {
        'title': lang.translate('emergency_dept_title'),
        'subtitle': lang.translate('emergency_dept_sub'),
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
            lang.translate('care_stream_sub'),
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
        label: _selectedStream.contains('AYUSH')
            ? lang.translate('continue_ayush_intake')
            : (_selectedStream == 'Emergency'
                ? lang.translate('continue_emergency_triage')
                : lang.translate('continue_intake')),
        backgroundColor: _selectedStream.contains('AYUSH')
            ? const Color(0xFF2E7D32)
            : (_selectedStream == 'Emergency' ? const Color(0xFFD32F2F) : null),
        icon: Icons.arrow_forward_rounded,
        onPressed: () async {
          encounter.setDepartment(_selectedStream);
          if (_selectedStream == 'Emergency') {
            Navigator.of(context).pushNamed('/emergency');
          } else {
            if (encounter.encounterId == null) {
              await encounter.bootstrap(
                channel: 'android_byod',
                language: lang.currentLanguage,
              );
            }
            if (!context.mounted) return;
            await context.read<IntakeProvider>().startSession(
              encounterId: encounter.encounterId!,
              language: lang.currentLanguage,
              department: _selectedStream,
            );
            if (context.mounted) {
              Navigator.of(context).pushNamed('/intake');
            }
          }
        },
      ),
    );
  }
}
