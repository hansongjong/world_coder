// V3: 결제 수단 선택 및 영수증 기능 추가 버전
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
      // Error handling
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
    
    // 주문 데이터 생성
    final orderData = {
      "store_id": widget.storeId,
      "table_no": "POS-01",
      "payment_method": method, // 백엔드에 결제 수단 전송 추가 필요 (API 수정 권장)
      "items": cart.items.map((e) => {"product_id": e.productId, "quantity": e.quantity}).toList()
    };

    try {
      // 실제 API 호출 (백엔드 models.py의 Payment 테이블에 method 저장 로직이 필요하지만 현재는 생략)
      await _api.placeOrder(orderData);
      
      // 장바구니 백업 (영수증용)
      final itemsBackup = List.from(cart.items);
      final totalBackup = cart.totalAmount;
      
      cart.clear(); // 장바구니 비우기

      if (!mounted) return;
      
      // 영수증 출력
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (_) => ReceiptDialog(
          orderId: "ORDER-${DateTime.now().millisecondsSinceEpoch}", // 임시 ID
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
    // (기존 UI 코드와 동일, 버튼 이벤트만 변경)
    return Scaffold(
      appBar: AppBar(title: const Text("TG-POS Expert"), backgroundColor: Colors.black87),
      body: Row(
        children: [
          // Left: Menu
          Expanded(
            flex: 2,
            child: GridView.builder(
              padding: const EdgeInsets.all(10),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 3, childAspectRatio: 1.5, crossAxisSpacing: 10, mainAxisSpacing: 10),
              itemCount: _menu.fold(0, (sum, cat) => sum + (cat['items'] as List).length),
              itemBuilder: (ctx, i) {
                // Flatten Logic (간소화)
                var allItems = [];
                for(var cat in _menu) allItems.addAll(cat['items']);
                final p = allItems[i];
                return Card(
                  color: Colors.white,
                  elevation: 2,
                  child: InkWell(
                    onTap: () => context.read<CartProvider>().addToCart(p['id'], p['name'], p['price']),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(p['name'], style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 5),
                        Text("${currency.format(p['price'])}원", style: const TextStyle(color: Colors.blue)),
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
            child: Container(
              color: Colors.grey[100],
              child: Column(
                children: [
                  Expanded(
                    child: Consumer<CartProvider>(
                      builder: (ctx, cart, _) => ListView.builder(
                        itemCount: cart.items.length,
                        itemBuilder: (ctx, i) {
                          final item = cart.items[i];
                          return ListTile(
                            title: Text(item.name),
                            subtitle: Text("${currency.format(item.price)} x ${item.quantity}"),
                            trailing: Text(currency.format(item.total)),
                          );
                        }
                      )
                    )
                  ),
                  Container(
                    padding: const EdgeInsets.all(20),
                    color: Colors.white,
                    child: Column(
                      children: [
                        Consumer<CartProvider>(builder: (ctx, cart, _) => 
                          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                            const Text("합계 금액", style: TextStyle(fontSize: 20)),
                            Text("${currency.format(cart.totalAmount)}원", style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Colors.red))
                          ])
                        ),
                        const SizedBox(height: 15),
                        SizedBox(
                          width: double.infinity,
                          height: 60,
                          child: ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(backgroundColor: Colors.blue[800]),
                            icon: const Icon(Icons.payment, color: Colors.white),
                            label: const Text("결제하기", style: TextStyle(fontSize: 20, color: Colors.white)),
                            onPressed: _showPaymentModal, // 결제 모달 호출
                          ),
                        )
                      ],
                    ),
                  )
                ],
              ),
            ),
          )
        ]
      )
    );
  }
}