import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 13 — Document Camera & Clinical Scanner
/// Real camera / gallery image capture using image_picker.
/// The selected image bytes are sent to the backend /api/documents/upload for OCR.
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 13)
class DocumentCameraScreen extends StatefulWidget {
  const DocumentCameraScreen({super.key});

  @override
  State<DocumentCameraScreen> createState() => _DocumentCameraScreenState();
}

class _DocumentCameraScreenState extends State<DocumentCameraScreen> {
  final ImagePicker _picker = ImagePicker();
  XFile? _pickedFile;
  String? _errorMessage;

  Future<void> _pickImage(ImageSource source) async {
    setState(() {
      _errorMessage = null;
    });
    try {
      final XFile? file = await _picker.pickImage(
        source: source,
        imageQuality: 90,
        maxWidth: 2048,
        maxHeight: 2048,
      );
      if (file != null) {
        setState(() {
          _pickedFile = file;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Could not access camera/gallery. Please grant permissions in Settings.';
      });
    }
  }

  Future<void> _captureAndAnalyze(BuildContext context) async {
    final intake = context.read<IntakeProvider>();
    final encounter = context.read<EncounterProvider>();

    final encId = encounter.encounterId;
    if (encId == null || encId.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Session not started. Please go back and begin a new intake.'),
          backgroundColor: MediColors.triageRed,
        ),
      );
      return;
    }

    if (_pickedFile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please capture or select a document first.'),
          backgroundColor: MediColors.warning,
        ),
      );
      return;
    }

    final imageBytes = await File(_pickedFile!.path).readAsBytes();
    final filename = _pickedFile!.name.isNotEmpty ? _pickedFile!.name : 'prescription.jpg';

    // Cache captured image locally for visual verification and inspection
    intake.setCapturedImage(imageBytes, _pickedFile!.path);
    intake.processDocument(encId, imageBytes: imageBytes, filename: filename);

    if (context.mounted) {
      Navigator.of(context).pushNamed('/ocr_processing');
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();

    return MediScaffold(
      title: 'Scan Prescription',
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: MediDimensions.space12),
            Text(
              'Scan Your Prescription or Lab Report',
              style: MediTypography.headlineMedium.copyWith(fontSize: 22),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space8),
            const Text(
              'Take a photo or select from your gallery for instant AI extraction',
              style: TextStyle(fontSize: 15, color: MediColors.textMuted),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space20),

            // Error banner
            if (_errorMessage != null)
              Container(
                padding: const EdgeInsets.all(MediDimensions.space12),
                decoration: BoxDecoration(
                  color: MediColors.triageTint,
                  borderRadius: MediDimensions.borderMd,
                  border: Border.all(color: MediColors.triageRed),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.warning_rounded, color: MediColors.triageRed, size: 24),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: MediColors.triageRed, fontWeight: FontWeight.w600),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, size: 20, color: MediColors.triageRed),
                      onPressed: () => setState(() => _errorMessage = null),
                    ),
                  ],
                ),
              ),
            if (_errorMessage != null) const SizedBox(height: MediDimensions.space16),

            // Document Preview / Viewfinder Frame
            Container(
              width: double.infinity,
              height: 300,
              decoration: BoxDecoration(
                color: _pickedFile == null ? MediColors.slate900 : MediColors.white,
                borderRadius: MediDimensions.borderLg,
                boxShadow: MediDimensions.elevation3,
                border: _pickedFile != null
                    ? Border.all(color: MediColors.emerald400, width: 2.5)
                    : null,
              ),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  if (_pickedFile != null)
                    // Real image preview
                    ClipRRect(
                      borderRadius: MediDimensions.borderLg,
                      child: Image.file(
                        File(_pickedFile!.path),
                        fit: BoxFit.contain,
                        width: double.infinity,
                        height: double.infinity,
                      ),
                    )
                  else ...[
                    // Empty viewfinder placeholder
                    Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.document_scanner_rounded,
                          size: 64,
                          color: MediColors.slate600,
                        ),
                        const SizedBox(height: MediDimensions.space12),
                        const Text(
                          'No document selected',
                          style: TextStyle(color: MediColors.slate500, fontSize: 15),
                        ),
                        const SizedBox(height: MediDimensions.space8),
                        const Text(
                          'Use buttons below to capture or choose',
                          style: TextStyle(color: MediColors.slate500, fontSize: 13),
                        ),
                      ],
                    ),
                    // Corner reticle brackets
                    Positioned.fill(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Container(
                          decoration: BoxDecoration(
                            border: Border.all(
                              color: MediColors.emerald400.withValues(alpha: 0.6),
                              width: 2.0,
                            ),
                            borderRadius: MediDimensions.borderMd,
                          ),
                        ),
                      ),
                    ),
                  ],

                  // "Change" button overlay when image is set
                  if (_pickedFile != null)
                    Positioned(
                      top: 10,
                      right: 10,
                      child: GestureDetector(
                        onTap: () => setState(() => _pickedFile = null),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          decoration: BoxDecoration(
                            color: MediColors.slate900.withValues(alpha: 0.75),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.refresh_rounded, color: MediColors.white, size: 16),
                              SizedBox(width: 4),
                              Text('Change', style: TextStyle(color: MediColors.white, fontSize: 13, fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                      ),
                    ),

                  // Confirmed badge
                  if (_pickedFile != null)
                    Positioned(
                      top: 10,
                      left: 10,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: MediColors.emerald800,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.check_circle_rounded, color: MediColors.white, size: 16),
                            SizedBox(width: 4),
                            Text('Document Ready', style: TextStyle(color: MediColors.white, fontSize: 13, fontWeight: FontWeight.bold)),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),

            const SizedBox(height: MediDimensions.space24),

            // Source selector: Camera vs Gallery
            Row(
              children: [
                Expanded(
                  child: _SourceButton(
                    icon: Icons.camera_alt_rounded,
                    label: 'Take Photo',
                    sublabel: 'Use camera now',
                    isSelected: false,
                    onTap: () => _pickImage(ImageSource.camera),
                  ),
                ),
                const SizedBox(width: MediDimensions.space12),
                Expanded(
                  child: _SourceButton(
                    icon: Icons.photo_library_rounded,
                    label: 'Gallery',
                    sublabel: 'Choose existing image',
                    isSelected: false,
                    onTap: () => _pickImage(ImageSource.gallery),
                  ),
                ),
              ],
            ),

            const SizedBox(height: MediDimensions.space24),
          ],
        ),
      ),
      bottomBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          PrimaryActionButton(
            label: _pickedFile == null
                ? 'Select a Document to Continue'
                : 'Analyze Prescription with AI',
            icon: _pickedFile == null ? Icons.camera_alt_rounded : Icons.biotech_rounded,
            onPressed: _pickedFile == null ? null : () => _captureAndAnalyze(context),
          ),
          const SizedBox(height: MediDimensions.space8),
          TextButton(
            onPressed: () => Navigator.of(context).pushNamed('/vitals'),
            child: const Text(
              'Skip — No document to scan',
              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: MediColors.textMuted),
            ),
          ),
        ],
      ),
    );
  }
}

/// Compact tap target for Camera / Gallery source selection
class _SourceButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final String sublabel;
  final bool isSelected;
  final VoidCallback onTap;

  const _SourceButton({
    required this.icon,
    required this.label,
    required this.sublabel,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: isSelected ? MediColors.emerald50 : MediColors.surface,
      borderRadius: MediDimensions.borderLg,
      child: InkWell(
        onTap: onTap,
        borderRadius: MediDimensions.borderLg,
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: MediDimensions.space16,
            vertical: MediDimensions.space20,
          ),
          decoration: BoxDecoration(
            borderRadius: MediDimensions.borderLg,
            border: Border.all(
              color: isSelected ? MediColors.emerald400 : MediColors.border,
              width: isSelected ? 2.0 : 1.0,
            ),
          ),
          child: Column(
            children: [
              Icon(
                icon,
                size: 36,
                color: isSelected ? MediColors.emerald800 : MediColors.brandPrimary,
              ),
              const SizedBox(height: 8),
              Text(
                label,
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: isSelected ? MediColors.emerald800 : MediColors.textPrimary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 4),
              Text(
                sublabel,
                style: const TextStyle(fontSize: 12, color: MediColors.textMuted),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
