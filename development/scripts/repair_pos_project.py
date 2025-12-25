import os
from pathlib import Path

# 프로젝트 경로 설정
BASE_DIR = Path(__file__).resolve().parents[2] / "tg_pos_app"
LIB_DIR = BASE_DIR / "lib"

# --- [1. pubspec.yaml] ---
PUBSPEC = """name: tg_pos_app
description: TG-SYSTEM Windows POS
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: ">=3.0.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.0.5
  flutter_secure_storage: ^9.0.0
  shared_preferences: ^2.2.0
  intl: ^0.18.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0

flutter:
  uses-material-design: true
"""

# --- [2. main.dart] ---
MAIN_DART = """import 'package:flutter/material.dart';
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
        title: 'TG-POS Enterprise',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
          scaffoldBackgroundColor: Colors.grey[100],
        ),
        home: const LoginScreen(),
      ),
    );
  }
}
"""

# --- [3. api_service.dart] ---
API_SERVICE = """import 'dart:convert';
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
      print("Login Failed: ${response.body}");
      return false;
    } catch (e) {
      print("Login Network Error: $e");
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
      print("Get Menu Error: $e");
      return [];
    }
  }

  Future<void> placeOrder(Map<String, dynamic> data) async {
    final token = await _getToken();
    final url = Uri.parse("$baseUrl/orders/place");
    final response = await http.post(
      url,
      headers: {
        "Authorization": "Bearer $token",
        "Content-Type": "application/json"
      },
      body: jsonEncode(data),
    );

    if (response.statusCode != 200) {
      throw Exception("Order Failed: ${response.body}");
    }
  }

  Future<List<dynamic>> getReservations(int storeId) async {
    try {
      final token = await _getToken();
      final url = Uri.parse("$baseUrl/booking/list/$storeId");
      final response = await http.get(url, headers: {"Authorization": "Bearer $token"});
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return [];
    } catch (e) {
      return [];
    }
  }
}
"""

# --- [4. cart_provider.dart] ---
CART_PROVIDER = """import 'package:flutter/material.dart';

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

# --- [5. login_screen.dart] ---
LOGIN_SCREEN = """import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'pos_screen_v3.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController(text: "owner");
  final _passwordController = TextEditingController(text: "1234");
  final _api = ApiService();
  bool _isLoading = false;

  Future<void> _login() async {
    setState(() => _isLoading = true);
    
    final success = await _api.login(
      _usernameController.text, 
      _passwordController.text
    );
    
    setState(() => _isLoading = false);

    if (success) {
      if (!mounted) return;
      Navigator.pushReplacement(
        context, 
        MaterialPageRoute(builder: (_) => const PosScreenV3(storeId: 1))
      );
    } else {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("로그인 실패. 서버 상태를 확인하세요."))
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1E293B),
      body: Center(
        child: Container(
          width: 400,
          padding: const EdgeInsets.all(40),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: const [BoxShadow(blurRadius: 20, color: Colors.black26)],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                "TG-POS SYSTEM",
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              const SizedBox(height: 10),
              const Text("Store Management Client", style: TextStyle(color: Colors.grey)),
              const SizedBox(height: 40),
              TextField(
                controller: _usernameController,
                decoration: const InputDecoration(
                  labelText: "Username",
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person),
                ),
              ),
              const SizedBox(height: 20),
              TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: "Password",
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.lock),
                ),
              ),
              const SizedBox(height: 30),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF3B82F6),
                    foregroundColor: Colors.white,
                  ),
                  onPressed: _isLoading ? null : _login,
                  child: _isLoading 
                    ? const CircularProgressIndicator(color: Colors.white) 
                    : const Text("LOGIN", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
"""

# --- [6. pos_screen_v3.dart] ---
# [FIX] 복잡한 GridView 로직을 단순화하고, 메뉴를 Flatten 리스트로 변환하여 처리
POS_SCREEN = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../providers/cart_provider.dart';
import '../widgets/payment_modal.dart';
import '../widgets/receipt_dialog.dart';
import 'reservation_screen.dart';

class PosScreenV3 extends StatefulWidget {
  final int storeId;
  const PosScreenV3({super.key, required this.storeId});

  @override
  State<PosScreenV3> createState() => _PosScreenV3State();
}

class _PosScreenV3State extends State<PosScreenV3> {
  final _api = ApiService();
  
  // UI용으로 변환된 단일 상품 리스트
  List<Map<String, dynamic>> _flatProducts = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadMenu();
  }

  Future<void> _loadMenu() async {
    try {
      final rawMenu = await _api.getMenu(widget.storeId);
      final List<Map<String, dynamic>> flatList = [];
      
      // 카테고리별 상품을 하나의 리스트로 평탄화 (단순화)
      for (var cat in rawMenu) {
        for (var item in cat['items']) {
          flatList.add({
            "id": item['id'],
            "name": item['name'],
            "price": item['price'],
            "category": cat['category_name']
          });
        }
      }
      
      setState(() {
        _flatProducts = flatList;
        _isLoading = false;
      });
    } catch (e) {
      print("Error loading menu: $e");
      setState(() => _isLoading = false);
    }
  }

  void _showPaymentModal() {
    final cart = context.read<CartProvider>();
    if (cart.items.isEmpty) return;

    showDialog(
      context: context,
      builder: (_) => PaymentModal(
        totalAmount: cart.totalAmount,
        onPaymentComplete: (method, received, change) => _processOrder(method, received, change),
      )
    );
  }

  Future<void> _processOrder(String method, int received, int change) async {
    final cart = context.read<CartProvider>();
    
    final orderData = {
      "store_id": widget.storeId,
      "table_no": "POS-01",
      "items": cart.items.map((e) => {
        "product_id": e.productId, 
        "quantity": e.quantity
      }).toList()
    };

    try {
      await _api.placeOrder(orderData);
      
      // 영수증용 데이터 백업
      final itemsBackup = List.from(cart.items);
      final totalBackup = cart.totalAmount;
      final orderId = "ORD-${DateTime.now().millisecondsSinceEpoch}";
      
      cart.clear();

      if (!mounted) return;
      
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (_) => ReceiptDialog(
          orderId: orderId,
          totalAmount: totalBackup,
          method: method,
          received: received,
          change: change,
          items: itemsBackup
        )
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("주문 실패: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    final currency = NumberFormat("#,###", "ko_KR");

    return Scaffold(
      appBar: AppBar(
        title: const Text("TG-POS Pro", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)), 
        backgroundColor: const Color(0xFF1E293B),
        actions: [
          IconButton(
            icon: const Icon(Icons.calendar_month, color: Colors.white),
            tooltip: "예약 확인",
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ReservationScreen(storeId: widget.storeId))),
          ),
          const SizedBox(width: 10),
        ],
      ),
      body: Row(
        children: [
          // Left Panel: Menu Grid
          Expanded(
            flex: 7,
            child: _isLoading 
              ? const Center(child: CircularProgressIndicator())
              : Padding(
                  padding: const EdgeInsets.all(10),
                  child: GridView.builder(
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 4,
                      childAspectRatio: 1.0,
                      crossAxisSpacing: 10,
                      mainAxisSpacing: 10,
                    ),
                    itemCount: _flatProducts.length,
                    itemBuilder: (ctx, i) {
                      final p = _flatProducts[i];
                      return Card(
                        elevation: 2,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        color: Colors.white,
                        child: InkWell(
                          borderRadius: BorderRadius.circular(12),
                          onTap: () => context.read<CartProvider>().addToCart(p['id'], p['name'], p['price']),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(p['name'], style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
                              const SizedBox(height: 8),
                              Text("${currency.format(p['price'])}원", style: const TextStyle(color: Colors.blue, fontWeight: FontWeight.bold)),
                              const SizedBox(height: 4),
                              Text(p['category'], style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
          ),
          
          // Right Panel: Cart
          Expanded(
            flex: 3,
            child: Container(
              color: Colors.white,
              border: const Border(left: BorderSide(color: Colors.black12)),
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.all(15),
                    color: const Color(0xFFF1F5F9),
                    width: double.infinity,
                    child: const Text("Current Order", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  ),
                  Expanded(
                    child: Consumer<CartProvider>(
                      builder: (ctx, cart, _) => ListView.separated(
                        itemCount: cart.items.length,
                        separatorBuilder: (_, __) => const Divider(height: 1),
                        itemBuilder: (ctx, i) {
                          final item = cart.items[i];
                          return ListTile(
                            title: Text(item.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Text("${currency.format(item.price)} x ${item.quantity}"),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(currency.format(item.price * item.quantity), style: const TextStyle(fontWeight: FontWeight.bold)),
                                IconButton(
                                  icon: const Icon(Icons.close, color: Colors.red, size: 20),
                                  onPressed: () => cart.removeFromCart(i),
                                )
                              ],
                            ),
                          );
                        },
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      boxShadow: [BoxShadow(offset: const Offset(0, -2), blurRadius: 10, color: Colors.black.withOpacity(0.05))]
                    ),
                    child: Column(
                      children: [
                        Consumer<CartProvider>(
                          builder: (ctx, cart, _) => Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text("Total", style: TextStyle(fontSize: 20, color: Colors.grey)),
                              Text("${currency.format(cart.totalAmount)}원", style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.blue)),
                            ],
                          )
                        ),
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          height: 60,
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF1E293B),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                            ),
                            onPressed: _showPaymentModal,
                            child: const Text("결제하기 (PAY)", style: TextStyle(fontSize: 20, color: Colors.white, fontWeight: FontWeight.bold)),
                          ),
                        )
                      ],
                    ),
                  )
                ],
              ),
            ),
          )
        ],
      ),
    );
  }
}
"""

# --- [7. reservation_screen.dart] ---
RESERVATION_SCREEN = """import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ReservationScreen extends StatefulWidget {
  final int storeId;
  const ReservationScreen({super.key, required this.storeId});

  @override
  State<ReservationScreen> createState() => _ReservationScreenState();
}

class _ReservationScreenState extends State<ReservationScreen> {
  final _api = ApiService();
  List<dynamic> _list = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final data = await _api.getReservations(widget.storeId);
    setState(() {
      _list = data;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("예약 현황")),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator())
        : _list.isEmpty 
          ? const Center(child: Text("예약 내역이 없습니다."))
          : ListView.builder(
              itemCount: _list.length,
              itemBuilder: (ctx, i) {
                final item = _list[i];
                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  child: ListTile(
                    leading: CircleAvatar(child: Text("${item['guest_count']}")),
                    title: Text(item['guest_name']),
                    subtitle: Text(item['reserved_at']),
                    trailing: Chip(label: Text(item['status'])),
                  ),
                );
              }
            ),
    );
  }
}
"""

# --- [8. payment_modal.dart] ---
PAYMENT_MODAL = """import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class PaymentModal extends StatefulWidget {
  final int totalAmount;
  final Function(String, int, int) onPaymentComplete;

  const PaymentModal({
    super.key, 
    required this.totalAmount, 
    required this.onPaymentComplete
  });

  @override
  State<PaymentModal> createState() => _PaymentModalState();
}

class _PaymentModalState extends State<PaymentModal> {
  String _method = "CARD";
  final TextEditingController _cashController = TextEditingController();
  int _change = 0;
  final currency = NumberFormat("#,###", "ko_KR");

  void _calculateChange(String value) {
    int received = int.tryParse(value) ?? 0;
    setState(() {
      _change = received - widget.totalAmount;
    });
  }

  void _submit() {
    int received = _method == "CASH" ? int.tryParse(_cashController.text) ?? 0 : widget.totalAmount;
    widget.onPaymentComplete(_method, received, _change);
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text("결제 수단 선택"),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Expanded(
                child: RadioListTile(
                  title: const Text("카드"),
                  value: "CARD", 
                  groupValue: _method, 
                  onChanged: (v) => setState(() => _method = v.toString())
                )
              ),
              Expanded(
                child: RadioListTile(
                  title: const Text("현금"),
                  value: "CASH", 
                  groupValue: _method, 
                  onChanged: (v) => setState(() => _method = v.toString())
                )
              ),
            ],
          ),
          if (_method == "CASH") ...[
            const SizedBox(height: 10),
            TextField(
              controller: _cashController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: "받은 금액", 
                border: OutlineInputBorder()
              ),
              onChanged: _calculateChange,
            ),
            const SizedBox(height: 10),
            Text(
              "거스름돈: ${currency.format(_change)}원", 
              style: TextStyle(
                fontWeight: FontWeight.bold, 
                color: _change < 0 ? Colors.red : Colors.green
              )
            ),
          ]
        ],
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text("취소")),
        ElevatedButton(onPressed: _submit, child: const Text("결제 완료")),
      ],
    );
  }
}
"""

# --- [9. receipt_dialog.dart] ---
RECEIPT_DIALOG = """import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../providers/cart_provider.dart';

class ReceiptDialog extends StatelessWidget {
  final String orderId;
  final int totalAmount;
  final String method;
  final int received;
  final int change;
  final List<CartItem> items;

  const ReceiptDialog({
    super.key,
    required this.orderId,
    required this.totalAmount,
    required this.method,
    required this.received,
    required this.change,
    required this.items
  });

  @override
  Widget build(BuildContext context) {
    final currency = NumberFormat("#,###", "ko_KR");
    
    return AlertDialog(
      title: const Center(child: Text("RECEIPT", style: TextStyle(fontWeight: FontWeight.bold))),
      content: SizedBox(
        width: 300,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Order No: $orderId", style: const TextStyle(fontSize: 12)),
            const Divider(),
            ...items.map((i) => Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("${i.name} x${i.quantity}"),
                Text(currency.format(i.price * i.quantity)),
              ],
            )),
            const Divider(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("Total", style: TextStyle(fontWeight: FontWeight.bold)),
                Text(currency.format(totalAmount), style: const TextStyle(fontWeight: FontWeight.bold)),
              ],
            ),
            if (method == "CASH") ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [const Text("Received"), Text(currency.format(received))],
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [const Text("Change"), Text(currency.format(change))],
              ),
            ],
            const SizedBox(height: 10),
            Center(child: Text("Method: $method")),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text("Close")),
      ],
    );
  }
}
"""

def repair_flutter_project():
    print(f"[*] Reparing Flutter Project at: {LIB_DIR}")
    
    # 1. 디렉토리 구조 생성
    for d in ["screens", "widgets", "services", "providers"]:
        (LIB_DIR / d).mkdir(parents=True, exist_ok=True)
    
    # 2. 파일 덮어쓰기
    files = {
        BASE_DIR / "pubspec.yaml": PUBSPEC,
        LIB_DIR / "main.dart": MAIN_DART,
        LIB_DIR / "services/api_service.dart": API_SERVICE,
        LIB_DIR / "providers/cart_provider.dart": CART_PROVIDER,
        LIB_DIR / "screens/login_screen.dart": LOGIN_SCREEN,
        LIB_DIR / "screens/pos_screen_v3.dart": POS_SCREEN,
        LIB_DIR / "screens/reservation_screen.dart": RESERVATION_SCREEN,
        LIB_DIR / "widgets/payment_modal.dart": PAYMENT_MODAL,
        LIB_DIR / "widgets/receipt_dialog.dart": RECEIPT_DIALOG,
    }
    
    for path, content in files.items():
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"    [OK] Writen: {path.name}")
        except Exception as e:
            print(f"    [FAIL] {path.name}: {e}")

if __name__ == "__main__":
    repair_flutter_project()