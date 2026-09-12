import 'package:flutter/material.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/hospital_service_card.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 20 — Hospital Services & Facilities Directory
/// Pharmacy, Lab, Radiology, and Dispensary information
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 20)
class ServicesScreen extends StatelessWidget {
  const ServicesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final services = [
      {
        'title': 'OPD Pharmacy (दवाखाना)',
        'floor': 'Ground Floor, Counter 3-6',
        'waitTime': '5 min',
        'icon': Icons.local_pharmacy_rounded,
      },
      {
        'title': 'Pathology & Blood Lab (जाँच लैब)',
        'floor': '1st Floor, Room 114',
        'waitTime': '12 min',
        'icon': Icons.biotech_rounded,
      },
      {
        'title': 'Injection & Dressing Room',
        'floor': 'Ground Floor, Room 12',
        'waitTime': '3 min',
        'icon': Icons.healing_rounded,
      },
      {
        'title': 'Radiology & X-Ray (एक्स-रे)',
        'floor': 'Basement 1, Wing B',
        'waitTime': '15 min',
        'icon': Icons.personal_injury_rounded,
      },
      {
        'title': 'AYUSH Herbal Dispensary (आयुष औषधि)',
        'floor': 'Ground Floor, Room 8',
        'waitTime': '4 min',
        'icon': Icons.eco_rounded,
      },
    ];

    return MediScaffold(
      title: 'Hospital Services',
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Hospital Facilities & Counters',
            style: MediTypography.headlineLarge,
          ),
          const SizedBox(height: MediDimensions.space8),
          const Text(
            'Live wait times and locations for essential hospital counters.',
            style: TextStyle(fontSize: 16),
          ),
          const SizedBox(height: MediDimensions.space20),
          Expanded(
            child: ListView.builder(
              itemCount: services.length,
              itemBuilder: (context, index) {
                final s = services[index];
                return HospitalServiceCard(
                  title: s['title'] as String,
                  floor: s['floor'] as String,
                  waitTime: s['waitTime'] as String,
                  icon: s['icon'] as IconData,
                  onDirectionsTap: () => Navigator.of(context).pushNamed('/map'),
                );
              },
            ),
          ),
        ],
      ),
      bottomBar: PrimaryActionButton(
        label: 'View Interactive Hospital Map',
        icon: Icons.map_rounded,
        onPressed: () => Navigator.of(context).pushNamed('/map'),
      ),
    );
  }
}
