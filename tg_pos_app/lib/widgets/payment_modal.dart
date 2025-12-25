import 'package:flutter/material.dart';
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
