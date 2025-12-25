import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'pos_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _userController = TextEditingController(text: "owner");
  final TextEditingController _passController = TextEditingController(text: "1234");
  final ApiService _api = ApiService();
  bool _isLoading = false;

  Future<void> _handleLogin() async {
    setState(() => _isLoading = true);
    final success = await _api.login(_userController.text, _passController.text);
    setState(() => _isLoading = false);

    if (success) {
      if (!mounted) return;
      Navigator.pushReplacement(
        context, 
        MaterialPageRoute(builder: (_) => const PosScreen(storeId: 1))
      );
    } else {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Login Failed. Check Server."))
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blueGrey[900],
      body: Center(
        child: Card(
          elevation: 8,
          child: Container(
            width: 350,
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text("TG-POS", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                const SizedBox(height: 30),
                TextField(controller: _userController, decoration: const InputDecoration(labelText: "ID", border: OutlineInputBorder())),
                const SizedBox(height: 16),
                TextField(controller: _passController, obscureText: true, decoration: const InputDecoration(labelText: "PW", border: OutlineInputBorder())),
                const SizedBox(height: 30),
                ElevatedButton(
                  onPressed: _isLoading ? null : _handleLogin,
                  child: const Text("LOGIN"),
                )
              ],
            ),
          ),
        ),
      ),
    );
  }
}