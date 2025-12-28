import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'providers/cart_provider.dart';
import 'providers/store_config_provider.dart';
import 'screens/login_screen.dart';
import 'l10n/app_localizations.dart';

// 테스트 모드 설정
const bool kTestMode = false;  // true: 자동 로그인, false: 일반 로그인

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
        ChangeNotifierProvider(create: (_) => StoreConfigProvider()),
      ],
      child: MaterialApp(
        title: 'TG-POS',
        debugShowCheckedModeBanner: false,
        // 다국어 설정 (한국어 기본)
        locale: const Locale('ko'),
        supportedLocales: const [
          Locale('ko'), // 한국어
          Locale('en'), // 영어
        ],
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
          fontFamily: 'NotoSansKR',
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFF1E293B),
            foregroundColor: Colors.white,
            elevation: 0,
          ),
        ),
        home: const LoginScreen(),
      ),
    );
  }
}
