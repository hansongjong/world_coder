import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../l10n/app_localizations.dart';

class ReceiptDialog extends StatelessWidget {
  final String id;
  final String method;
  final int total;
  final int rec;
  final int chg;
  final List items;

  const ReceiptDialog({
    super.key,
    required this.id,
    required this.total,
    required this.method,
    required this.rec,
    required this.chg,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final cur = NumberFormat("#,###", "ko_KR");

    return AlertDialog(
      title: Row(
        children: [
          const Icon(Icons.receipt_long, color: Color(0xFF3B82F6)),
          const SizedBox(width: 10),
          Text(l10n.get('order_complete')),
        ],
      ),
      content: SizedBox(
        width: 320,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Success Icon
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.green[50],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  Icon(
                    Icons.check_circle,
                    color: Colors.green[600],
                    size: 48,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    l10n.get('payment_complete'),
                    style: TextStyle(
                      color: Colors.green[700],
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Order Number
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    l10n.get('order_number'),
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  Text(
                    id.substring(id.length - 8),
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Items List
            Container(
              constraints: const BoxConstraints(maxHeight: 150),
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: items.length,
                itemBuilder: (context, index) {
                  final item = items[index];
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            '${item.name} x${item.quantity}',
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        Text(
                          '${cur.format(item.price * item.quantity)}${l10n.get('won')}',
                          style: const TextStyle(fontWeight: FontWeight.w500),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
            const Divider(),

            // Total
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.get('total'),
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Text(
                  '${cur.format(total)}${l10n.get('won')}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                    color: Color(0xFF3B82F6),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),

            // Payment Method
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  l10n.get('payment_method'),
                  style: TextStyle(color: Colors.grey[600]),
                ),
                Text(
                  method == 'CARD' ? l10n.get('card') : l10n.get('cash'),
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
              ],
            ),

            // Cash details
            if (method == 'CASH') ...[
              const SizedBox(height: 4),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    l10n.get('received'),
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  Text('${cur.format(rec)}${l10n.get('won')}'),
                ],
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    l10n.get('change'),
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  Text(
                    '${cur.format(chg)}${l10n.get('won')}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.green[700],
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
      actions: [
        ElevatedButton(
          onPressed: () => Navigator.pop(context),
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF3B82F6),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
          ),
          child: Text(l10n.get('confirm')),
        ),
      ],
    );
  }
}
