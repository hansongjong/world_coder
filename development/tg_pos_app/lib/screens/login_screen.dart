
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'pos_screen_v3.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _u = TextEditingController(text: "owner");
  final _p = TextEditingController(text: "1234");
  final _api = ApiService();
  bool _l = false;

  Future<void> _f() async {
    setState(() => _l = true);
    final ok = await _api.login(_u.text, _p.text);
    setState(() => _l = false);
    if (ok && mounted) Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const PosScreenV3(storeId: 1)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(child: ElevatedButton(onPressed: _f, child: const Text("LOGIN")))
    );
  }
}
