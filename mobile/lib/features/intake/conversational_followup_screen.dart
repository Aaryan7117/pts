import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/colors.dart';
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
  String _selectedAnswer = '';

  List<Map<String, String>> _getOptionsForQuestion(String question) {
    final q = question.toLowerCase();

    // 1. Pain / Severity Scale (1 to 10)
    if (q.contains('1-10') || q.contains('1 से 10') || q.contains('पैमाने') || q.contains('scale') || q.contains('1 to 10') || q.contains('तकलीफ कितनी')) {
      return [
        {
          'title': '1 - 3 : Mild (हल्का दर्द)',
          'subtitle': 'Noticeable but does not disrupt routine activities',
          'val': '1-3 Mild Pain',
        },
        {
          'title': '4 - 6 : Moderate (मध्यम दर्द)',
          'subtitle': 'Significant discomfort, interferes with daily tasks',
          'val': '4-6 Moderate Pain',
        },
        {
          'title': '7 - 10 : Severe / Unbearable (तेज या असहनीय दर्द)',
          'subtitle': 'Severe pain, unable to perform basic functions',
          'val': '7-10 Severe Pain',
        },
      ];
    }

    // 2. Duration (Days / Weeks / Months)
    if (q.contains('कब से') || q.contains('how long') || q.contains('दिन') || q.contains('हफ्ते') || q.contains('महीने') || q.contains('duration')) {
      return [
        {
          'title': '1 - 2 Days (आज या कल से)',
          'subtitle': 'Acute onset within the past 48 hours',
          'val': '1-2 Days',
        },
        {
          'title': '3 - 7 Days (लगभग 1 हफ्ते से)',
          'subtitle': 'Ongoing for several days this week',
          'val': '3-7 Days',
        },
        {
          'title': '2 - 4 Weeks (2 से 4 हफ्ते से)',
          'subtitle': 'Sub-acute symptoms lasting weeks',
          'val': '2-4 Weeks',
        },
        {
          'title': 'More than a month (1 महीने से अधिक)',
          'subtitle': 'Chronic persistent problem',
          'val': 'Over 1 Month',
        },
      ];
    }

    // 3. Current Medications / Medicine
    if (q.contains('दवाई') || q.contains('medication') || q.contains('medicine') || q.contains('दवाइयाँ')) {
      return [
        {
          'title': 'No Medicines (कोई दवा नहीं ले रहे)',
          'subtitle': 'Not on any regular or prescription drugs',
          'val': 'No current medications',
        },
        {
          'title': 'Taking BP/Sugar/Thyroid (नियमित दवाएं चल रही हैं)',
          'subtitle': 'Taking daily prescription medication',
          'val': 'Taking regular chronic medications',
        },
        {
          'title': 'Took Painkiller / Paracetamol (पैरासिटामोल या दर्द की दवा ली है)',
          'subtitle': 'Over-the-counter temporary relief taken recently',
          'val': 'Took OTC Paracetamol / Pain relief',
        },
      ];
    }

    // 4. Drug Allergy
    if (q.contains('एलर्जी') || q.contains('allergy') || q.contains('reaction')) {
      return [
        {
          'title': 'No Known Drug Allergy (कोई एलर्जी नहीं है)',
          'subtitle': 'Never had an adverse drug reaction',
          'val': 'No drug allergies',
        },
        {
          'title': 'Yes, Allergic to Medicines (हाँ, दवा से एलर्जी है)',
          'subtitle': 'History of reaction (e.g. Penicillin, Sulfa)',
          'val': 'Yes, has drug allergy',
        },
        {
          'title': 'Unsure / Never Checked (पक्का नहीं पता)',
          'subtitle': 'Not aware of any specific drug allergies',
          'val': 'Unsure about allergies',
        },
      ];
    }

    // 5. Default / Yes-No Symptoms
    return [
      {
        'title': 'Yes (हाँ)',
        'subtitle': 'Experiencing this symptom',
        'val': 'Yes',
      },
      {
        'title': 'No (नहीं)',
        'subtitle': 'Do not have this symptom',
        'val': 'No',
      },
      {
        'title': 'Mild / Occasionally (थोड़ा बहुत / कभी-कभी)',
        'subtitle': 'Occasional or mild sensation',
        'val': 'Mild occasional',
      },
    ];
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.watch<IntakeProvider>();

    final question = intake.activeQuestion.isNotEmpty
        ? intake.activeQuestion
        : 'क्या सिरदर्द के साथ चक्कर या उल्टी जैसा लग रहा है?';

    final options = _getOptionsForQuestion(question);

    return MediScaffold(
      title: lang.translate('followup_title'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: MediDimensions.space12),
          Text(
            question,
            style: MediTypography.headlineLarge.copyWith(fontSize: 24),
          ),
          const SizedBox(height: MediDimensions.space12),
          Text(
            lang.translate('followup_sub'),
            style: MediTypography.bodyMedium,
          ),
          const SizedBox(height: MediDimensions.space20),
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
      bottomBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          PrimaryActionButton(
            label: lang.translate('confirm_answer'),
            icon: Icons.arrow_forward_rounded,
            onPressed: () async {
              final answerToSubmit = _selectedAnswer.isNotEmpty
                  ? _selectedAnswer
                  : (options.isNotEmpty ? options.first['val']! : 'Yes');

              await intake.submitTurn(patientSpeech: answerToSubmit);
              if (context.mounted) {
                if (intake.isInterviewCompleted) {
                  Navigator.of(context).pushReplacementNamed('/summary');
                } else {
                  setState(() {
                    _selectedAnswer = '';
                  });
                }
              }
            },
          ),
          const SizedBox(height: MediDimensions.space8),
          TextButton(
            onPressed: () => Navigator.of(context).pushNamed('/summary'),
            child: const Text(
              'Skip directly to Summary (सीधे सारांश देखें)',
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: MediColors.brandPrimary),
            ),
          ),
        ],
      ),
    );
  }
}
