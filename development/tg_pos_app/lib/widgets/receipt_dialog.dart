import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class ReceiptDialog extends StatelessWidget {
  final String orderId;
  final int totalAmount;
  final String method;
  final int received;
  final int change;
  final List<dynamic> items; // CartItems

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
    final now = DateFormat("yyyy-MM-dd HH:mm:ss").format(DateTime.now());

    return AlertDialog(
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero), // 영수증처럼 각지게
      content: SizedBox(
        width: 300,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Center(child: Text("TG-BURGER GANGNAM", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18))),
            const Center(child: Text("Tel: 02-1234-5678", style: TextStyle(fontSize: 12))),
            const Divider(thickness: 2, height: 30),
            Text("주문번호: ${orderId.substring(0, 8)}"),
            Text("일시: $now"),
            const Divider(),
            ...items.map((item) => Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text("${item.name} x${item.quantity}"),
                Text("${currency.format(item.price * item.quantity)}")
              ],
            )),
            const Divider(thickness: 2),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("합계 금액", style: TextStyle(fontWeight: FontWeight.bold)),
                Text(currency.format(totalAmount), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))
              ],
            ),
            const SizedBox(height: 10),
            if (method == "CASH") ...[
              Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const Text("받은 금액"), Text(currency.format(received))]),
              Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const Text("거스름돈"), Text(currency.format(change))]),
            ],
            Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const Text("결제 수단"), Text(method, style: const TextStyle(fontWeight: FontWeight.bold))]),
            const SizedBox(height: 20),
            const Center(child: Text("Thank you!", style: TextStyle(fontStyle: FontStyle.italic))),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text("닫기")),
        ElevatedButton(onPressed: () => Navigator.pop(context), child: const Text("출력 (Print)")),
      ],
    );
  }
}