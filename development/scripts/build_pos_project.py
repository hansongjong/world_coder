import os
from pathlib import Path

# 프로젝트 루트 설정
BASE_DIR = Path(__file__).resolve().parents[2] / "tg_pos_app"
LIB_DIR = BASE_DIR / "lib"

# --- [CONTENT VARIABLES] ---
PUBSPEC_CONTENT = """name: tg_pos_app
description: TG-SYSTEM Windows POS Client
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

API_SERVICE_CONTENT = """import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
class ApiService {
  static const String baseUrl = "http://127.0.0.1:8001";
  final storage = const FlutterSecureStorage();
  Future<String> _getToken() async => await storage.read(key: "access_token") ?? "";
  Future<bool> login(String u, String p) async {
    try {
      final res = await http.post(Uri.parse("$baseUrl/auth/token"), body: {"username": u, "password": p});
      if (res.statusCode == 200) {
        await storage.write(key: "access_token", value: jsonDecode(res.body)["access_token"]);
        return true;
      }
      return false;
    } catch(e) { return false; }
  }
  Future<List<dynamic>> getMenu(int id) async {
    final t = await _getToken();
    final res = await http.get(Uri.parse("$baseUrl/products/menu/$id"), headers: {"Authorization": "Bearer $t"});
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : [];
  }
  Future<void> placeOrder(Map<String, dynamic> d) async {
    final t = await _getToken();
    await http.post(Uri.parse("$baseUrl/orders/place"), headers: {"Authorization": "Bearer $t", "Content-Type": "application/json"}, body: jsonEncode(d));
  }
  Future<List<dynamic>> getReservations(int id) async {
    final t = await _getToken();
    final res = await http.get(Uri.parse("$baseUrl/booking/list/$id"), headers: {"Authorization": "Bearer $t"});
    return res.statusCode == 200 ? jsonDecode(res.body) : [];
  }
  Future<void> earnPoints(int id, String p, int a) async {
    final t = await _getToken();
    await http.post(Uri.parse("$baseUrl/membership/earn"), headers: {"Authorization": "Bearer $t", "Content-Type": "application/json"}, body: jsonEncode({"store_id": id, "user_phone": p, "amount": a}));
  }
}
"""

CART_PROVIDER_CONTENT = """import 'package:flutter/material.dart';
class CartItem { final int productId; final String name; final int price; int quantity; CartItem({required this.productId, required this.name, required this.price, this.quantity = 1}); }
class CartProvider with ChangeNotifier {
  final List<CartItem> _items = [];
  List<CartItem> get items => _items;
  int get totalAmount => _items.fold(0, (s, i) => s + (i.price * i.quantity));
  void addToCart(int id, String name, int price) {
    final idx = _items.indexWhere((i) => i.productId == id);
    if (idx >= 0) _items[idx].quantity++; else _items.add(CartItem(productId: id, name: name, price: price));
    notifyListeners();
  }
  void removeFromCart(int index) { _items.removeAt(index); notifyListeners(); }
  void clear() { _items.clear(); notifyListeners(); }
}
"""

# [중요] 누락되었던 login_screen.dart 내용 정의
LOGIN_SCREEN_CONTENT = """import 'package:flutter/material.dart';
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
"""

POS_SCREEN_V3_CONTENT = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../providers/cart_provider.dart';
import '../widgets/payment_modal.dart';
import '../widgets/receipt_dialog.dart';
import 'reservation_screen.dart';
class PosScreenV3 extends StatefulWidget { final int storeId; const PosScreenV3({super.key, required this.storeId}); @override State<PosScreenV3> createState() => _S(); }
class _S extends State<PosScreenV3> {
  List _m = []; @override void initState() { super.initState(); _f(); }
  Future<void> _f() async { try { final d = await ApiService().getMenu(widget.storeId); setState(() => _m = d); } catch(e) {} }
  void _pay() {
    final cart = context.read<CartProvider>();
    if(cart.items.isEmpty) return;
    showDialog(context: context, builder: (_) => PaymentModal(total: cart.totalAmount, onDone: (m, r, c) => _order(m, r, c)));
  }
  Future<void> _order(String m, int r, int c) async {
    final cart = context.read<CartProvider>();
    await ApiService().placeOrder({"store_id": widget.storeId, "table_no": "POS", "items": cart.items.map((e) => {"product_id": e.productId, "quantity": e.quantity}).toList()});
    final items = List.from(cart.items); final total = cart.totalAmount; cart.clear();
    if(mounted) showDialog(context: context, builder: (_) => ReceiptDialog(id: "ORD-${DateTime.now().millisecondsSinceEpoch}", total: total, method: m, rec: r, chg: c, items: items));
  }
  @override Widget build(BuildContext context) {
    final cur = NumberFormat("#,###", "ko_KR");
    return Scaffold(appBar: AppBar(title: const Text("TG-POS"), actions: [IconButton(icon: const Icon(Icons.list), onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ReservationScreen(storeId: widget.storeId))))]),
      body: Row(children: [
        Expanded(flex: 2, child: GridView.builder(padding: const EdgeInsets.all(10), gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, childAspectRatio: 1.5), itemCount: _m.fold(0, (s, c) => s + (c['items'] as List).length), itemBuilder: (ctx, i) {
          var all = []; for(var c in _m) all.addAll(c['items']); final p = all[i];
          return Card(child: InkWell(onTap: () => context.read<CartProvider>().addToCart(p['id'], p['name'], p['price']), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Text(p['name']), Text("${cur.format(p['price'])}원")])));
        })),
        Expanded(flex: 1, child: Consumer<CartProvider>(builder: (ctx, cart, _) => Column(children: [
          Expanded(child: ListView.builder(itemCount: cart.items.length, itemBuilder: (ctx, i) => ListTile(title: Text(cart.items[i].name), trailing: IconButton(icon: const Icon(Icons.remove), onPressed: () => cart.removeFromCart(i))))),
          ElevatedButton(onPressed: _pay, child: Text("PAY ${cur.format(cart.totalAmount)}"))
        ])))
      ]));
  }
}
"""

RESERVATION_SCREEN_CONTENT = """import 'package:flutter/material.dart';
import '../services/api_service.dart';
class ReservationScreen extends StatefulWidget { final int storeId; const ReservationScreen({super.key, required this.storeId}); @override State<ReservationScreen> createState() => _S(); }
class _S extends State<ReservationScreen> {
  List _l = []; @override void initState() { super.initState(); _f(); }
  Future<void> _f() async { try { final d = await ApiService().getReservations(widget.storeId); setState(() => _l = d); } catch(e) {} }
  @override Widget build(BuildContext context) { return Scaffold(appBar: AppBar(title: const Text("Reservations")), body: ListView.builder(itemCount: _l.length, itemBuilder: (ctx, i) => ListTile(title: Text(_l[i]['guest_name']), subtitle: Text(_l[i]['reserved_at'])))); }
}
"""

PAYMENT_MODAL_CONTENT = """import 'package:flutter/material.dart';
class PaymentModal extends StatefulWidget { final int total; final Function(String, int, int) onDone; const PaymentModal({super.key, required this.total, required this.onDone}); @override State<PaymentModal> createState() => _S(); }
class _S extends State<PaymentModal> {
  String _m = "CARD"; final _c = TextEditingController();
  @override Widget build(BuildContext context) {
    return AlertDialog(title: const Text("Pay"), content: Column(mainAxisSize: MainAxisSize.min, children: [
      DropdownButton(value: _m, items: const [DropdownMenuItem(value: "CARD", child: Text("Card")), DropdownMenuItem(value: "CASH", child: Text("Cash"))], onChanged: (v) => setState(() => _m = v!)),
      if(_m == "CASH") TextField(controller: _c, decoration: const InputDecoration(labelText: "Received"))
    ]), actions: [ElevatedButton(onPressed: () { int r = _m=="CASH"?int.parse(_c.text):widget.total; widget.onDone(_m, r, r-widget.total); Navigator.pop(context); }, child: const Text("OK"))]);
  }
}
"""

RECEIPT_DIALOG_CONTENT = """import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
class ReceiptDialog extends StatelessWidget {
  final String id, method; final int total, rec, chg; final List items;
  const ReceiptDialog({super.key, required this.id, required this.total, required this.method, required this.rec, required this.chg, required this.items});
  @override Widget build(BuildContext context) {
    final cur = NumberFormat("#,###", "ko_KR");
    return AlertDialog(title: const Text("Receipt"), content: Column(mainAxisSize: MainAxisSize.min, children: [Text("ID: $id"), ...items.map((i) => Text("${i.name} ${cur.format(i.price)}")), Text("Total: ${cur.format(total)}")]), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text("Close"))]);
  }
}
"""

MAIN_DART_CONTENT = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/cart_provider.dart';
import 'screens/login_screen.dart';
void main() { runApp(const App()); }
class App extends StatelessWidget { const App({super.key}); @override Widget build(BuildContext context) { return MultiProvider(providers: [ChangeNotifierProvider(create: (_) => CartProvider())], child: MaterialApp(title: 'TG-POS', theme: ThemeData(primarySwatch: Colors.blue), home: const LoginScreen())); } }
"""

def generate_flutter_project():
    print(f"[*] Generating POS Source Code in: {LIB_DIR}")
    
    # 1. 폴더 구조 생성
    for d in ["screens", "widgets", "services", "providers"]:
        (LIB_DIR / d).mkdir(parents=True, exist_ok=True)
    
    # 2. 생성할 파일 목록 정의
    files = {
        BASE_DIR / "pubspec.yaml": PUBSPEC_CONTENT,
        LIB_DIR / "main.dart": MAIN_DART_CONTENT,
        LIB_DIR / "services/api_service.dart": API_SERVICE_CONTENT,
        LIB_DIR / "providers/cart_provider.dart": CART_PROVIDER_CONTENT,
        
        # [중요] 누락되었던 파일들 추가
        LIB_DIR / "screens/login_screen.dart": LOGIN_SCREEN_CONTENT,
        LIB_DIR / "screens/pos_screen_v3.dart": POS_SCREEN_V3_CONTENT,
        LIB_DIR / "screens/reservation_screen.dart": RESERVATION_SCREEN_CONTENT,
        
        LIB_DIR / "widgets/payment_modal.dart": PAYMENT_MODAL_CONTENT,
        LIB_DIR / "widgets/receipt_dialog.dart": RECEIPT_DIALOG_CONTENT,
    }
    
    # 3. 파일 생성 실행
    for path, content in files.items():
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # 파일이 실제로 생성되었는지 검증
            if path.exists() and path.stat().st_size > 0:
                print(f"    [OK] {path.name} created.")
            else:
                print(f"    [FAIL] {path.name} failed to write!")
                
        except Exception as e:
            print(f"    [ERROR] {path.name}: {e}")

if __name__ == "__main__":
    generate_flutter_project()