import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/cart_provider.dart';
import 'screens/login_screen.dart';
void main() { runApp(const App()); }
class App extends StatelessWidget { const App({super.key}); @override Widget build(BuildContext context) { return MultiProvider(providers: [ChangeNotifierProvider(create: (_) => CartProvider())], child: MaterialApp(title: 'TG-POS', theme: ThemeData(primarySwatch: Colors.blue), home: const LoginScreen())); } }
