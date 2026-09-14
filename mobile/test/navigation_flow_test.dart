import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/app.dart';
import 'package:mobile/core/widgets/primary_button.dart';

void main() {
  testWidgets('MediKiosk complete mock flow navigation test in English', (WidgetTester tester) async {
    await tester.pumpWidget(const MediKioskApp());
    await tester.pumpAndSettle();

    // 1. Welcome Screen
    expect(find.byType(PrimaryActionButton), findsOneWidget);
    await tester.tap(find.byType(PrimaryActionButton));
    await tester.pumpAndSettle();

    // 2. Language Selection Screen — Select English
    expect(find.text('English'), findsOneWidget);
    await tester.tap(find.text('English'));
    await tester.pumpAndSettle();

    // Verify language change reflected immediately on screen
    expect(find.text('Select Your Language'), findsWidgets);
    expect(find.text('I AGREE & CONTINUE'), findsOneWidget);
    await tester.tap(find.byType(PrimaryActionButton));
    await tester.pumpAndSettle();

    // 3. Consent Screen
    expect(find.text('Patient Consent & Privacy Notice'), findsWidgets);
    await tester.tap(find.byType(PrimaryActionButton));
    await tester.pumpAndSettle();

    // 4. Identification Screen
    expect(find.text('Patient Identification'), findsWidgets);
    // Tap Skip as guest
    await tester.tap(find.text('SKIP & PROCEED AS GUEST'));
    await tester.pumpAndSettle();

    // 5. Care Stream Screen
    expect(find.text('Select Reason for Visit'), findsWidgets);
    expect(find.text('General Medicine'), findsWidgets);
    await tester.tap(find.byType(PrimaryActionButton));
    await tester.pumpAndSettle();

    // 6. Voice Intake Screen
    expect(find.text('Tell Us What Is Bothering You'), findsWidgets);

    // 7. Test Navigation to Text Intake Screen
    await tester.tap(find.text('Prefer typing? Tap here to type symptoms'));
    await tester.pumpAndSettle();

    // Verify Text Intake Screen is displayed in English
    expect(find.text('Describe Your Symptoms'), findsWidgets);
    expect(find.text('Submit Symptoms & Analyze'), findsOneWidget);

    // Enter symptom into TextField
    await tester.enterText(find.byType(TextField), 'I have severe fever and headache for two days');
    await tester.pumpAndSettle();

    // Submit symptoms to AI processing
    await tester.tap(find.byType(PrimaryActionButton));
    await tester.pumpAndSettle();

    // Verify reached follow-up question screen after processing
    expect(find.text('Follow-Up Question'), findsOneWidget);

    // 8. Confirm Follow-up answer
    await tester.tap(find.text('Confirm Answer'));
    await tester.pumpAndSettle();

    // 9. Summary Confirmation Screen
    expect(find.text('Please Confirm What We Understood'), findsWidgets);
    await tester.tap(find.text('Confirm & Next'));
    await tester.pumpAndSettle();

    // 10. Document Intro Screen
    expect(find.text('Scan Your Old Prescription or Reports'), findsWidgets);
    await tester.tap(find.text("I Don't Have Documents / Skip"));
    await tester.pumpAndSettle();

    // 11. Vitals Screen
    expect(find.text('Vital Signs Measurement'), findsWidgets);
    await tester.tap(find.text('Confirm Vitals & Next'));
    await tester.pumpAndSettle();

    // 12. Queue Screen
    expect(find.text('Your OPD Token Number'), findsWidgets);
    await tester.tap(find.text('Finish Intake & Print Ticket'));
    await tester.pumpAndSettle();

    // 13. Completion Screen
    expect(find.text('Intake Successfully Completed!'), findsWidgets);
    expect(find.text('FINISH & RESET SCREEN'), findsOneWidget);
  });

  testWidgets('Language selection updates UI across Tamil, Telugu, and Marathi', (WidgetTester tester) async {
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(const MediKioskApp());
    await tester.pumpAndSettle();

    // Go to Language Selection Screen
    await tester.tap(find.byType(PrimaryActionButton));
    await tester.pumpAndSettle();

    // Select Tamil
    await tester.ensureVisible(find.text('தமிழ்'));
    await tester.tap(find.text('தமிழ்'));
    await tester.pumpAndSettle();

    // Assert Tamil translation appears on screen
    expect(find.text('உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்'), findsWidgets);
    expect(find.text('நான் ஒப்புக்கொள்கிறேன்'), findsOneWidget);

    // Select Telugu
    await tester.ensureVisible(find.text('తెలుగు'));
    await tester.tap(find.text('తెలుగు'));
    await tester.pumpAndSettle();

    // Assert Telugu translation appears
    expect(find.text('మీ భాషను ఎంచుకోండి'), findsWidgets);
    expect(find.text('నేను అంగీకరిస్తున్నాను'), findsOneWidget);

    // Select Marathi
    await tester.ensureVisible(find.text('मराठी'));
    await tester.tap(find.text('मराठी'));
    await tester.pumpAndSettle();

    // Assert Marathi translation appears
    expect(find.text('आपली भाषा निवडा'), findsWidgets);
    expect(find.text('मी सहमत आहे आणि पुढे जा'), findsOneWidget);
  });
}
