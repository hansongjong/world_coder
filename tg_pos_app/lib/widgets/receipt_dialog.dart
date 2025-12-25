import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
class ReceiptDialog extends StatelessWidget {
  final String id, method; final int total, rec, chg; final List items;
  const ReceiptDialog({super.key, required this.id, required this.total, required this.method, required this.rec, required this.chg, required this.items});
  @override Widget build(BuildContext context) {
    final cur = NumberFormat("#,###", "ko_KR");
    return AlertDialog(title: const Text("Receipt"), content: Column(mainAxisSize: MainAxisSize.min, children: [Text("ID: $id"), ...items.map((i) => Text("${i.name} ${cur.format(i.price)}")), Text("Total: ${cur.format(total)}")]), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text("Close"))]);
  }
}
