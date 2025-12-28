import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../l10n/app_localizations.dart';

class PaymentModal extends StatefulWidget {
  final int total;
  final Function(String, int, int, {int? discountAmount, String? discountType}) onDone;

  const PaymentModal({
    super.key,
    required this.total,
    required this.onDone,
  });

  @override
  State<PaymentModal> createState() => _PaymentModalState();
}

class _PaymentModalState extends State<PaymentModal> {
  String _paymentMethod = "CARD";
  final _receivedController = TextEditingController();
  final _discountController = TextEditingController();
  final _currencyFormat = NumberFormat("#,###", "ko_KR");

  // Discount options
  bool _showDiscount = false;
  String _discountType = "percent"; // "percent" or "amount"
  int _discountValue = 0;

  int get _discountAmount {
    if (_discountValue == 0) return 0;
    if (_discountType == "percent") {
      return (widget.total * _discountValue / 100).round();
    }
    return _discountValue;
  }

  int get _finalTotal => widget.total - _discountAmount;

  int get _received {
    if (_paymentMethod == "CASH") {
      return int.tryParse(_receivedController.text) ?? 0;
    }
    return _finalTotal;
  }

  int get _change => _received - _finalTotal;

  void _processPayment() {
    if (_paymentMethod == "CASH" && _received < _finalTotal) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('받은 금액이 부족합니다')),
      );
      return;
    }
    widget.onDone(
      _paymentMethod,
      _received,
      _change,
      discountAmount: _discountAmount > 0 ? _discountAmount : null,
      discountType: _discountAmount > 0 ? _discountType : null,
    );
    Navigator.pop(context);
  }

  void _updateDiscount(String value) {
    setState(() {
      _discountValue = int.tryParse(value) ?? 0;
      if (_discountType == "percent" && _discountValue > 100) {
        _discountValue = 100;
        _discountController.text = "100";
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);

    return AlertDialog(
      title: Text(l10n.get('payment')),
      content: SizedBox(
        width: 350,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Total Amount
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    if (_discountAmount > 0) ...[
                      Text(
                        l10n.get('original_price'),
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                      Text(
                        '${_currencyFormat.format(widget.total)}${l10n.get('won')}',
                        style: TextStyle(
                          fontSize: 16,
                          decoration: TextDecoration.lineThrough,
                          color: Colors.grey[500],
                        ),
                      ),
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.red[100],
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          '-${_currencyFormat.format(_discountAmount)}${l10n.get('won')} ${l10n.get('discount')}',
                          style: TextStyle(
                            color: Colors.red[700],
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                    ],
                    Text(
                      l10n.get('total'),
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${_currencyFormat.format(_finalTotal)}${l10n.get('won')}',
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF3B82F6),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Discount Toggle
              InkWell(
                onTap: () => setState(() => _showDiscount = !_showDiscount),
                borderRadius: BorderRadius.circular(8),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey[300]!),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.discount,
                            color: _showDiscount ? Colors.red : Colors.grey[600],
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            l10n.get('discount'),
                            style: TextStyle(
                              color: _showDiscount ? Colors.red : Colors.grey[700],
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                      Icon(
                        _showDiscount
                            ? Icons.keyboard_arrow_up
                            : Icons.keyboard_arrow_down,
                        color: Colors.grey[600],
                      ),
                    ],
                  ),
                ),
              ),

              // Discount Options
              if (_showDiscount) ...[
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _buildDiscountTypeButton(
                        l10n.get('discount_percent'),
                        "percent",
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _buildDiscountTypeButton(
                        l10n.get('discount_amount'),
                        "amount",
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: _discountController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: _discountType == "percent"
                        ? l10n.get('discount_percent')
                        : l10n.get('discount_amount'),
                    border: const OutlineInputBorder(),
                    suffixText:
                        _discountType == "percent" ? '%' : l10n.get('won'),
                  ),
                  onChanged: _updateDiscount,
                ),
              ],
              const SizedBox(height: 16),

              // Payment Method
              Text(
                l10n.get('payment_method'),
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: _buildMethodButton(
                      l10n.get('card'),
                      Icons.credit_card,
                      "CARD",
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _buildMethodButton(
                      l10n.get('cash'),
                      Icons.money,
                      "CASH",
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Cash input
              if (_paymentMethod == "CASH") ...[
                TextField(
                  controller: _receivedController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: l10n.get('received'),
                    border: const OutlineInputBorder(),
                    suffixText: l10n.get('won'),
                  ),
                  onChanged: (_) => setState(() {}),
                ),
                const SizedBox(height: 12),
                if (_received >= _finalTotal)
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.green[50],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          l10n.get('change'),
                          style: TextStyle(color: Colors.green[700]),
                        ),
                        Text(
                          '${_currencyFormat.format(_change)}${l10n.get('won')}',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                            color: Colors.green[700],
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text(l10n.get('cancel')),
        ),
        ElevatedButton(
          onPressed: _processPayment,
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF3B82F6),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          ),
          child: Text(l10n.get('payment_complete')),
        ),
      ],
    );
  }

  Widget _buildMethodButton(String label, IconData icon, String value) {
    final isSelected = _paymentMethod == value;
    return InkWell(
      onTap: () => setState(() => _paymentMethod = value),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF3B82F6) : Colors.grey[100],
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? const Color(0xFF3B82F6) : Colors.grey[300]!,
            width: 2,
          ),
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color: isSelected ? Colors.white : Colors.grey[600],
              size: 28,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.grey[600],
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDiscountTypeButton(String label, String value) {
    final isSelected = _discountType == value;
    return InkWell(
      onTap: () {
        setState(() {
          _discountType = value;
          _discountController.clear();
          _discountValue = 0;
        });
      },
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? Colors.red[50] : Colors.grey[100],
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? Colors.red : Colors.grey[300]!,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              color: isSelected ? Colors.red : Colors.grey[600],
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              fontSize: 13,
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _receivedController.dispose();
    _discountController.dispose();
    super.dispose();
  }
}
