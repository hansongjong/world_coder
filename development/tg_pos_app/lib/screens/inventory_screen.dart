import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class InventoryScreen extends StatefulWidget {
  final int storeId;
  const InventoryScreen({super.key, required this.storeId});

  @override
  State<InventoryScreen> createState() => _InventoryScreenState();
}

class _InventoryScreenState extends State<InventoryScreen> {
  List<Map<String, dynamic>> _inventory = [];
  bool _isLoading = true;
  String _searchQuery = '';
  String _filterStatus = 'all'; // all, low, out
  final _numberFormat = NumberFormat("#,###", "ko_KR");

  @override
  void initState() {
    super.initState();
    _loadInventory();
  }

  Future<void> _loadInventory() async {
    setState(() => _isLoading = true);
    try {
      // In real app, this would come from API
      await Future.delayed(const Duration(milliseconds: 500));
      setState(() {
        _inventory = [
          {'id': 1, 'name': 'Coffee Beans (1kg)', 'sku': 'CB-001', 'stock': 15, 'min_stock': 10, 'unit': 'bags', 'cost': 25000},
          {'id': 2, 'name': 'Milk (1L)', 'sku': 'ML-001', 'stock': 24, 'min_stock': 20, 'unit': 'bottles', 'cost': 3500},
          {'id': 3, 'name': 'Sugar (1kg)', 'sku': 'SG-001', 'stock': 8, 'min_stock': 10, 'unit': 'bags', 'cost': 2500},
          {'id': 4, 'name': 'Paper Cups (100ct)', 'sku': 'PC-001', 'stock': 0, 'min_stock': 5, 'unit': 'packs', 'cost': 15000},
          {'id': 5, 'name': 'Straws (200ct)', 'sku': 'ST-001', 'stock': 12, 'min_stock': 5, 'unit': 'packs', 'cost': 8000},
          {'id': 6, 'name': 'Napkins (500ct)', 'sku': 'NP-001', 'stock': 3, 'min_stock': 10, 'unit': 'packs', 'cost': 12000},
          {'id': 7, 'name': 'Vanilla Syrup', 'sku': 'VS-001', 'stock': 6, 'min_stock': 5, 'unit': 'bottles', 'cost': 18000},
          {'id': 8, 'name': 'Caramel Syrup', 'sku': 'CS-001', 'stock': 4, 'min_stock': 5, 'unit': 'bottles', 'cost': 18000},
        ];
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load inventory: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  List<Map<String, dynamic>> get _filteredInventory {
    var items = _inventory;

    // Apply search filter
    if (_searchQuery.isNotEmpty) {
      items = items.where((item) {
        final name = (item['name'] as String).toLowerCase();
        final sku = (item['sku'] as String).toLowerCase();
        final query = _searchQuery.toLowerCase();
        return name.contains(query) || sku.contains(query);
      }).toList();
    }

    // Apply status filter
    if (_filterStatus == 'low') {
      items = items.where((item) {
        final stock = item['stock'] as int;
        final minStock = item['min_stock'] as int;
        return stock > 0 && stock <= minStock;
      }).toList();
    } else if (_filterStatus == 'out') {
      items = items.where((item) => item['stock'] == 0).toList();
    }

    return items;
  }

  String _getStockStatus(int stock, int minStock) {
    if (stock == 0) return 'out';
    if (stock <= minStock) return 'low';
    return 'ok';
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'out':
        return Colors.red;
      case 'low':
        return Colors.orange;
      default:
        return Colors.green;
    }
  }

  void _showStockUpdateDialog(Map<String, dynamic> item) {
    final controller = TextEditingController();
    String action = 'add';

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: Text('Update Stock: ${item['name']}'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Current Stock: ${item['stock']} ${item['unit']}'),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: RadioListTile<String>(
                      title: const Text('Add'),
                      value: 'add',
                      groupValue: action,
                      onChanged: (v) => setDialogState(() => action = v!),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                  Expanded(
                    child: RadioListTile<String>(
                      title: const Text('Remove'),
                      value: 'remove',
                      groupValue: action,
                      onChanged: (v) => setDialogState(() => action = v!),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              TextField(
                controller: controller,
                decoration: InputDecoration(
                  labelText: 'Quantity',
                  suffixText: item['unit'],
                  border: const OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
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
                final qty = int.tryParse(controller.text) ?? 0;
                if (qty <= 0) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Enter valid quantity')),
                  );
                  return;
                }
                Navigator.pop(context);
                _updateStock(item, action, qty);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF3B82F6),
                foregroundColor: Colors.white,
              ),
              child: const Text('Update'),
            ),
          ],
        ),
      ),
    );
  }

  void _updateStock(Map<String, dynamic> item, String action, int qty) {
    setState(() {
      final idx = _inventory.indexWhere((i) => i['id'] == item['id']);
      if (idx != -1) {
        var newStock = item['stock'] as int;
        if (action == 'add') {
          newStock += qty;
        } else {
          newStock = (newStock - qty).clamp(0, 999999);
        }
        _inventory[idx] = {..._inventory[idx], 'stock': newStock};
      }
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Stock updated for ${item['name']}')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final outOfStock = _inventory.where((i) => i['stock'] == 0).length;
    final lowStock = _inventory.where((i) {
      final stock = i['stock'] as int;
      final minStock = i['min_stock'] as int;
      return stock > 0 && stock <= minStock;
    }).length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Inventory'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadInventory,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Summary
                Container(
                  padding: const EdgeInsets.all(16),
                  color: const Color(0xFF1E293B),
                  child: Row(
                    children: [
                      Expanded(
                        child: _buildSummaryCard(
                          'Total Items',
                          '${_inventory.length}',
                          Icons.inventory_2,
                          Colors.blue,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildSummaryCard(
                          'Low Stock',
                          '$lowStock',
                          Icons.warning,
                          Colors.orange,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildSummaryCard(
                          'Out of Stock',
                          '$outOfStock',
                          Icons.error,
                          Colors.red,
                        ),
                      ),
                    ],
                  ),
                ),
                // Search & Filter
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          decoration: const InputDecoration(
                            hintText: 'Search by name or SKU...',
                            prefixIcon: Icon(Icons.search),
                            border: OutlineInputBorder(),
                            contentPadding: EdgeInsets.symmetric(vertical: 0, horizontal: 12),
                          ),
                          onChanged: (v) => setState(() => _searchQuery = v),
                        ),
                      ),
                      const SizedBox(width: 12),
                      DropdownButton<String>(
                        value: _filterStatus,
                        items: const [
                          DropdownMenuItem(value: 'all', child: Text('All')),
                          DropdownMenuItem(value: 'low', child: Text('Low Stock')),
                          DropdownMenuItem(value: 'out', child: Text('Out of Stock')),
                        ],
                        onChanged: (v) => setState(() => _filterStatus = v!),
                      ),
                    ],
                  ),
                ),
                // Inventory List
                Expanded(
                  child: _filteredInventory.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.inventory_2, size: 60, color: Colors.grey[300]),
                              const SizedBox(height: 10),
                              Text(
                                'No items found',
                                style: TextStyle(color: Colors.grey[500]),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: _filteredInventory.length,
                          itemBuilder: (context, index) {
                            final item = _filteredInventory[index];
                            return _buildInventoryCard(item);
                          },
                        ),
                ),
              ],
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddItemDialog,
        backgroundColor: const Color(0xFF3B82F6),
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }

  Widget _buildSummaryCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInventoryCard(Map<String, dynamic> item) {
    final stock = item['stock'] as int;
    final minStock = item['min_stock'] as int;
    final status = _getStockStatus(stock, minStock);
    final statusColor = _getStatusColor(status);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _showStockUpdateDialog(item),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Status indicator
              Container(
                width: 8,
                height: 60,
                decoration: BoxDecoration(
                  color: statusColor,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              const SizedBox(width: 16),
              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item['name'],
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'SKU: ${item['sku']}',
                      style: TextStyle(color: Colors.grey[600], fontSize: 13),
                    ),
                    Text(
                      'Cost: ${_numberFormat.format(item['cost'])}원',
                      style: TextStyle(color: Colors.grey[500], fontSize: 12),
                    ),
                  ],
                ),
              ),
              // Stock info
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '${item['stock']}',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: statusColor,
                    ),
                  ),
                  Text(
                    item['unit'],
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                  if (status != 'ok')
                    Container(
                      margin: const EdgeInsets.only(top: 4),
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: statusColor.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        status == 'out' ? 'OUT' : 'LOW',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: statusColor,
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(width: 8),
              Icon(Icons.chevron_right, color: Colors.grey[400]),
            ],
          ),
        ),
      ),
    );
  }

  void _showAddItemDialog() {
    final nameController = TextEditingController();
    final skuController = TextEditingController();
    final stockController = TextEditingController();
    final minStockController = TextEditingController(text: '10');
    final costController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Inventory Item'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'Item Name',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: skuController,
                decoration: const InputDecoration(
                  labelText: 'SKU',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: stockController,
                      decoration: const InputDecoration(
                        labelText: 'Initial Stock',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextField(
                      controller: minStockController,
                      decoration: const InputDecoration(
                        labelText: 'Min Stock',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              TextField(
                controller: costController,
                decoration: const InputDecoration(
                  labelText: 'Unit Cost (원)',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (nameController.text.isEmpty || skuController.text.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Name and SKU are required')),
                );
                return;
              }
              Navigator.pop(context);
              setState(() {
                _inventory.add({
                  'id': _inventory.length + 1,
                  'name': nameController.text,
                  'sku': skuController.text,
                  'stock': int.tryParse(stockController.text) ?? 0,
                  'min_stock': int.tryParse(minStockController.text) ?? 10,
                  'unit': 'units',
                  'cost': int.tryParse(costController.text) ?? 0,
                });
              });
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Added ${nameController.text}')),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF3B82F6),
              foregroundColor: Colors.white,
            ),
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }
}
