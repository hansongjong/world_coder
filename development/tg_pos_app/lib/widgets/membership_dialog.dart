import 'package:flutter/material.dart';
import '../services/api_service_v2.dart';

class MembershipDialog extends StatefulWidget {
  final int storeId;
  final int paymentAmount;
  final Function onCompleted;

  const MembershipDialog({
    super.key, 
    required this.storeId, 
    required this.paymentAmount,
    required this.onCompleted
  });

  @override
  State<MembershipDialog> createState() => _MembershipDialogState();
}

class _MembershipDialogState extends State<MembershipDialog> {
  final TextEditingController _phoneController = TextEditingController();
  final ApiServiceV2 _api = ApiServiceV2();
  String _statusMessage = "";

  Future<void> _earn() async {
    if (_phoneController.text.length < 10) {
      setState(() => _statusMessage = "올바른 전화번호를 입력하세요.");
      return;
    }

    try {
      await _api.earnPoints(widget.storeId, _phoneController.text, widget.paymentAmount);
      if (!mounted) return;
      Navigator.pop(context); // 닫기
      widget.onCompleted(); // 결제 완료 콜백 실행
    } catch (e) {
      setState(() => _statusMessage = "적립 실패: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text("포인트 적립"),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: _phoneController,
            keyboardType: TextInputType.phone,
            decoration: const InputDecoration(
              labelText: "전화번호 입력 (010...)",
              border: OutlineInputBorder()
            ),
          ),
          const SizedBox(height: 10),
          Text(_statusMessage, style: const TextStyle(color: Colors.red)),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.pop(context);
            widget.onCompleted(); // 적립 안 하고 결제 완료
          },
          child: const Text("건너뛰기"),
        ),
        ElevatedButton(
          onPressed: _earn,
          child: const Text("적립하기"),
        ),
      ],
    );
  }
}