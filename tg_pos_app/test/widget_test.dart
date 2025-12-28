import 'package:flutter_test/flutter_test.dart';
import 'package:tg_pos_app/main.dart';

void main() {
  testWidgets('TG-POS app starts', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const TgPosApp());

    // Verify the app shows login screen
    expect(find.text('TG-POS'), findsOneWidget);
    expect(find.text('LOGIN'), findsOneWidget);
  });
}
