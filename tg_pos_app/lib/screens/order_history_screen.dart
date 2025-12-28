import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../l10n/app_localizations.dart';

class OrderHistoryScreen extends StatefulWidget {
  final int storeId;
  const OrderHistoryScreen({super.key, required this.storeId});

  @override
  State<OrderHistoryScreen> createState() => _OrderHistoryScreenState();
}

class _OrderHistoryScreenState extends State<OrderHistoryScreen> {
  final _currencyFormat = NumberFormat("#,###", "ko_KR");
  final _dateFormat = DateFormat("yyyy-MM-dd");

  List<dynamic> _orders = [];
  bool _isLoading = true;
  int _totalCount = 0;

  DateTime _selectedDate = DateTime.now();
  String? _selectedStatus;

  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  List<Map<String, String>> _getStatusOptions(AppLocalizations l10n) => [
        {'value': '', 'label': l10n.get('order_status')},
        {'value': 'pending', 'label': l10n.get('pending')},
        {'value': 'paid', 'label': l10n.get('paid')},
        {'value': 'preparing', 'label': l10n.get('preparing')},
        {'value': 'ready', 'label': l10n.get('ready')},
        {'value': 'completed', 'label': l10n.get('completed')},
        {'value': 'canceled', 'label': l10n.get('canceled')},
      ];

  Future<void> _loadOrders() async {
    setState(() => _isLoading = true);
    try {
      final result = await ApiService().getOrderHistory(
        widget.storeId,
        date: _dateFormat.format(_selectedDate),
        status: _selectedStatus,
      );
      setState(() {
        _orders = result['orders'] ?? [];
        _totalCount = result['total'] ?? 0;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('로드 오류: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
      locale: const Locale('ko'),
    );
    if (picked != null && picked != _selectedDate) {
      setState(() => _selectedDate = picked);
      _loadOrders();
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return Colors.orange;
      case 'paid':
        return Colors.blue;
      case 'preparing':
        return Colors.purple;
      case 'ready':
        return Colors.teal;
      case 'completed':
        return Colors.green;
      case 'canceled':
      case 'refunded':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String _getStatusLabel(String status, AppLocalizations l10n) {
    switch (status.toLowerCase()) {
      case 'pending':
        return l10n.get('pending');
      case 'paid':
        return l10n.get('paid');
      case 'preparing':
        return l10n.get('preparing');
      case 'ready':
        return l10n.get('ready');
      case 'completed':
        return l10n.get('completed');
      case 'canceled':
        return l10n.get('canceled');
      case 'refunded':
        return l10n.get('refund_complete');
      default:
        return status;
    }
  }

  void _showRefundDialog(dynamic order) {
    final l10n = AppLocalizations.of(context);
    String? selectedReason;
    final reasons = [
      l10n.get('customer_request'),
      l10n.get('wrong_order'),
      l10n.get('product_issue'),
    ];

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: Row(
            children: [
              const Icon(Icons.replay, color: Colors.red),
              const SizedBox(width: 8),
              Text(l10n.get('refund')),
            ],
          ),
          content: SizedBox(
            width: 300,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Order Info
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(l10n.get('order_number')),
                          Text(
                            (order['id'] as String?)?.substring(0, 8) ?? '',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(l10n.get('refund_amount')),
                          Text(
                            '${_currencyFormat.format(order['total'])}${l10n.get('won')}',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 18,
                              color: Colors.red,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Refund Reason
                Text(
                  l10n.get('refund_reason'),
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                ...reasons.map((reason) => RadioListTile<String>(
                      title: Text(reason),
                      value: reason,
                      groupValue: selectedReason,
                      onChanged: (value) {
                        setDialogState(() => selectedReason = value);
                      },
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                    )),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(l10n.get('cancel')),
            ),
            ElevatedButton(
              onPressed: selectedReason == null
                  ? null
                  : () => _processRefund(order, selectedReason!),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
              ),
              child: Text(l10n.get('process_refund')),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _processRefund(dynamic order, String reason) async {
    Navigator.pop(context); // Close dialog

    try {
      // Call refund API
      await ApiService().refundOrder(order['id'], reason);

      if (mounted) {
        final l10n = AppLocalizations.of(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(l10n.get('refund_complete')),
            backgroundColor: Colors.green,
          ),
        );
        _loadOrders(); // Refresh list
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('환불 처리 실패: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.get('order_history')),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadOrders,
            tooltip: l10n.get('refresh'),
          ),
        ],
      ),
      body: Column(
        children: [
          _buildFilterBar(l10n),
          _buildSummaryBar(l10n),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _orders.isEmpty
                    ? Center(child: Text(l10n.get('no_waiting')))
                    : _buildOrderList(l10n),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterBar(AppLocalizations l10n) {
    return Container(
      padding: const EdgeInsets.all(12),
      color: Colors.grey[100],
      child: Row(
        children: [
          // Date Picker
          Expanded(
            child: InkWell(
              onTap: _selectDate,
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[300]!),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      _dateFormat.format(_selectedDate),
                      style: const TextStyle(fontSize: 14),
                    ),
                    const Icon(Icons.calendar_today, size: 18),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(width: 10),
          // Status Filter
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.grey[300]!),
              ),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  value: _selectedStatus ?? '',
                  isExpanded: true,
                  items: _getStatusOptions(l10n).map((option) {
                    return DropdownMenuItem(
                      value: option['value'],
                      child: Text(option['label']!,
                          style: const TextStyle(fontSize: 14)),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setState(() =>
                        _selectedStatus = value?.isEmpty == true ? null : value);
                    _loadOrders();
                  },
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryBar(AppLocalizations l10n) {
    final totalSales = _orders.fold<int>(
      0,
      (sum, order) => sum + ((order['total'] as num?)?.toInt() ?? 0),
    );

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: const Color(0xFF1E293B),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            '${l10n.get('total')}: $_totalCount ${l10n.get('order')}',
            style:
                const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
          Text(
            '${_currencyFormat.format(totalSales)}${l10n.get('won')}',
            style: const TextStyle(
              color: Color(0xFF3B82F6),
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOrderList(AppLocalizations l10n) {
    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: _orders.length,
      itemBuilder: (context, index) {
        final order = _orders[index];
        final status = (order['status'] as String?) ?? 'unknown';
        final items = order['items'] as List<dynamic>? ?? [];
        final createdAt = DateTime.tryParse(order['created_at'] ?? '');
        final canRefund = status == 'paid' || status == 'completed';

        return Card(
          margin: const EdgeInsets.only(bottom: 10),
          child: ExpansionTile(
            leading: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: _getStatusColor(status),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                _getStatusLabel(status, l10n),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            title: Row(
              children: [
                Expanded(
                  child: Text(
                    '${l10n.get('tables')}: ${order['table'] ?? '-'}',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
                Text(
                  '${_currencyFormat.format(order['total'])}${l10n.get('won')}',
                  style: const TextStyle(
                    color: Color(0xFF3B82F6),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            subtitle: Text(
              createdAt != null
                  ? DateFormat('HH:mm:ss').format(createdAt)
                  : order['created_at'] ?? '',
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.get('order_list'),
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    ...items.map((item) => Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('${item['name']} x ${item['qty']}'),
                              Text(
                                '${_currencyFormat.format((item['price'] ?? 0) * (item['qty'] ?? 1))}${l10n.get('won')}',
                              ),
                            ],
                          ),
                        )),
                    const Divider(),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '${l10n.get('payment_method')}: ${order['payment_method'] ?? 'N/A'}',
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                        Text(
                          'ID: ${(order['id'] as String?)?.substring(0, 8) ?? ''}...',
                          style:
                              TextStyle(color: Colors.grey[600], fontSize: 12),
                        ),
                      ],
                    ),
                    // Refund Button
                    if (canRefund) ...[
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton.icon(
                          onPressed: () => _showRefundDialog(order),
                          icon: const Icon(Icons.replay, color: Colors.red),
                          label: Text(
                            l10n.get('refund'),
                            style: const TextStyle(color: Colors.red),
                          ),
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: Colors.red),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
