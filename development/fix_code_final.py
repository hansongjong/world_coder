import os
from pathlib import Path

# 1. 경로 설정 (사용자 환경 절대 경로)
ROOT_DIR = Path(r"D:\python_projects\world_coder\development\tg_pos_app")
LIB_DIR = ROOT_DIR / "lib"
SCREENS_DIR = LIB_DIR / "screens"
SERVICES_DIR = LIB_DIR / "services"
PROVIDERS_DIR = LIB_DIR / "providers"
WIDGETS_DIR = LIB_DIR / "widgets"

# 디렉토리 생성
for d in [SCREENS_DIR, SERVICES_DIR, PROVIDERS_DIR, WIDGETS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# 2. 파일 내용 정의 (문법 오류 수정됨)
# ---------------------------------------------------------

# [File 1] lib/main.dart
CODE_MAIN = r"""
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/cart_provider.dart';
import 'screens/login_screen.dart';

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
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        ),
        home: const LoginScreen(),
      ),
    );
  }
}
"""

# [File 2] lib/screens/login_screen.dart (문법 오류 수정)
CODE_LOGIN = r"""
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'pos_screen_v3.dart';

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
    
    // API 호출
    final success = await _api.login(_userController.text, _passController.text);
    
    setState(() => _isLoading = false);

    if (success) {
      if (!mounted) return;
      // 로그인 성공 시 POS 화면으로 이동
      Navigator.pushReplacement(
        context, 
        MaterialPageRoute(builder: (_) => const PosScreenV3(storeId: 1))
      );
    } else {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("로그인 실패: ID/PW를 확인하거나 서버를 켜주세요."))
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
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Container(
            width: 380,
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text("TG-POS SYSTEM", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                const SizedBox(height: 30),
                TextField(
                  controller: _userController,
                  decoration: const InputDecoration(
                    labelText: "Username",
                    prefixIcon: Icon(Icons.person),
                    border: OutlineInputBorder()
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _passController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: "Password",
                    prefixIcon: Icon(Icons.lock),
                    border: OutlineInputBorder()
                  ),
                ),
                const SizedBox(height: 30),
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.indigo,
                      foregroundColor: Colors.white,
                    ),
                    onPressed: _isLoading ? null : _handleLogin,
                    child: _isLoading 
                      ? const CircularProgressIndicator(color: Colors.white) 
                      : const Text("LOGIN", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  ),
                )
              ],
            ),
          ),
        ),
      ),
    );
  }
}
"""

# [File 3] lib/services/api_service.dart
CODE_API = r"""
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static const String baseUrl = "http://127.0.0.1:8001";
  final storage = const FlutterSecureStorage();

  Future<String> _getToken() async {
    return await storage.read(key: "access_token") ?? "";
  }

  Future<bool> login(String username, String password) async {
    try {
      final url = Uri.parse("$baseUrl/auth/token");
      final response = await http.post(
        url,
        body: {"username": username, "password": password},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await storage.write(key: "access_token", value: data["access_token"]);
        return true;
      }
      return false;
    } catch (e) {
      print("Login Error: $e");
      return false;
    }
  }

  Future<List<dynamic>> getMenu(int storeId) async {
    try {
      final token = await _getToken();
      final url = Uri.parse("$baseUrl/products/menu/$storeId");
      final response = await http.get(url, headers: {"Authorization": "Bearer $token"});
      
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  Future<void> placeOrder(Map<String, dynamic> data) async {
    final token = await _getToken();
    final url = Uri.parse("$baseUrl/orders/place");
    await http.post(
      url,
      headers: {
        "Authorization": "Bearer $token",
        "Content-Type": "application/json"
      },
      body: jsonEncode(data),
    );
  }
}
"""

# [File 4] lib/providers/cart_provider.dart
CODE_CART = r"""
import 'package:flutter/material.dart';

class CartItem {
  final int productId;
  final String name;
  final int price;
  int quantity;

  CartItem({
    required this.productId,
    required this.name,
    required this.price,
    this.quantity = 1,
  });
}

class CartProvider with ChangeNotifier {
  final List<CartItem> _items = [];

  List<CartItem> get items => _items;

  int get totalAmount {
    return _items.fold(0, (sum, item) => sum + (item.price * item.quantity));
  }

  void addToCart(int id, String name, int price) {
    final index = _items.indexWhere((item) => item.productId == id);
    if (index >= 0) {
      _items[index].quantity++;
    } else {
      _items.add(CartItem(productId: id, name: name, price: price));
    }
    notifyListeners();
  }

  void removeFromCart(int index) {
    _items.removeAt(index);
    notifyListeners();
  }

  void clear() {
    _items.clear();
    notifyListeners();
  }
}
"""

# [File 5] lib/screens/pos_screen_v3.dart (최소화 버전)
CODE_POS = r"""
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../providers/cart_provider.dart';

class PosScreenV3 extends StatefulWidget {
  final int storeId;
  const PosScreenV3({super.key, required this.storeId});

  @override
  State<PosScreenV3> createState() => _PosScreenV3State();
}

class _PosScreenV3State extends State<PosScreenV3> {
  final ApiService _api = ApiService();
  List<dynamic> _menu = [];

  @override
  void initState() {
    super.initState();
    _loadMenu();
  }

  Future<void> _loadMenu() async {
    final data = await _api.getMenu(widget.storeId);
    setState(() => _menu = data);
  }

  Future<void> _pay() async {
    final cart = context.read<CartProvider>();
    if (cart.items.isEmpty) return;

    try {
      await _api.placeOrder({
        "store_id": widget.storeId,
        "table_no": "POS",
        "items": cart.items.map((e) => {"product_id": e.productId, "quantity": e.quantity}).toList()
      });
      cart.clear();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("결제 완료!")));
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    final currency = NumberFormat("#,###", "ko_KR");
    
    return Scaffold(
      appBar: AppBar(title: const Text("TG-POS"), backgroundColor: Colors.indigo, foregroundColor: Colors.white),
      body: Row(
        children: [
          Expanded(
            flex: 2,
            child: ListView.builder(
              itemCount: _menu.length,
              itemBuilder: (ctx, i) {
                final cat = _menu[i];
                return Column(
                  children: [
                    Text(cat['category_name'], style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                    ... (cat['items'] as List).map((p) => ListTile(
                      title: Text(p['name']),
                      subtitle: Text("${currency.format(p['price'])}원"),
                      onTap: () => context.read<CartProvider>().addToCart(p['id'], p['name'], p['price']),
                    ))
                  ],
                );
              }
            )
          ),
          Expanded(
            flex: 1,
            child: Consumer<CartProvider>(
              builder: (ctx, cart, _) => Column(
                children: [
                  Expanded(
                    child: ListView.builder(
                      itemCount: cart.items.length,
                      itemBuilder: (ctx, i) => ListTile(
                        title: Text(cart.items[i].name),
                        trailing: IconButton(icon: const Icon(Icons.remove), onPressed: () => cart.removeFromCart(i))
                      )
                    )
                  ),
                  ElevatedButton(onPressed: _pay, child: const Text("PAY"))
                ],
              )
            )
          )
        ],
      ),
    );
  }
}
"""

# ---------------------------------------------------------
# 3. 파일 쓰기
# ---------------------------------------------------------
files = {
    LIB_DIR / "main.dart": CODE_MAIN,
    SCREENS_DIR / "login_screen.dart": CODE_LOGIN,
    SERVICES_DIR / "api_service.dart": CODE_API,
    PROVIDERS_DIR / "cart_provider.dart": CODE_CART,
    SCREENS_DIR / "pos_screen_v3.dart": CODE_POS,
}

print("[*] Fixing Flutter Source Code...")
for path, content in files.items():
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"    [FIXED] {path.name}")
    except Exception as e:
        print(f"    [FAIL] {path.name}: {e}")

print("\n[SUCCESS] All files repaired. You can run 'run_pos.bat' now.")