import 'package:flutter/material.dart';
import '../services/api_service.dart';

class MembershipDialog extends StatefulWidget {
  final int storeId;
  final int amount;
  final VoidCallback onDone;
  const MembershipDialog({super.key, required this.storeId, required this.amount, required this.onDone});
  @override
  State<MembershipDialog> createState() => _MembershipDialogState();
}

class _MembershipDialogState extends State<MembershipDialog> {
  final _ctrl = TextEditingController();
  final _api = ApiService();

  Future<void> _earn() async {
    await _api.earnPoints(widget.storeId, _ctrl.text, widget.amount);
    if (!mounted) return;
    Navigator.pop(context);
    widget.onDone();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text("Earn Points?"),
      content: TextField(controller: _ctrl, decoration: const InputDecoration(labelText: "Phone Number")),
      actions: [
        TextButton(onPressed: () { Navigator.pop(context); widget.onDone(); }, child: const Text("Skip")),
        ElevatedButton(onPressed: _earn, child: const Text("Earn")),
      ],
    );
  }
}
