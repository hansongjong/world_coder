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
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadMenu();
  }

  Future<void> _loadMenu() async {
    try {
      final menu = await _api.getMenu(widget.storeId);
      setState(() {
        _menu = menu;
        _isLoading = false;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  Future<void> _processOrder() async {
    final cart = context.read<CartProvider>();
    if (cart.items.isEmpty) return;

    final orderData = {
      "store_id": widget.storeId,
      "table_no": "POS-01", // 고정값 or 입력값
      "items": cart.items.map((e) => {
        "product_id": e.productId,
        "quantity": e.quantity,
        "options": "{}"
      }).toList()
    };

    try {
      await _api.placeOrder(orderData);
      cart.clearCart();
      if (!mounted) return;
      showDialog(
        context: context, 
        builder: (_) => const AlertDialog(
          title: Text("Order Success"),
          content: Text("주문이 주방으로 전송되었습니다."),
        )
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Fail: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    final currency = NumberFormat("#,###", "ko_KR");
    
    return Scaffold(
      appBar: AppBar(title: const Text("TG-POS System"), backgroundColor: Colors.black87),
      body: Row(
        children: [
          // Left: Menu Grid
          Expanded(
            flex: 2,
            child: _isLoading 
              ? const Center(child: CircularProgressIndicator())
              : ListView.builder(
                  itemCount: _menu.length,
                  itemBuilder: (ctx, i) {
                    final cat = _menu[i];
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: Text(cat['category_name'], style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                        ),
                        GridView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 3, childAspectRatio: 1.2
                          ),
                          itemCount: cat['items'].length,
                          itemBuilder: (ctx, j) {
                            final prod = cat['items'][j];
                            return Card(
                              elevation: 2,
                              child: InkWell(
                                onTap: () => context.read<CartProvider>().addToCart(prod['id'], prod['name'], prod['price']),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(prod['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
                                    const SizedBox(height: 5),
                                    Text("${currency.format(prod['price'])}원"),
                                  ],
                                ),
                              ),
                            );
                          },
                        )
                      ],
                    );
                  },
                ),
          ),
          
          // Right: Cart & Payment
          Expanded(
            flex: 1,
            child: Container(
              color: Colors.grey[200],
              child: Column(
                children: [
                  const Padding(
                    padding: EdgeInsets.all(15.0),
                    child: Text("ORDER LIST", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  ),
                  Expanded(
                    child: Consumer<CartProvider>(
                      builder: (ctx, cart, child) => ListView.builder(
                        itemCount: cart.items.length,
                        itemBuilder: (ctx, i) {
                          final item = cart.items[i];
                          return ListTile(
                            title: Text(item.name),
                            subtitle: Text("${currency.format(item.price)} x ${item.quantity}"),
                            trailing: IconButton(
                              icon: const Icon(Icons.remove_circle, color: Colors.red),
                              onPressed: () => cart.removeFromCart(i),
                            ),
                          );
                        },
                      ),
                    ),
                  ),
                  Consumer<CartProvider>(
                    builder: (ctx, cart, child) => Container(
                      padding: const EdgeInsets.all(20),
                      color: Colors.white,
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text("Total:", style: TextStyle(fontSize: 20)),
                              Text("${currency.format(cart.totalAmount)}원", style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.blue)),
                            ],
                          ),
                          const SizedBox(height: 10),
                          SizedBox(
                            width: double.infinity,
                            height: 50,
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(backgroundColor: Colors.blue),
                              onPressed: cart.items.isEmpty ? null : _processOrder,
                              child: const Text("결제하기 (PAY)", style: TextStyle(fontSize: 18, color: Colors.white)),
                            ),
                          )
                        ],
                      ),
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