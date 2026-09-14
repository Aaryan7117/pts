import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';
import '../../core/widgets/secondary_button.dart';
import '../../data/models/queue_status.dart';
import '../../data/repositories/intake_repository.dart';
import '../../data/datasources/mock_datasource.dart';

/// Screen 19 — Department Routing & Queue Token Tracker
/// Large high-visibility token card with live position and wait estimate
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 19)
class QueueScreen extends StatefulWidget {
  const QueueScreen({super.key});

  @override
  State<QueueScreen> createState() => _QueueScreenState();
}

class _QueueScreenState extends State<QueueScreen> {
  final IntakeRepository _repository = IntakeRepository();
  QueueStatusResponse? _queueData;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fetchQueueStatus();
    });
  }

  Future<void> _fetchQueueStatus() async {
    final encounter = context.read<EncounterProvider>();
    final token = encounter.tokenNumber ?? 'A-104';

    setState(() => _isLoading = true);
    try {
      final res = await _repository.getQueueStatus(token);
      if (mounted) {
        setState(() {
          _queueData = res;
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _queueData = MockDataSource.getMockQueueStatus();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final encounter = context.watch<EncounterProvider>();

    final token = encounter.tokenNumber ?? 'A-104';
    final queueData = _queueData ?? MockDataSource.getMockQueueStatus();

    return MediScaffold(
      title: lang.translate('queue_title'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Oversized Token Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(MediDimensions.space24),
              decoration: BoxDecoration(
                color: MediColors.surface,
                borderRadius: MediDimensions.borderXl,
                border: Border.all(color: MediColors.brandPrimary, width: 2.5),
                boxShadow: MediDimensions.elevation3,
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                        decoration: BoxDecoration(
                          color: MediColors.blue50,
                          borderRadius: MediDimensions.borderSm,
                        ),
                        child: Text(
                          encounter.department.toUpperCase(),
                          style: const TextStyle(
                            color: MediColors.brandPrimary,
                            fontWeight: FontWeight.w800,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      IconButton(
                        onPressed: _isLoading ? null : _fetchQueueStatus,
                        icon: _isLoading
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.refresh_rounded, color: MediColors.brandPrimary),
                        tooltip: 'Refresh Queue',
                      ),
                    ],
                  ),
                  const SizedBox(height: MediDimensions.space16),
                  Text(
                    lang.translate('your_queue_token'),
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: MediColors.textMuted,
                      letterSpacing: 1.5,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    token,
                    style: const TextStyle(
                      fontSize: 64,
                      fontWeight: FontWeight.w900,
                      color: MediColors.brandPrimary,
                      letterSpacing: 2.0,
                    ),
                  ),
                  const SizedBox(height: MediDimensions.space8),
                  Text(
                    queueData.doctorRoom ?? 'Room 102 (Dr. Verma)',
                    style: MediTypography.headlineMedium.copyWith(fontSize: 20),
                  ),
                  const Divider(height: 36),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      Column(
                        children: [
                          Text(
                            lang.translate('patients_ahead'),
                            style: const TextStyle(fontSize: 14, color: MediColors.textMuted),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${queueData.patientsAhead}',
                            style: const TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: MediColors.textPrimary,
                            ),
                          ),
                        ],
                      ),
                      Container(height: 40, width: 1, color: MediColors.border),
                      Column(
                        children: [
                          Text(
                            lang.translate('est_wait'),
                            style: const TextStyle(fontSize: 14, color: MediColors.textMuted),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '~${queueData.estimatedWaitMinutes} min',
                            style: const TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: MediColors.emerald800,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: MediDimensions.space24),
            // Hospital Services & Wayfinding Shortcuts
            Row(
              children: [
                Expanded(
                  child: SecondaryActionButton(
                    label: lang.translate('hospital_services'),
                    icon: Icons.local_pharmacy_rounded,
                    onPressed: () => Navigator.of(context).pushNamed('/services'),
                  ),
                ),
                const SizedBox(width: MediDimensions.space12),
                Expanded(
                  child: SecondaryActionButton(
                    label: lang.translate('hospital_map'),
                    icon: Icons.map_rounded,
                    onPressed: () => Navigator.of(context).pushNamed('/map'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
      bottomBar: PrimaryActionButton(
        label: lang.translate('finish_print_ticket'),
        icon: Icons.print_rounded,
        onPressed: () => Navigator.of(context).pushNamed('/completion'),
      ),
    );
  }
}
