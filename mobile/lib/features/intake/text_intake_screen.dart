import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';
import '../../core/widgets/secondary_button.dart';

/// Screen 06-Text — Manual Symptom Typing Interface
/// Touch and keyboard fallback for patients who prefer typing their symptoms
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 06 Secondary CTA)
class TextIntakeScreen extends StatefulWidget {
  const TextIntakeScreen({super.key});

  @override
  State<TextIntakeScreen> createState() => _TextIntakeScreenState();
}

class _TextIntakeScreenState extends State<TextIntakeScreen> {
  final TextEditingController _textController = TextEditingController();
  final FocusNode _focusNode = FocusNode();

  final List<String> _quickChips = [
    'बुखार (Fever)',
    'सिरदर्द (Headache)',
    'खांसी और जुकाम (Cough & Cold)',
    'पेट दर्द (Stomach Pain)',
    'कमजोरी (Fatigue)',
    'उल्टी / जी मिचलाना (Nausea)',
    'सांस लेने में तकलीफ (Breathlessness)',
    'जोड़ों में दर्द (Joint Pain)',
  ];

  @override
  void dispose() {
    _textController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _appendChip(String chipText) {
    // Extract base symptom name
    final symptom = chipText.split('(').first.trim();
    final currentText = _textController.text.trim();
    if (currentText.isEmpty) {
      _textController.text = symptom;
    } else if (!currentText.contains(symptom)) {
      _textController.text = '$currentText, $symptom';
    }
    _textController.selection = TextSelection.fromPosition(
      TextPosition(offset: _textController.text.length),
    );
    setState(() {});
  }

  void _submitSymptoms() {
    final text = _textController.text.trim();
    if (text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('कृपया अपने लक्षण लिखकर बताएं (Please describe your symptoms)'),
          backgroundColor: MediColors.amber800,
        ),
      );
      return;
    }

    final intake = context.read<IntakeProvider>();
    intake.submitTurn(patientSpeech: text);
    Navigator.of(context).pushNamed('/processing');
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.watch<IntakeProvider>();

    return MediScaffold(
      title: 'Type Symptoms',
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        padding: const EdgeInsets.only(bottom: MediDimensions.space24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: MediDimensions.space12),
            Text(
              'Describe Your Symptoms (लक्षण लिखें)',
              style: MediTypography.headlineLarge,
            ),
            const SizedBox(height: MediDimensions.space8),
            const Text(
              'Type your health complaints below or tap the quick symptom chips.',
              style: TextStyle(fontSize: 16, color: MediColors.textMuted),
            ),
            const SizedBox(height: MediDimensions.space16),

            // AI Prompt / Question Bubble
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(MediDimensions.space16),
              decoration: BoxDecoration(
                color: MediColors.blue50,
                borderRadius: MediDimensions.borderLg,
                border: Border.all(color: MediColors.blue200),
              ),
              child: Row(
                children: [
                  const Icon(Icons.help_outline_rounded, color: MediColors.brandPrimary, size: 28),
                  const SizedBox(width: MediDimensions.space12),
                  Expanded(
                    child: Text(
                      intake.activeQuestion,
                      style: MediTypography.bodyLarge.copyWith(fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: MediDimensions.space20),

            // Symptom Multi-Line Input Box
            Container(
              decoration: BoxDecoration(
                color: MediColors.surface,
                borderRadius: MediDimensions.borderLg,
                border: Border.all(
                  color: _focusNode.hasFocus ? MediColors.brandPrimary : MediColors.borderStrong,
                  width: 2.0,
                ),
                boxShadow: MediDimensions.elevation1,
              ),
              child: Column(
                children: [
                  TextField(
                    controller: _textController,
                    focusNode: _focusNode,
                    maxLines: 5,
                    minLines: 4,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w500,
                      color: MediColors.textPrimary,
                      height: 1.4,
                    ),
                    decoration: InputDecoration(
                      contentPadding: const EdgeInsets.all(MediDimensions.space16),
                      hintText: 'उदा. मुझे दो दिन से तेज सिरदर्द और बुखार है... (Describe your symptoms here)',
                      hintStyle: const TextStyle(color: MediColors.slate400, fontSize: 16),
                      border: InputBorder.none,
                      suffixIcon: _textController.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear, color: MediColors.slate400),
                              onPressed: () {
                                _textController.clear();
                                setState(() {});
                              },
                            )
                          : null,
                    ),
                    onChanged: (_) => setState(() {}),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: const BoxDecoration(
                      border: Border(top: BorderSide(color: MediColors.slate200)),
                      color: MediColors.slate50,
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '${_textController.text.length} characters',
                          style: const TextStyle(fontSize: 12, color: MediColors.textMuted),
                        ),
                        if (_textController.text.isNotEmpty)
                          TextButton.icon(
                            onPressed: () {
                              _textController.clear();
                              setState(() {});
                            },
                            icon: const Icon(Icons.delete_outline, size: 16),
                            label: const Text('Clear (हटाएं)', style: TextStyle(fontSize: 12)),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: MediDimensions.space20),

            // Quick Symptom Chips
            Text(
              'Quick Add Symptoms (सामान्य लक्षण जोड़ें):',
              style: MediTypography.caption.copyWith(fontWeight: FontWeight.w700, fontSize: 14),
            ),
            const SizedBox(height: MediDimensions.space8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _quickChips.map((chip) {
                return ActionChip(
                  avatar: const Icon(Icons.add, size: 16, color: MediColors.brandPrimary),
                  label: Text(chip, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  backgroundColor: MediColors.blue50,
                  side: const BorderSide(color: MediColors.blue200),
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                  onPressed: () => _appendChip(chip),
                );
              }).toList(),
            ),
          ],
        ),
      ),
      bottomBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          PrimaryActionButton(
            label: 'Submit Symptoms & Analyze (लक्षण दर्ज करें)',
            icon: Icons.check_circle_rounded,
            onPressed: _submitSymptoms,
          ),
          const SizedBox(height: MediDimensions.space8),
          SecondaryActionButton(
            label: 'Switch to Voice Intake (बोलकर बताएं)',
            icon: Icons.mic_rounded,
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
    );
  }
}
