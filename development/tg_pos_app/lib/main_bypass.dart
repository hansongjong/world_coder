import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'providers/cart_provider.dart';
import 'screens/pos_screen_v3.dart';
import 'services/api_service.dart';

void main() async {
  // 앱 시작 전 비동기 작업 허용
  WidgetsFlutterBinding.ensureInitialized();
  
  // 1. 강제 로그인 시도 (토큰 확보)
  final api = ApiService();
  try {
    print("Attempting Auto-Login...");
    final success = await api.login("owner", "1234");
    if (success) {
      print("Auto-Login Success!");
    } else {
      print("Auto-Login Failed. Is Server Running?");
    }
  } catch (e) {
    print("Auto-Login Error: $e");
  }

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
        title: 'TG-POS (Bypass Mode)',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        ),
        // [FIX] 로그인 화면 건너뛰고 바로 POS 화면 진입
        home: const PosScreenV3(storeId: 1),
      ),
    );
  }
}