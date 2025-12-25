import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../providers/cart_provider.dart';

class PosScreen extends StatefulWidget {
  final int storeId;
  const PosScreen({super.key, required this.storeId});

  @override
  State<PosScreen> createState() => _PosScreenState();
}

class _PosScreenState extends State<PosScreen> {
  final ApiService _api = ApiService();
  List<dynamic> _menu = [];
  final currency = NumberFormat("#,###", "ko_KR");

  @override
  void initState() {
    super.initState();
    _loadMenu();
  }

  Future<void> _loadMenu() async {
    final data = await _api.getMenu(widget.storeId);
    // Flatten menu for simple grid
    List<dynamic> flat = [];
    for(var cat in data) {
      for(var item in cat['items']) {
        flat.add(item);
      }
    }
    setState(() => _menu = flat);
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
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Payment Success!")));
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("TG-POS"), backgroundColor: Colors.indigo, foregroundColor: Colors.white),
      body: Row(
        children: [
          // Menu Area
          Expanded(
            flex: 2,
            child: GridView.builder(
              padding: const EdgeInsets.all(10),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, childAspectRatio: 1.2),
              itemCount: _menu.length,
              itemBuilder: (ctx, i) {
                final p = _menu[i];
                return Card(
                  child: InkWell(
                    onTap: () => context.read<CartProvider>().addToCart(p['id'], p['name'], p['price']),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(p['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
                        Text("${currency.format(p['price'])}원")
                      ],
                    ),
                  ),
                );
              }
            )
          ),
          // Cart Area
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
                        subtitle: Text("x${cart.items[i].quantity}"),
                        trailing: IconButton(icon: const Icon(Icons.remove_circle, color: Colors.red), onPressed: () => cart.removeFromCart(i))
                      )
                    )
                  ),
                  Container(
                    padding: const EdgeInsets.all(20),
                    color: Colors.white,
                    child: Column(
                      children: [
                        Text("Total: ${currency.format(cart.totalAmount)}", style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 10),
                        SizedBox(width: double.infinity, height: 50, child: ElevatedButton(onPressed: _pay, child: const Text("PAY")))
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