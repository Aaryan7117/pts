import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/app/app.dart';

void main() {
  testWidgets('MediKiosk Welcome Screen smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MediKioskApp());
    await tester.pumpAndSettle();

    // Verify Welcome title and Start Button are present
    expect(find.textContaining('MediKiosk'), findsWidgets);
    expect(find.textContaining('START INTAKE'), findsOneWidget);
  });
}
