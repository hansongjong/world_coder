import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'pos_screen_v3.dart';
class LoginScreen extends StatefulWidget { const LoginScreen({super.key}); @override State<LoginScreen> createState() => _S(); }
class _S extends State<LoginScreen> {
  final _u = TextEditingController(text: "owner"); final _p = TextEditingController(text: "1234");
  bool _l = false;
  Future<void> _f() async {
    setState(() => _l = true);
    final ok = await ApiService().login(_u.text, _p.text);
    setState(() => _l = false);
    if (ok && mounted) Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const PosScreenV3(storeId: 1)));
    else if(mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Login Failed")));
  }
  @override Widget build(BuildContext context) {
    return Scaffold(backgroundColor: Colors.blueGrey, body: Center(child: Card(child: Container(width: 300, padding: const EdgeInsets.all(20), child: Column(mainAxisSize: MainAxisSize.min, children: [
      const Text("Login", style: TextStyle(fontSize: 24)), const SizedBox(height: 20),
      TextField(controller: _u, decoration: const InputDecoration(labelText: "ID")),
      TextField(controller: _p, obscureText: true, decoration: const InputDecoration(labelText: "PW")),
      const SizedBox(height: 20),
      ElevatedButton(onPressed: _l ? null : _f, child: const Text("LOGIN"))
    ])))));
  }
}
