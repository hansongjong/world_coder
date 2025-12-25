import 'package:flutter/material.dart';
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
