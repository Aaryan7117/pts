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
  bool _hasCoatedTongue = false;
  bool _hasMorningStiffness = false;

  String _getPrakritiNamasteCode() {
    switch (_selectedPrakriti) {
      case 'vata': return 'NAM-PRAK-VATA';
      case 'pitta': return 'NAM-PRAK-PITTA';
      case 'kapha': return 'NAM-PRAK-KAPHA';
      case 'vata_pitta': return 'NAM-PRAK-VP';
      case 'pitta_kapha': return 'NAM-PRAK-PK';
      case 'vata_kapha': return 'NAM-PRAK-VK';
      default: return 'NAM-PRAK-TRI';
    }
  }

  String _getAgniNamasteCode() {
    switch (_selectedAgni) {
      case 'vishama': return 'NAM-AGNI-VISH';
      case 'tikshna': return 'NAM-AGNI-TIK';
      case 'manda': return 'NAM-AGNI-MAND';
      default: return 'NAM-AGNI-SAM';
    }
  }

  String _getKoshthaNamasteCode() {
    switch (_selectedKoshtha) {
      case 'krura': return 'NAM-KOSH-KRU';
      case 'mridu': return 'NAM-KOSH-MRI';
      default: return 'NAM-KOSH-MAD';
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.read<IntakeProvider>();

    return MediScaffold(
      title: lang.translate('ayush_title'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: MediColors.emerald50,
                    borderRadius: MediDimensions.borderSm,
                    border: Border.all(color: MediColors.emerald200),
                  ),
                  child: const Text(
                    'NAMASTE PORTAL COMPLIANT',
                    style: TextStyle(color: MediColors.emerald800, fontWeight: FontWeight.w700, fontSize: 12),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.amber.shade50,
                    borderRadius: MediDimensions.borderSm,
                    border: Border.all(color: Colors.amber.shade200),
                  ),
                  child: Text(
                    '${_getPrakritiNamasteCode()} • ${_getAgniNamasteCode()}',
                    style: TextStyle(color: Colors.amber.shade900, fontWeight: FontWeight.w600, fontSize: 12),
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
            Text(
              lang.translate('ayush_sub'),
              style: const TextStyle(fontSize: 16, color: MediColors.textMuted),
            ),
            const SizedBox(height: MediDimensions.space24),

            // Section 1: Agni Assessment (Digestive Fire)
            Text(lang.translate('agni_section_title'), style: MediTypography.headlineMedium.copyWith(fontSize: 20)),
            const SizedBox(height: MediDimensions.space12),
            LargeChoiceCard(
              title: lang.translate('sama_agni'),
              subtitle: lang.translate('sama_agni_sub'),
              icon: Icons.local_fire_department_rounded,
              isSelected: _selectedAgni == 'sama',
              onTap: () => setState(() => _selectedAgni = 'sama'),
            ),
            const SizedBox(height: MediDimensions.space8),
            LargeChoiceCard(
              title: lang.translate('vishama_agni'),
              subtitle: lang.translate('vishama_agni_sub'),
              icon: Icons.waves_rounded,
              isSelected: _selectedAgni == 'vishama',
              onTap: () => setState(() => _selectedAgni = 'vishama'),
            ),
            const SizedBox(height: MediDimensions.space8),
            LargeChoiceCard(
              title: lang.translate('tikshna_agni'),
              subtitle: lang.translate('tikshna_agni_sub'),
              icon: Icons.whatshot_rounded,
              isSelected: _selectedAgni == 'tikshna',
              onTap: () => setState(() => _selectedAgni = 'tikshna'),
            ),
            const SizedBox(height: MediDimensions.space8),
            LargeChoiceCard(
              title: lang.translate('manda_agni'),
              subtitle: lang.translate('manda_agni_sub'),
              icon: Icons.hourglass_bottom_rounded,
              isSelected: _selectedAgni == 'manda',
              onTap: () => setState(() => _selectedAgni = 'manda'),
            ),

            const SizedBox(height: MediDimensions.space16),
            // Ama Markers
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: MediDimensions.borderMd,
                border: Border.all(color: Colors.grey.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(lang.translate('ama_section_title'), style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                  CheckboxListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    title: Text(lang.translate('coated_tongue')),
                    value: _hasCoatedTongue,
                    onChanged: (v) => setState(() => _hasCoatedTongue = v ?? false),
                  ),
                  CheckboxListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    title: Text(lang.translate('morning_stiffness')),
                    value: _hasMorningStiffness,
                    onChanged: (v) => setState(() => _hasMorningStiffness = v ?? false),
                  ),
                ],
              ),
            ),

            const SizedBox(height: MediDimensions.space24),

            // Section 2: Prakriti (Constitution)
            Text(lang.translate('prakriti_section_title'), style: MediTypography.headlineMedium.copyWith(fontSize: 20)),
            const SizedBox(height: MediDimensions.space12),
            LargeChoiceCard(
              title: lang.translate('tridoshaja_title'),
              subtitle: lang.translate('tridoshaja_sub'),
              icon: Icons.balance_rounded,
              isSelected: _selectedPrakriti == 'tridoshaja',
              onTap: () => setState(() => _selectedPrakriti = 'tridoshaja'),
            ),
            const SizedBox(height: MediDimensions.space8),
            LargeChoiceCard(
              title: lang.translate('vata_title'),
              subtitle: lang.translate('vata_sub'),
              icon: Icons.air_rounded,
              isSelected: _selectedPrakriti == 'vata',
              onTap: () => setState(() => _selectedPrakriti = 'vata'),
            ),
            const SizedBox(height: MediDimensions.space8),
            LargeChoiceCard(
              title: lang.translate('pitta_title'),
              subtitle: lang.translate('pitta_sub'),
              icon: Icons.wb_sunny_rounded,
              isSelected: _selectedPrakriti == 'pitta',
              onTap: () => setState(() => _selectedPrakriti = 'pitta'),
            ),
            const SizedBox(height: MediDimensions.space8),
            LargeChoiceCard(
              title: lang.translate('kapha_title'),
              subtitle: lang.translate('kapha_sub'),
              icon: Icons.water_drop_rounded,
              isSelected: _selectedPrakriti == 'kapha',
              onTap: () => setState(() => _selectedPrakriti = 'kapha'),
            ),

            const SizedBox(height: MediDimensions.space24),

            // Section 3: Koshtha (Bowel Habits)
            Text(lang.translate('koshtha_section_title'), style: MediTypography.headlineMedium.copyWith(fontSize: 20)),
            const SizedBox(height: MediDimensions.space12),
            LargeChoiceCard(
              title: lang.translate('madhyama_koshtha'),
              subtitle: 'Regular once-daily bowel motion, normal soft formed stool',
              icon: Icons.check_circle_outline,
              isSelected: _selectedKoshtha == 'madhyama',
              onTap: () => setState(() => _selectedKoshtha = 'madhyama'),
            ),
            const SizedBox(height: MediDimensions.space8),
            LargeChoiceCard(
              title: lang.translate('krura_koshtha'),
              subtitle: 'Constipation-prone, hard dry stools, requires laxatives',
              icon: Icons.warning_amber_rounded,
              isSelected: _selectedKoshtha == 'krura',
              onTap: () => setState(() => _selectedKoshtha = 'krura'),
            ),
            const SizedBox(height: MediDimensions.space8),
            LargeChoiceCard(
              title: lang.translate('mridu_koshtha'),
              subtitle: 'Easy loose motions, sensitive digestion, evacuated quickly with milk',
              icon: Icons.opacity_rounded,
              isSelected: _selectedKoshtha == 'mridu',
              onTap: () => setState(() => _selectedKoshtha = 'mridu'),
            ),
            const SizedBox(height: MediDimensions.space24),
          ],
        ),
      ),
      bottomBar: PrimaryActionButton(
        label: lang.translate('continue_queue'),
        backgroundColor: MediColors.ayushGreen,
        icon: Icons.confirmation_number_rounded,
        onPressed: () {
          final agniRec = AgniAssessment(
            agniType: _selectedAgni,
            appetitePattern: _selectedAgni == 'sama' ? 'regular' : (_selectedAgni == 'tikshna' ? 'excessive' : 'irregular'),
            postMealHeaviness: _hasMorningStiffness || _selectedAgni == 'manda',
            bowelRegularity: _selectedKoshtha == 'madhyama' ? 'regular' : 'irregular',
            namasteCode: _getAgniNamasteCode(),
          );

          final prakritiRec = PrakritiAssessment(
            dominantDosha: _selectedPrakriti,
            bodyFrame: _selectedPrakriti == 'kapha' ? 'broad_heavy' : (_selectedPrakriti == 'vata' ? 'thin_light' : 'medium_muscular'),
            skinTexture: _selectedPrakriti == 'vata' ? 'dry_rough' : (_selectedPrakriti == 'pitta' ? 'warm_reddish' : 'smooth_oily'),
            digestionSpeed: _selectedAgni == 'tikshna' ? 'rapid' : (_selectedAgni == 'manda' ? 'slow' : 'moderate'),
            weatherSensitivity: _selectedPrakriti == 'pitta' ? 'intolerant_to_heat' : 'intolerant_to_cold',
            sleepPattern: _selectedPrakriti == 'vata' ? 'light_interrupted' : (_selectedPrakriti == 'kapha' ? 'deep_heavy' : 'moderate'),
            namasteCode: _getPrakritiNamasteCode(),
          );

          final koshthaRec = KoshthaAssessment(
            koshthaType: _selectedKoshtha,
            bowelFrequency: _selectedKoshtha == 'madhyama' ? 'once_daily' : (_selectedKoshtha == 'mridu' ? 'twice_or_more' : 'alternate_days'),
            stoolConsistency: _selectedKoshtha == 'krura' ? 'hard_dry' : (_selectedKoshtha == 'mridu' ? 'soft_loose' : 'soft_formed'),
            namasteCode: _getKoshthaNamasteCode(),
          );

          final fullRecord = AyurvedicIntakeRecord(
            agni: agniRec,
            prakritiBaseline: prakritiRec,
            koshtha: koshthaRec,
            provisionalDoshaImbalance: [_selectedPrakriti.toUpperCase(), if (_hasCoatedTongue) 'AMA_POSITIVE'],
          );

          intake.setAyushRecord(fullRecord);

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('AYUSH Profile Saved (${_getPrakritiNamasteCode()} • ${_getAgniNamasteCode()})'),
              backgroundColor: MediColors.ayushGreen,
              duration: const Duration(seconds: 2),
            ),
          );
          Navigator.of(context).pushNamed('/queue');
        },
      ),
    );
  }
}
