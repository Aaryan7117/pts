import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'state/language_provider.dart';
import 'state/encounter_provider.dart';
import 'state/intake_provider.dart';
import 'state/connectivity_provider.dart';
import 'theme/app_theme.dart';
import 'router.dart';

/// Root MediKiosk Application Widget
/// Configures State Management Providers, Healthcare Theme, and Route Graph
class MediKioskApp extends StatelessWidget {
  const MediKioskApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => LanguageProvider()),
        ChangeNotifierProvider(create: (_) => EncounterProvider()),
        ChangeNotifierProvider(create: (_) => IntakeProvider()),
        ChangeNotifierProvider(create: (_) => ConnectivityProvider()),
      ],
      child: MaterialApp(
        title: 'MediKiosk',
        debugShowCheckedModeBanner: false,
        theme: MediKioskTheme.lightTheme,
        initialRoute: MediRouter.initialRoute,
        routes: MediRouter.routes,
      ),
    );
  }
}
