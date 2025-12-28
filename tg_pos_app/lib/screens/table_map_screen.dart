import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../widgets/payment_modal.dart';
import '../services/api_service.dart';
import 'table_layout_editor.dart';

class TableMapScreen extends StatefulWidget {
  final int storeId;
  const TableMapScreen({super.key, required this.storeId});

  @override
  State<TableMapScreen> createState() => _TableMapScreenState();
}

class _TableMapScreenState extends State<TableMapScreen> {
  List<Map<String, dynamic>> _tables = [];
  bool _isLoading = true;
  String? _selectedTable;
  final _currencyFormat = NumberFormat("#,###", "ko_KR");

  @override
  void initState() {
    super.initState();
    _loadTables();
  }

  Future<void> _loadTables() async {
    setState(() => _isLoading = true);
    try {
      // Load table layout from store config
      final config = await ApiService().getStoreConfig(widget.storeId);

      if (config != null && config['extra_settings'] != null) {
        final extraSettings = config['extra_settings'];
        if (extraSettings is Map && extraSettings['table_layout'] != null) {
          final layout = extraSettings['table_layout'] as List;
          setState(() {
            _tables = layout.map((t) {
              final tableNo = t['name'] ?? 'T01';
              // For demo: alternate between occupied/available
              final hasOrder = _tables.any((existing) =>
                existing['table_no'] == tableNo && existing['status'] == 'occupied');
              return <String, dynamic>{
                'table_no': tableNo,
                'status': hasOrder ? 'occupied' : 'available',
                'guests': hasOrder ? 2 : 0,
                'order_amount': hasOrder ? 25000 : 0,
                'order_time': hasOrder ? DateTime.now().subtract(const Duration(minutes: 30)) : null,
                'x': t['x'] ?? 0.0,
                'y': t['y'] ?? 0.0,
                'shape': t['shape'] ?? 'rect4',
                'capacity': t['capacity'] ?? 4,
              };
            }).toList();
          });
          return;
        }
      }

      // Fallback: generate default tables if no layout saved
      setState(() {
        _tables = List.generate(12, (i) {
          final tableNo = 'T${(i + 1).toString().padLeft(2, '0')}';
          final hasOrder = i % 3 == 0;
          return <String, dynamic>{
            'table_no': tableNo,
            'status': hasOrder ? 'occupied' : 'available',
            'guests': hasOrder ? (i % 4) + 1 : 0,
            'order_amount': hasOrder ? (i + 1) * 15000 : 0,
            'order_time': hasOrder ? DateTime.now().subtract(Duration(minutes: i * 10)) : null,
          };
        });
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load tables: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Color _getTableColor(String status) {
    switch (status) {
      case 'occupied':
        return Colors.orange.shade100;
      case 'reserved':
        return Colors.blue.shade100;
      default:
        return Colors.green.shade100;
    }
  }

  Color _getTableBorderColor(String status) {
    switch (status) {
      case 'occupied':
        return Colors.orange;
      case 'reserved':
        return Colors.blue;
      default:
        return Colors.green;
    }
  }

  IconData _getTableIcon(String status) {
    switch (status) {
      case 'occupied':
        return Icons.restaurant;
      case 'reserved':
        return Icons.event_seat;
      default:
        return Icons.table_restaurant;
    }
  }

  void _onTableTap(Map<String, dynamic> table) {
    setState(() => _selectedTable = table['table_no']);

    if (table['status'] == 'occupied') {
      _showTableOrderDialog(table);
    } else {
      _showNewOrderDialog(table);
    }
  }

  void _showTableOrderDialog(Map<String, dynamic> table) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Table ${table['table_no']}'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Guests: ${table['guests']}'),
            const SizedBox(height: 8),
            Text('Order Amount: ${_currencyFormat.format(table['order_amount'])}원'),
            const SizedBox(height: 8),
            if (table['order_time'] != null)
              Text('Time: ${DateFormat('HH:mm').format(table['order_time'])}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _addItemsToTable(table);
            },
            child: const Text('Add Items'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _showPaymentForTable(table);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF3B82F6),
              foregroundColor: Colors.white,
            ),
            child: const Text('Pay'),
          ),
        ],
      ),
    );
  }

  void _showNewOrderDialog(Map<String, dynamic> table) {
    int guests = 1;
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: Text('Open Table ${table['table_no']}'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Number of Guests'),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  IconButton(
                    onPressed: guests > 1
                        ? () => setDialogState(() => guests--)
                        : null,
                    icon: const Icon(Icons.remove_circle_outline),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Text(
                      '$guests',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () => setDialogState(() => guests++),
                    icon: const Icon(Icons.add_circle_outline),
                  ),
                ],
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                _openTable(table, guests);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF3B82F6),
                foregroundColor: Colors.white,
              ),
              child: const Text('Open Table'),
            ),
          ],
        ),
      ),
    );
  }

  void _openTable(Map<String, dynamic> table, int guests) {
    setState(() {
      final idx = _tables.indexWhere((t) => t['table_no'] == table['table_no']);
      if (idx != -1) {
        _tables[idx] = {
          ..._tables[idx],
          'status': 'occupied',
          'guests': guests,
          'order_amount': 0,
          'order_time': DateTime.now(),
        };
      }
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Table ${table['table_no']} opened with $guests guests')),
    );
  }

  void _addItemsToTable(Map<String, dynamic> table) {
    // Navigate back to POS with table context
    Navigator.pop(context, {'action': 'add_items', 'table': table['table_no']});
  }

  void _showPaymentForTable(Map<String, dynamic> table) {
    showDialog(
      context: context,
      builder: (_) => PaymentModal(
        total: table['order_amount'],
        onDone: (method, received, change, {discountAmount, discountType}) {
          _completeTablePayment(table, method);
        },
      ),
    );
  }

  void _completeTablePayment(Map<String, dynamic> table, String method) {
    setState(() {
      final idx = _tables.indexWhere((t) => t['table_no'] == table['table_no']);
      if (idx != -1) {
        _tables[idx] = {
          ..._tables[idx],
          'status': 'available',
          'guests': 0,
          'order_amount': 0,
          'order_time': null,
        };
      }
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Table ${table['table_no']} payment completed via $method')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Table Map'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => TableLayoutEditor(storeId: widget.storeId),
              ),
            ).then((_) => _loadTables()),
            tooltip: 'Edit Layout',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadTables,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Legend
                Container(
                  padding: const EdgeInsets.all(12),
                  color: Colors.grey[100],
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      _buildLegendItem('Available', Colors.green),
                      const SizedBox(width: 20),
                      _buildLegendItem('Occupied', Colors.orange),
                      const SizedBox(width: 20),
                      _buildLegendItem('Reserved', Colors.blue),
                    ],
                  ),
                ),
                // Table Grid
                Expanded(
                  child: GridView.builder(
                    padding: const EdgeInsets.all(16),
                    gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                      maxCrossAxisExtent: 200,
                      childAspectRatio: 1,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                    ),
                    itemCount: _tables.length,
                    itemBuilder: (context, index) {
                      final table = _tables[index];
                      return _buildTableCard(table);
                    },
                  ),
                ),
                // Summary
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.1),
                        blurRadius: 10,
                        offset: const Offset(0, -2),
                      ),
                    ],
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildSummaryItem(
                        'Available',
                        _tables.where((t) => t['status'] == 'available').length,
                        Colors.green,
                      ),
                      _buildSummaryItem(
                        'Occupied',
                        _tables.where((t) => t['status'] == 'occupied').length,
                        Colors.orange,
                      ),
                      _buildSummaryItem(
                        'Total Sales',
                        _tables.fold<int>(0, (sum, t) => sum + (t['order_amount'] as int)),
                        Colors.blue,
                        isCurrency: true,
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.3),
            border: Border.all(color: color, width: 2),
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(fontSize: 13)),
      ],
    );
  }

  Widget _buildTableCard(Map<String, dynamic> table) {
    final status = table['status'] as String;
    final isSelected = _selectedTable == table['table_no'];

    return Card(
      elevation: isSelected ? 6 : 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: isSelected ? const Color(0xFF3B82F6) : _getTableBorderColor(status),
          width: isSelected ? 3 : 2,
        ),
      ),
      child: InkWell(
        onTap: () => _onTableTap(table),
        borderRadius: BorderRadius.circular(12),
        child: Container(
          decoration: BoxDecoration(
            color: _getTableColor(status),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                _getTableIcon(status),
                size: 36,
                color: _getTableBorderColor(status),
              ),
              const SizedBox(height: 8),
              Text(
                table['table_no'],
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (status == 'occupied') ...[
                const SizedBox(height: 4),
                Text(
                  '${table['guests']} guests',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[700],
                  ),
                ),
                Text(
                  '${_currencyFormat.format(table['order_amount'])}원',
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF3B82F6),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSummaryItem(String label, dynamic value, Color color, {bool isCurrency = false}) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          isCurrency ? '${_currencyFormat.format(value)}원' : '$value',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}
