import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/cart_provider.dart';
import 'screens/login_screen.dart'; // 로그인 스크린 별도 구현 가정 (코드량 제한으로 생략했으나 구조상 필요)
import 'screens/pos_screen.dart';

void main() {
  runApp(const TgPosApp());
}

class TgPosApp extends StatelessWidget {
  const TgPosApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => CartProvider()),
      ],
      child: MaterialApp(
        title: 'TG-POS',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        // 데모용으로 StoreID=1 로 고정하여 POS 화면 진입 (실제론 LoginScreen 먼저)
        home: const PosScreen(storeId: 1), 
      ),
    );
  }
}