import 'package:flutter/material.dart';
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
  List<dynamic> _menu = [];

  @override
  void initState() {
    super.initState();
    _loadMenu();
  }

  Future<void> _loadMenu() async {
    try {
      final data = await _api.getMenu(widget.storeId);
      setState(() => _menu = data);
    } catch(e) {
      print("Menu Load Error: $e");
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
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    final currency = NumberFormat("#,###", "ko_KR");

    return Scaffold(
      appBar: AppBar(title: const Text("TG-POS V3"), backgroundColor: Colors.indigo),
      drawer: Drawer(
        child: ListView(
          children: [
            const DrawerHeader(child: Text("Menu")),
            ListTile(
              title: const Text("Booking"), 
              onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ReservationScreen(storeId: widget.storeId)))
            )
          ]
        )
      ),
      body: Row(
        children: [
          // Left: Menu Grid
          Expanded(
            flex: 2,
            child: GridView.builder(
              padding: const EdgeInsets.all(10),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3, 
                childAspectRatio: 1.5,
                crossAxisSpacing: 10,
                mainAxisSpacing: 10
              ),
              // [FIX 1] 타입 명시: int sum
              itemCount: _menu.fold<int>(0, (int sum, dynamic cat) => sum + (cat['items'] as List).length),
              itemBuilder: (ctx, i) {
                var allItems = [];
                for(var cat in _menu) allItems.addAll(cat['items']);
                final p = allItems[i];
                return Card(
                  elevation: 2,
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
          // Right: Cart
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
                        // [FIX 2] item.total 대신 직접 계산
                        final itemTotal = item.price * item.quantity;
                        return ListTile(
                          title: Text(item.name),
                          subtitle: Text("${currency.format(item.price)} x ${item.quantity}"),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(currency.format(itemTotal)),
                              IconButton(
                                icon: const Icon(Icons.remove_circle, color: Colors.red),
                                onPressed: () => cart.removeFromCart(i)
                              )
                            ],
                          ),
                        );
                      }
                    )
                  ),
                  Container(
                    padding: const EdgeInsets.all(20),
                    color: Colors.white,
                    child: Column(
                      children: [
                        Text("Total: ${currency.format(cart.totalAmount)}", style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 10),
                        SizedBox(
                          width: double.infinity,
                          height: 50,
                          child: ElevatedButton(
                            onPressed: _showPaymentModal, 
                            child: const Text("PAY")
                          )
                        )
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