import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';

class ProductManagementScreen extends StatefulWidget {
  final int storeId;
  const ProductManagementScreen({super.key, required this.storeId});

  @override
  State<ProductManagementScreen> createState() => _ProductManagementScreenState();
}

class _ProductManagementScreenState extends State<ProductManagementScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _currencyFormat = NumberFormat("#,###", "ko_KR");

  List<dynamic> _categories = [];
  List<dynamic> _products = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final categories = await ApiService().getCategories(widget.storeId);
      final products = await ApiService().getAllProducts(widget.storeId);
      setState(() {
        _categories = categories;
        _products = products;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Load error: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Product Management'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.category), text: 'Categories'),
            Tab(icon: Icon(Icons.fastfood), text: 'Products'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildCategoriesTab(),
                _buildProductsTab(),
              ],
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          if (_tabController.index == 0) {
            _showCategoryDialog();
          } else {
            _showProductDialog();
          }
        },
        child: const Icon(Icons.add),
      ),
    );
  }

  // =====================================================
  // Categories Tab
  // =====================================================

  Widget _buildCategoriesTab() {
    if (_categories.isEmpty) {
      return const Center(child: Text('No categories. Add one!'));
    }

    return ReorderableListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _categories.length,
      onReorder: _reorderCategories,
      itemBuilder: (context, index) {
        final cat = _categories[index];
        return Card(
          key: ValueKey(cat['id']),
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: const Icon(Icons.drag_handle),
            title: Text(cat['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text('Order: ${cat['display_order']}'),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconButton(
                  icon: const Icon(Icons.edit, color: Colors.blue),
                  onPressed: () => _showCategoryDialog(category: cat),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () => _deleteCategory(cat['id']),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _reorderCategories(int oldIndex, int newIndex) async {
    if (newIndex > oldIndex) newIndex--;
    final item = _categories.removeAt(oldIndex);
    _categories.insert(newIndex, item);
    setState(() {});

    final ids = _categories.map<int>((c) => c['id'] as int).toList();
    await ApiService().reorderCategories(ids);
  }

  void _showCategoryDialog({Map<String, dynamic>? category}) {
    final nameController = TextEditingController(text: category?['name'] ?? '');
    final isEdit = category != null;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(isEdit ? 'Edit Category' : 'New Category'),
        content: TextField(
          controller: nameController,
          decoration: const InputDecoration(
            labelText: 'Category Name',
            border: OutlineInputBorder(),
          ),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (nameController.text.isEmpty) return;

              if (isEdit) {
                await ApiService().updateCategory(
                  category['id'],
                  {'name': nameController.text},
                );
              } else {
                await ApiService().createCategory({
                  'store_id': widget.storeId,
                  'name': nameController.text,
                  'display_order': _categories.length,
                });
              }

              if (mounted) {
                Navigator.pop(ctx);
                _loadData();
              }
            },
            child: Text(isEdit ? 'Update' : 'Create'),
          ),
        ],
      ),
    );
  }

  Future<void> _deleteCategory(int categoryId) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Category?'),
        content: const Text('This category must have no products.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      final success = await ApiService().deleteCategory(categoryId);
      if (success) {
        _loadData();
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to delete. Category may have products.')),
          );
        }
      }
    }
  }

  // =====================================================
  // Products Tab
  // =====================================================

  Widget _buildProductsTab() {
    if (_products.isEmpty) {
      return const Center(child: Text('No products. Add one!'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _products.length,
      itemBuilder: (context, index) {
        final product = _products[index];
        final isSoldout = product['is_soldout'] == true;
        final categoryName = _getCategoryName(product['category_id']);

        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          color: isSoldout ? Colors.grey[200] : null,
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: isSoldout ? Colors.grey : const Color(0xFF3B82F6),
              child: Icon(
                Icons.fastfood,
                color: Colors.white,
                size: 20,
              ),
            ),
            title: Row(
              children: [
                Expanded(
                  child: Text(
                    product['name'],
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      decoration: isSoldout ? TextDecoration.lineThrough : null,
                    ),
                  ),
                ),
                if (isSoldout)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.red,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Text(
                      'SOLDOUT',
                      style: TextStyle(color: Colors.white, fontSize: 10),
                    ),
                  ),
              ],
            ),
            subtitle: Text('$categoryName | ${_currencyFormat.format(product['price'])}won'),
            trailing: PopupMenuButton<String>(
              onSelected: (value) async {
                switch (value) {
                  case 'edit':
                    _showProductDialog(product: product);
                    break;
                  case 'soldout':
                    await ApiService().toggleSoldout(product['id']);
                    _loadData();
                    break;
                  case 'delete':
                    _deleteProduct(product['id']);
                    break;
                }
              },
              itemBuilder: (context) => [
                const PopupMenuItem(value: 'edit', child: Text('Edit')),
                PopupMenuItem(
                  value: 'soldout',
                  child: Text(isSoldout ? 'Mark Available' : 'Mark Soldout'),
                ),
                const PopupMenuItem(
                  value: 'delete',
                  child: Text('Delete', style: TextStyle(color: Colors.red)),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  String _getCategoryName(int categoryId) {
    final cat = _categories.firstWhere(
      (c) => c['id'] == categoryId,
      orElse: () => {'name': 'Unknown'},
    );
    return cat['name'];
  }

  void _showProductDialog({Map<String, dynamic>? product}) {
    final nameController = TextEditingController(text: product?['name'] ?? '');
    final priceController = TextEditingController(
      text: product?['price']?.toString() ?? '',
    );
    final descController = TextEditingController(text: product?['description'] ?? '');
    int? selectedCategoryId = product?['category_id'];
    final isEdit = product != null;

    if (_categories.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Create a category first!')),
      );
      return;
    }

    selectedCategoryId ??= _categories.first['id'];

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: Text(isEdit ? 'Edit Product' : 'New Product'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<int>(
                  value: selectedCategoryId,
                  decoration: const InputDecoration(
                    labelText: 'Category',
                    border: OutlineInputBorder(),
                  ),
                  items: _categories.map<DropdownMenuItem<int>>((cat) {
                    return DropdownMenuItem(
                      value: cat['id'] as int,
                      child: Text(cat['name']),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setDialogState(() => selectedCategoryId = value);
                  },
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'Product Name',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: priceController,
                  decoration: const InputDecoration(
                    labelText: 'Price (won)',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: descController,
                  decoration: const InputDecoration(
                    labelText: 'Description (optional)',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 2,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (nameController.text.isEmpty || priceController.text.isEmpty) {
                  return;
                }

                final data = {
                  'category_id': selectedCategoryId,
                  'name': nameController.text,
                  'price': int.tryParse(priceController.text) ?? 0,
                  'description': descController.text.isEmpty ? null : descController.text,
                };

                if (isEdit) {
                  await ApiService().updateProduct(product['id'], data);
                } else {
                  await ApiService().createProduct(data);
                }

                if (mounted) {
                  Navigator.pop(ctx);
                  _loadData();
                }
              },
              child: Text(isEdit ? 'Update' : 'Create'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _deleteProduct(int productId) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Product?'),
        content: const Text('This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await ApiService().deleteProduct(productId);
      _loadData();
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
}
