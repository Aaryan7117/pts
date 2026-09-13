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
import '../../data/models/ayush_profile.dart';

/// Screen 18 — AYUSH Profile (Dashavidha Pariksha)
/// Agni, Prakriti, Koshtha, and Ahara-Vihara assessment
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 18)
class AyushScreen extends StatefulWidget {
  const AyushScreen({super.key});

  @override
  State<AyushScreen> createState() => _AyushScreenState();
}

class _AyushScreenState extends State<AyushScreen> {
  String _selectedAgni = 'sama';
  String _selectedPrakriti = 'tridoshaja';
  String _selectedKoshtha = 'madhyama';

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.read<IntakeProvider>();

    return MediScaffold(
      title: 'AYUSH Clinical Assessment',
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: MediColors.emerald50,
                    borderRadius: MediDimensions.borderSm,
                  ),
                  child: const Text(
                    'NAMASTE PORTAL COMPLIANT',
                    style: TextStyle(color: MediColors.emerald800, fontWeight: FontWeight.w700, fontSize: 12),
                  ),
                ),
              ],
            ),
            const SizedBox(height: MediDimensions.space12),
            Text(
              lang.translate('ayush_title'),
              style: MediTypography.headlineLarge,
            ),
            const SizedBox(height: MediDimensions.space8),
            const Text(
              'Dashavidha Pariksha pre-assessment for your Ayurvedic physician.',
              style: TextStyle(fontSize: 16, color: MediColors.textMuted),
            ),
            const SizedBox(height: MediDimensions.space24),

            // Section 1: Agni Assessment (Digestive Fire)
            Text('1. Digestive Fire / Agni (पाचन शक्ति)', style: MediTypography.headlineMedium.copyWith(fontSize: 20)),
            const SizedBox(height: MediDimensions.space12),
            LargeChoiceCard(
              title: 'Sama Agni (सम अग्नि)',
              subtitle: 'Balanced appetite, normal digestion without discomfort',
              icon: Icons.local_fire_department_rounded,
              isSelected: _selectedAgni == 'sama',
              onTap: () => setState(() => _selectedAgni = 'sama'),
            ),
            const SizedBox(height: MediDimensions.space8),
            LargeChoiceCard(
              title: 'Tikshna Agni (तीक्ष्ण अग्नि)',
              subtitle: 'Excessive appetite, heartburn, acidity, rapid digestion',
              icon: Icons.whatshot_rounded,
              isSelected: _selectedAgni == 'tikshna',
              onTap: () => setState(() => _selectedAgni = 'tikshna'),
            ),

            const SizedBox(height: MediDimensions.space24),

            // Section 2: Prakriti (Constitution)
            Text('2. Body Constitution / Prakriti (प्रकृति)', style: MediTypography.headlineMedium.copyWith(fontSize: 20)),
            const SizedBox(height: MediDimensions.space12),
            LargeChoiceCard(
              title: 'Tridoshaja / Balanced (त्रिदोषज)',
              subtitle: 'Medium frame, balanced sleep, good seasonal resilience',
              icon: Icons.balance_rounded,
              isSelected: _selectedPrakriti == 'tridoshaja',
              onTap: () => setState(() => _selectedPrakriti = 'tridoshaja'),
            ),
            const SizedBox(height: MediDimensions.space8),
            LargeChoiceCard(
              title: 'Vata Dominant (वात प्रधान)',
              subtitle: 'Light frame, dry skin, light sleep, cold intolerance',
              icon: Icons.air_rounded,
              isSelected: _selectedPrakriti == 'vata',
              onTap: () => setState(() => _selectedPrakriti = 'vata'),
            ),

            const SizedBox(height: MediDimensions.space24),

            // Section 3: Koshtha (Bowel Habits)
            Text('3. Bowel Constitution / Koshtha (कोष्ठ)', style: MediTypography.headlineMedium.copyWith(fontSize: 20)),
            const SizedBox(height: MediDimensions.space12),
            LargeChoiceCard(
              title: 'Madhyama Koshtha (मध्यम कोष्ठ)',
              subtitle: 'Regular once-daily bowel motion, normal soft stool',
              icon: Icons.check_circle_outline,
              isSelected: _selectedKoshtha == 'madhyama',
              onTap: () => setState(() => _selectedKoshtha = 'madhyama'),
            ),
            const SizedBox(height: MediDimensions.space8),
            LargeChoiceCard(
              title: 'Krura Koshtha (क्रूर कोष्ठ)',
              subtitle: 'Constipation-prone, hard dry stools, requires laxative',
              icon: Icons.warning_amber_rounded,
              isSelected: _selectedKoshtha == 'krura',
              onTap: () => setState(() => _selectedKoshtha = 'krura'),
            ),
            const SizedBox(height: MediDimensions.space24),
          ],
        ),
      ),
      bottomBar: PrimaryActionButton(
        label: 'Save AYUSH Profile & Get Token (टोकन लें)',
        backgroundColor: MediColors.ayushGreen,
        icon: Icons.confirmation_number_rounded,
        onPressed: () {
          intake.setAyushRecord(AyurvedicIntakeRecord(
            agni: AgniAssessment(
              agniType: _selectedAgni,
              appetitePattern: _selectedAgni == 'sama' ? 'regular' : 'excessive',
              bowelRegularity: _selectedKoshtha == 'madhyama' ? 'regular' : 'irregular_hard',
              namasteCode: 'NAMASTE:AGNI-${_selectedAgni.toUpperCase()}',
            ),
            prakritiBaseline: PrakritiAssessment(
              dominantDosha: _selectedPrakriti,
              bodyFrame: _selectedPrakriti == 'vata' ? 'thin_prominent_joints' : 'medium_muscular',
              skinTexture: _selectedPrakriti == 'vata' ? 'dry_rough_cool' : 'smooth_balanced',
              digestionSpeed: 'moderate',
              weatherSensitivity: _selectedPrakriti == 'vata' ? 'cold' : 'none',
              sleepPattern: _selectedPrakriti == 'vata' ? 'light_broken' : 'sound_deep',
              namasteCode: 'NAMASTE:PRAKRITI-${_selectedPrakriti.toUpperCase()}',
            ),
            koshtha: KoshthaAssessment(
              koshthaType: _selectedKoshtha,
              bowelFrequency: _selectedKoshtha == 'madhyama' ? 'once_daily' : 'irregular',
              stoolConsistency: _selectedKoshtha == 'madhyama' ? 'soft_formed' : 'hard_dry',
              namasteCode: 'NAMASTE:KOSHTHA-${_selectedKoshtha.toUpperCase()}',
            ),
          ));
          Navigator.of(context).pushNamed('/queue');
        },
      ),
    );
  }
}
