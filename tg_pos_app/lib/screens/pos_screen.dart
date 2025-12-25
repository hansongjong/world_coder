import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../providers/cart_provider.dart';
import 'reservation_screen.dart';
import '../widgets/membership_dialog.dart';

class PosScreen extends StatefulWidget {
  final int storeId;
  const PosScreen({super.key, required this.storeId});
  @override
  State<PosScreen> createState() => _PosScreenState();
}

class _PosScreenState extends State<PosScreen> {
  final _api = ApiService();
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

  void _processPayment() {
    final cart = context.read<CartProvider>();
    showDialog(
      context: context,
      builder: (_) => MembershipDialog(
        storeId: widget.storeId,
        amount: cart.totalAmount,
        onDone: () async {
          // 주문 전송
          final orderData = {
            "store_id": widget.storeId,
            "table_no": "WIN-POS",
            "items": cart.items.map((e) => {"product_id": e.productId, "quantity": e.quantity}).toList()
          };
          await _api.placeOrder(orderData);
          cart.clear();
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("주문 완료!")));
        },
      )
    );
  }

  @override
  Widget build(BuildContext context) {
    final currency = NumberFormat("#,###", "ko_KR");
    
    return Scaffold(
      appBar: AppBar(
        title: const Text("TG-POS Windows"), 
        actions: [
          IconButton(
            icon: const Icon(Icons.calendar_today), 
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ReservationScreen(storeId: widget.storeId)))
          )
        ]
      ),
      body: Row(
        children: [
          Expanded(
            flex: 2,
            child: ListView.builder(
              itemCount: _menu.length,
              itemBuilder: (ctx, i) {
                final cat = _menu[i];
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(padding: const EdgeInsets.all(8), child: Text(cat['category_name'], style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold))),
                    GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 4, childAspectRatio: 1.2),
                      itemCount: cat['items'].length,
                      itemBuilder: (ctx, j) {
                        final p = cat['items'][j];
                        return Card(
                          child: InkWell(
                            onTap: () => context.read<CartProvider>().addToCart(p['id'], p['name'], p['price']),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [Text(p['name'], style: const TextStyle(fontWeight: FontWeight.bold)), Text("${currency.format(p['price'])}원")],
                            ),
                          ),
                        );
                      }
                    )
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
                      itemBuilder: (ctx, i) {
                        final item = cart.items[i];
                        return ListTile(
                          title: Text(item.name),
                          subtitle: Text("${currency.format(item.price)} x ${item.quantity}"),
                          trailing: IconButton(icon: const Icon(Icons.remove_circle), onPressed: () => cart.removeFromCart(i)),
                        );
                      }
                    )
                  ),
                  Container(
                    padding: const EdgeInsets.all(20),
                    color: Colors.blueGrey[100],
                    child: Column(
                      children: [
                        Text("Total: ${currency.format(cart.totalAmount)}원", style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 10),
                        SizedBox(width: double.infinity, height: 50, child: ElevatedButton(onPressed: cart.items.isEmpty ? null : _processPayment, child: const Text("PAY")))
                      ],
                    ),
                  )
                ],
              )
            )
          )
        ],
      ),
    );
  }
}
