import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/choice_card.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 08 — Conversational Follow-up (SOCRATES Adaptive Questioning)
/// Adaptive clinical follow-up questions with massive tactile choices
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 08)
class ConversationalFollowupScreen extends StatefulWidget {
  const ConversationalFollowupScreen({super.key});

  @override
  State<ConversationalFollowupScreen> createState() => _ConversationalFollowupScreenState();
}

class _ConversationalFollowupScreenState extends State<ConversationalFollowupScreen> {
  String _selectedAnswer = 'No';

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.watch<IntakeProvider>();

    final options = [
      {'title': 'Yes (हाँ)', 'subtitle': 'Experiencing dizziness or nausea', 'val': 'Yes'},
      {'title': 'No (नहीं)', 'subtitle': 'No dizziness or nausea', 'val': 'No'},
      {'title': 'Mild / Unsure (थोड़ा सा)', 'subtitle': 'Mild sensation occasionally', 'val': 'Mild'},
    ];

    return MediScaffold(
      title: 'Follow-Up Question',
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: MediDimensions.space12),
          Text(
            intake.activeQuestion.isNotEmpty
                ? intake.activeQuestion
                : 'क्या सिरदर्द के साथ चक्कर या उल्टी जैसा लग रहा है?',
            style: MediTypography.headlineLarge.copyWith(fontSize: 26),
          ),
          const SizedBox(height: MediDimensions.space12),
          Text(
            'Tap your answer or speak your response aloud (जवाब चुनें):',
            style: MediTypography.bodyMedium,
          ),
          const SizedBox(height: MediDimensions.space24),
          Expanded(
            child: ListView.separated(
              itemCount: options.length,
              separatorBuilder: (_, _) => const SizedBox(height: MediDimensions.space16),
              itemBuilder: (context, index) {
                final opt = options[index];
                final isSelected = _selectedAnswer == opt['val'];

                return LargeChoiceCard(
                  title: opt['title']!,
                  subtitle: opt['subtitle']!,
                  icon: isSelected ? Icons.check_circle : Icons.radio_button_unchecked,
                  isSelected: isSelected,
                  onTap: () {
                    setState(() {
                      _selectedAnswer = opt['val']!;
                    });
                  },
                );
              },
            ),
          ),
        ],
      ),
      bottomBar: PrimaryActionButton(
        label: 'Confirm Answer (आगे बढ़ें)',
        icon: Icons.arrow_forward_rounded,
        onPressed: () async {
          await intake.submitTurn(patientSpeech: _selectedAnswer);
          if (context.mounted) {
            Navigator.of(context).pushNamed('/summary');
          }
        },
      ),
    );
  }
}
