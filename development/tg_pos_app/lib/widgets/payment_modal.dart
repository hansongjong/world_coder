import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

enum PaymentMethod { card, cash, easyPay }

class PaymentModal extends StatefulWidget {
  final int totalAmount;
  final Function(String method, int received, int change) onPaymentComplete;

  const PaymentModal({super.key, required this.totalAmount, required this.onPaymentComplete});

  @override
  State<PaymentModal> createState() => _PaymentModalState();
}

class _PaymentModalState extends State<PaymentModal> {
  final currency = NumberFormat("#,###", "ko_KR");
  final TextEditingController _cashCtrl = TextEditingController();
  PaymentMethod _selected = PaymentMethod.card;
  int _change = 0;

  void _calculateChange(String value) {
    int received = int.tryParse(value) ?? 0;
    setState(() {
      _change = received - widget.totalAmount;
    });
  }

  void _submit() {
    if (_selected == PaymentMethod.cash && _change < 0) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("받은 금액이 부족합니다.")));
      return;
    }
    
    int received = _selected == PaymentMethod.cash ? int.tryParse(_cashCtrl.text) ?? 0 : widget.totalAmount;
    String methodStr = _selected == PaymentMethod.card ? "CARD" : (_selected == PaymentMethod.cash ? "CASH" : "EASY_PAY");
    
    widget.onPaymentComplete(methodStr, received, _change);
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text("결제 수단 선택", style: TextStyle(fontWeight: FontWeight.bold)),
      content: SizedBox(
        width: 400,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text("결제 금액: ${currency.format(widget.totalAmount)}원", 
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.blue), textAlign: TextAlign.center),
            const SizedBox(height: 20),
            
            // Payment Methods
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildMethodBtn(PaymentMethod.card, Icons.credit_card, "신용카드"),
                _buildMethodBtn(PaymentMethod.cash, Icons.money, "현금"),
                _buildMethodBtn(PaymentMethod.easyPay, Icons.qr_code, "간편결제"),
              ],
            ),
            const SizedBox(height: 20),

            // Cash Input Area
            if (_selected == PaymentMethod.cash) ...[
              TextField(
                controller: _cashCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: "받은 금액", border: OutlineInputBorder()),
                onChanged: _calculateChange,
              ),
              const SizedBox(height: 10),
              Text("거스름돈: ${currency.format(_change)}원", 
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: _change < 0 ? Colors.red : Colors.green)),
            ] else if (_selected == PaymentMethod.card) ...[
              const Center(child: Text("IC카드를 리더기에 꽂아주세요...", style: TextStyle(color: Colors.grey)))
            ]
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text("취소")),
        ElevatedButton(
          style: ElevatedButton.styleFrom(backgroundColor: Colors.blue, padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15)),
          onPressed: _submit,
          child: const Text("결제 완료", style: TextStyle(fontSize: 16, color: Colors.white)),
        ),
      ],
    );
  }

  Widget _buildMethodBtn(PaymentMethod method, IconData icon, String label) {
    bool isSelected = _selected == method;
    return GestureDetector(
      onTap: () => setState(() => _selected = method),
      child: Container(
        width: 100,
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: isSelected ? Colors.blue[50] : Colors.white,
          border: Border.all(color: isSelected ? Colors.blue : Colors.grey[300]!, width: 2),
          borderRadius: BorderRadius.circular(10)
        ),
        child: Column(
          children: [
            Icon(icon, color: isSelected ? Colors.blue : Colors.grey, size: 30),
            const SizedBox(height: 5),
            Text(label, style: TextStyle(color: isSelected ? Colors.blue : Colors.grey, fontWeight: FontWeight.bold))
          ],
        ),
      ),
    );
  }
}