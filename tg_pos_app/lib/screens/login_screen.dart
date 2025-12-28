import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:provider/provider.dart';
import 'dart:io' show Platform;
import '../services/api_service.dart';
import '../providers/store_config_provider.dart';
import '../main.dart' show kTestMode;
import 'pos_screen.dart';
import 'store_selection_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    // 테스트 모드일 경우 자동 로그인
    if (kTestMode) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _login();
      });
    }
  }

  String get _platformName {
    if (kIsWeb) return 'Web';
    if (Platform.isWindows) return 'Windows';
    if (Platform.isAndroid) return 'Android';
    if (Platform.isIOS) return 'iOS';
    return 'Unknown';
  }

  Future<void> _login() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      // 1단계: 로그인 → 접근 가능한 매장 목록 받기
      final result = await ApiService().loginWithStores(
        _usernameController.text,
        _passwordController.text,
      );

      if (!mounted) return;

      if (result != null) {
        final userId = result['user_id'] as int;
        final username = result['username'] as String;
        final stores = List<Map<String, dynamic>>.from(result['stores']);

        if (stores.isEmpty) {
          setState(() => _errorMessage = '접근 가능한 매장이 없습니다');
          return;
        }

        // 매장이 1개면 바로 진입, 여러 개면 선택 화면으로
        if (stores.length == 1) {
          await _enterStore(userId, stores.first);
        } else {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (_) => StoreSelectionScreen(
                userId: userId,
                username: username,
                stores: stores,
              ),
            ),
          );
        }
      } else {
        setState(() => _errorMessage = '로그인 실패. 아이디/비밀번호를 확인하세요.');
      }
    } catch (e) {
      setState(() => _errorMessage = '연결 오류: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _enterStore(int userId, Map<String, dynamic> store) async {
    final storeId = store['store_id'] as int;

    final selectResult = await ApiService().selectStore(userId, storeId);
    if (!mounted) return;

    if (selectResult != null) {
      // Load store config
      await context.read<StoreConfigProvider>().loadConfig(storeId);

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => PosScreen(storeId: storeId),
        ),
      );
    } else {
      setState(() => _errorMessage = '매장 접속 실패');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1E293B),
      body: Center(
        child: SingleChildScrollView(
          child: Card(
            margin: const EdgeInsets.all(20),
            child: Container(
              width: 350,
              padding: const EdgeInsets.all(30),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Logo
                  const Icon(
                    Icons.point_of_sale,
                    size: 60,
                    color: Color(0xFF3B82F6),
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    'TG-POS',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1E293B),
                    ),
                  ),
                  Text(
                    'Platform: $_platformName',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 30),

                  // Username
                  TextField(
                    controller: _usernameController,
                    decoration: const InputDecoration(
                      labelText: '아이디',
                      prefixIcon: Icon(Icons.person),
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 15),

                  // Password
                  TextField(
                    controller: _passwordController,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: '비밀번호',
                      prefixIcon: Icon(Icons.lock),
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: (_) => _login(),
                  ),
                  const SizedBox(height: 20),

                  // Error Message
                  if (_errorMessage.isNotEmpty)
                    Container(
                      padding: const EdgeInsets.all(10),
                      margin: const EdgeInsets.only(bottom: 15),
                      decoration: BoxDecoration(
                        color: Colors.red[50],
                        borderRadius: BorderRadius.circular(5),
                      ),
                      child: Text(
                        _errorMessage,
                        style: TextStyle(color: Colors.red[700]),
                      ),
                    ),

                  // Login Button
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _login,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF3B82F6),
                        foregroundColor: Colors.white,
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Text(
                              '로그인',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Test account hints
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '테스트 계정',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.grey[700],
                            fontSize: 12,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'boss / 1234 (다중 매장)\n'
                          'cafe / 1234 (카페)\n'
                          'gym / 1234 (헬스장)\n'
                          'staff1 / 1234 (직원)',
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 11,
                            height: 1.5,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
}
