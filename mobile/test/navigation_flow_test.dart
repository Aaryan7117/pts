import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/app.dart';
import 'package:mobile/core/widgets/primary_button.dart';

void main() {
  testWidgets('MediKiosk complete mock flow navigation test', (WidgetTester tester) async {
    await tester.pumpWidget(const MediKioskApp());
    await tester.pumpAndSettle();

    // 1. Welcome Screen
    expect(find.textContaining('START INTAKE'), findsOneWidget);
    await tester.tap(find.byType(PrimaryActionButton));
    await tester.pumpAndSettle();

    // 2. Language Selection Screen
    expect(find.textContaining('अपनी भाषा चुनें'), findsWidgets);
    await tester.tap(find.byType(PrimaryActionButton));
    await tester.pumpAndSettle();

    // 3. Consent Screen
    expect(find.textContaining('सहमति'), findsWidgets);
    await tester.tap(find.byType(PrimaryActionButton));
    await tester.pumpAndSettle();

    // 4. Identification Screen
    expect(find.textContaining('पहचान'), findsWidgets);
    // Tap Skip as guest
    await tester.tap(find.textContaining('छोड़ें'));
    await tester.pumpAndSettle();

    // 5. Care Stream Screen
    expect(find.textContaining('विभाग'), findsWidgets);
    await tester.tap(find.byType(PrimaryActionButton));
    await tester.pumpAndSettle();

    // 6. Voice Intake Screen
    expect(find.textContaining('बोलकर'), findsWidgets);

    // 7. Test Navigation to Text Intake Screen
    await tester.tap(find.textContaining('लिखकर बताएं'));
    await tester.pumpAndSettle();

    // Verify Text Intake Screen is displayed
    expect(find.textContaining('Describe Your Symptoms'), findsOneWidget);
    expect(find.textContaining('Submit Symptoms & Analyze'), findsOneWidget);

    // Enter symptom into TextField
    await tester.enterText(find.byType(TextField), 'दो दिन से तेज बुखार है');
    await tester.pumpAndSettle();

    // Submit symptoms to AI processing
    await tester.tap(find.byType(PrimaryActionButton));
    await tester.pumpAndSettle();

    // Verify reached follow-up question screen after processing
    expect(find.textContaining('Follow-Up Question'), findsOneWidget);

    // 8. Confirm Follow-up answer
    await tester.tap(find.textContaining('Confirm Answer'));
    await tester.pumpAndSettle();

    // 9. Summary Confirmation Screen
    expect(find.textContaining('Confirm Information'), findsOneWidget);
    await tester.tap(find.textContaining('Confirm & Next'));
    await tester.pumpAndSettle();

    // 10. Document Intro Screen
    expect(find.textContaining('Scan Medical Documents'), findsOneWidget);
    await tester.tap(find.textContaining('पर्ची नहीं है'));
    await tester.pumpAndSettle();

    // 11. Vitals Screen
    expect(find.textContaining('Vitals'), findsWidgets);
    await tester.tap(find.textContaining('Confirm Vitals'));
    await tester.pumpAndSettle();

    // 12. Queue Screen
    expect(find.textContaining('OPD Queue Ticket'), findsOneWidget);
    await tester.tap(find.textContaining('Print Ticket'));
    await tester.pumpAndSettle();

    // 13. Completion Screen
    expect(find.textContaining('Intake Completed'), findsOneWidget);
    expect(find.textContaining('Finish & Reset Screen Now'), findsOneWidget);
  });
}
