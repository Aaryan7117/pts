import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';

/// Screen 13 — Document Camera & Clinical Scanner
/// Provides interactive camera alignment viewfinder with real clinical prescription selections
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 13)
class DocumentCameraScreen extends StatefulWidget {
  const DocumentCameraScreen({super.key});

  @override
  State<DocumentCameraScreen> createState() => _DocumentCameraScreenState();
}

class _DocumentCameraScreenState extends State<DocumentCameraScreen> {
  int _selectedDocIndex = 0;

  final List<Map<String, dynamic>> _sampleDocs = [
    {
      'title': 'Lakshmi Devi (F/58)',
      'subtitle': 'Diabetes & HTN OPD — Metformin, Glimepiride',
      'doctor': 'Dr. S. Sharma (General Medicine)',
      'filename': 'doc-demo-lakshmi-rx_lakshmi_devi_prescription.jpg',
      'color': MediColors.blue50,
      'badge': 'Diabetes Rx',
      'meds': ['1. Tab Metformin 500mg BD', '2. Tab Glimepiride 1mg OD', '3. Tab Atorvastatin 10mg HS'],
    },
    {
      'title': 'Rajesh Sharma (M/45)',
      'subtitle': 'Cardiology OPD — Telmisartan, Amlodipine',
      'doctor': 'Dr. V. Verma (Cardiology)',
      'filename': 'doc-demo-rajesh-rx_rajesh_sharma_cardio_rx.jpg',
      'color': MediColors.emerald50,
      'badge': 'Cardio Rx',
      'meds': ['1. Tab Telmisartan 40mg OD', '2. Tab Amlodipine 5mg OD', '3. Tab Ecosprin 75mg OD'],
    },
    {
      'title': 'Priya Nair (F/32)',
      'subtitle': 'Gastroenterology — Pantoprazole, Domperidone',
      'doctor': 'Dr. P. Nair (Gastro OPD)',
      'filename': 'doc-demo-priya-rx_priya_nair_gastro_rx.jpg',
      'color': MediColors.blue50,
      'badge': 'Gastro Rx',
      'meds': ['1. Tab Pantoprazole 40mg OD (Empty Stomach)', '2. Tab Domperidone 10mg BD'],
    },
    {
      'title': 'Sunita Patel (F/52)',
      'subtitle': 'Emergency Lab Report — Critical Glucose Alert',
      'doctor': 'City Pathology Labs',
      'filename': 'doc-demo-sunita-lab_sunita_patel_glucose_panic_report.jpg',
      'color': MediColors.amber50,
      'badge': 'Panic Lab',
      'meds': ['Fasting Blood Sugar: 382 mg/dL [CRITICAL HIGH]', 'HbA1c: 11.4%'],
    },
  ];

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.read<IntakeProvider>();
    final encounter = context.read<EncounterProvider>();
    final currentDoc = _sampleDocs[_selectedDocIndex];

    return MediScaffold(
      title: 'Align Document',
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          children: [
            const SizedBox(height: MediDimensions.space12),
            Text(
              'Hold prescription within the frame',
              style: MediTypography.headlineMedium.copyWith(fontSize: 22),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space8),
            const Text(
              'Align corners and tap capture for instant AI extraction (पर्ची को सीधा रखें)',
              style: TextStyle(fontSize: 15, color: MediColors.textMuted),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space20),

            // Camera Viewfinder Frame with Selected Prescription Document
            Container(
              width: double.infinity,
              height: 310,
              decoration: BoxDecoration(
                color: MediColors.slate900,
                borderRadius: MediDimensions.borderLg,
                boxShadow: MediDimensions.elevation3,
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  // Document Surface Inside Camera
                  Container(
                    width: 270,
                    height: 250,
                    padding: const EdgeInsets.all(MediDimensions.space16),
                    decoration: BoxDecoration(
                      color: MediColors.white,
                      borderRadius: MediDimensions.borderSm,
                      boxShadow: MediDimensions.elevation2,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              currentDoc['doctor'] as String,
                              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 11, color: MediColors.brandPrimary),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: MediColors.blue100,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                currentDoc['badge'] as String,
                                style: const TextStyle(color: MediColors.brandPrimary, fontSize: 10, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ],
                        ),
                        const Divider(height: 12),
                        Text(
                          'Patient: ${currentDoc['title']}',
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Rx (Medications):',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: MediColors.textMuted),
                        ),
                        const SizedBox(height: 4),
                        ...(currentDoc['meds'] as List<String>).map((med) => Padding(
                              padding: const EdgeInsets.only(bottom: 4),
                              child: Text(
                                med,
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: MediColors.slate800),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            )),
                        const Spacer(),
                        const Align(
                          alignment: Alignment.bottomRight,
                          child: Text(
                            'Reg No: AIIA-74921\nVerified Clinical OPD Record',
                            textAlign: TextAlign.right,
                            style: TextStyle(fontSize: 9, color: MediColors.textMuted),
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Camera Reticles / Corner Target Brackets
                  Positioned.fill(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Container(
                        decoration: BoxDecoration(
                          border: Border.all(color: MediColors.emerald400.withValues(alpha: 0.8), width: 2.0),
                          borderRadius: MediDimensions.borderMd,
                        ),
                      ),
                    ),
                  ),

                  // Green Scan Crosshair HUD Label
                  Positioned(
                    top: 24,
                    right: 28,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: MediColors.emerald900.withValues(alpha: 0.85),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.crop_free, color: MediColors.emerald400, size: 14),
                          SizedBox(width: 4),
                          Text('DOCUMENT IN FRAME', style: TextStyle(color: MediColors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: MediDimensions.space20),

            // Select Clinical Prescription Selector
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Select Prescription to Scan (पर्ची बदलें):',
                style: MediTypography.caption.copyWith(fontWeight: FontWeight.w700),
              ),
            ),
            const SizedBox(height: MediDimensions.space8),
            SizedBox(
              height: 52,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _sampleDocs.length,
                separatorBuilder: (context, index) => const SizedBox(width: 8),
                itemBuilder: (context, index) {
                  final isSelected = index == _selectedDocIndex;
                  final doc = _sampleDocs[index];
                  return ChoiceChip(
                    label: Text(
                      doc['title'] as String,
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                        color: isSelected ? MediColors.white : MediColors.textPrimary,
                      ),
                    ),
                    selected: isSelected,
                    selectedColor: MediColors.brandPrimary,
                    backgroundColor: MediColors.slate100,
                    side: BorderSide(
                      color: isSelected ? MediColors.brandPrimary : MediColors.border,
                    ),
                    onSelected: (val) {
                      if (val) {
                        setState(() => _selectedDocIndex = index);
                      }
                    },
                  );
                },
              ),
            ),
            const SizedBox(height: MediDimensions.space24),
          ],
        ),
      ),
      bottomBar: SizedBox(
        height: 72,
        child: ElevatedButton.icon(
          onPressed: () {
            final encId = encounter.encounterId ?? 'enc-001';
            final filename = currentDoc['filename'] as String;
            intake.processDocument(encId, filename: filename);
            Navigator.of(context).pushNamed('/ocr_processing');
          },
          icon: const Icon(Icons.camera_rounded, size: 32),
          label: const Text(
            'Capture & Analyze (फोटो खींचें)',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700),
          ),
          style: ElevatedButton.styleFrom(
            backgroundColor: MediColors.brandPrimary,
            foregroundColor: MediColors.white,
            shape: RoundedRectangleBorder(borderRadius: MediDimensions.borderXl),
          ),
        ),
      ),
    );
  }
}
