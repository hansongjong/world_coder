import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../providers/cart_provider.dart';
import '../providers/store_config_provider.dart';
import '../widgets/payment_modal.dart';
import '../widgets/receipt_dialog.dart';
import '../l10n/app_localizations.dart';
import 'reservation_screen.dart';
import 'login_screen.dart';
import 'product_management_screen.dart';
import 'order_history_screen.dart';
import 'sales_report_screen.dart';
import 'table_map_screen.dart';
import 'queue_screen.dart';
import 'inventory_screen.dart';
import 'store_settings_screen.dart';
import 'subscription_screen.dart';

class PosScreen extends StatefulWidget {
  final int storeId;
  const PosScreen({super.key, required this.storeId});

  @override
  State<PosScreen> createState() => _PosScreenState();
}

class _PosScreenState extends State<PosScreen> {
  List<dynamic> _menuData = [];
  bool _isLoading = true;
  String? _selectedCategory;
  final _currencyFormat = NumberFormat("#,###", "ko_KR");

  @override
  void initState() {
    super.initState();
    _loadMenu();
  }

  Future<void> _loadMenu() async {
    setState(() => _isLoading = true);
    try {
      final data = await ApiService().getMenu(widget.storeId);
      setState(() {
        _menuData = data;
        if (data.isNotEmpty) {
          _selectedCategory = data[0]['category_name'];
        }
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Menu load error: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  List<dynamic> get _currentProducts {
    if (_selectedCategory == null) return [];
    final category = _menuData.firstWhere(
      (c) => c['category_name'] == _selectedCategory,
      orElse: () => {'items': []},
    );
    return category['items'] ?? [];
  }

  void _showPaymentModal() {
    final cart = context.read<CartProvider>();
    if (cart.items.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('장바구니가 비었습니다')),
      );
      return;
    }
    showDialog(
      context: context,
      builder: (_) => PaymentModal(
        total: cart.totalAmount,
        onDone: (method, received, change, {discountAmount, discountType}) =>
            _placeOrder(method, received, change,
                discountAmount: discountAmount, discountType: discountType),
      ),
    );
  }

  Future<void> _placeOrder(String method, int received, int change,
      {int? discountAmount, String? discountType}) async {
    final cart = context.read<CartProvider>();
    try {
      final Map<String, dynamic> orderData = {
        "store_id": widget.storeId,
        "table_no": "POS",
        "items": cart.items
            .map((e) => {"product_id": e.productId, "quantity": e.quantity})
            .toList(),
      };

      // Add discount info if present
      if (discountAmount != null && discountAmount > 0) {
        orderData["discount_amount"] = discountAmount;
        orderData["discount_type"] = discountType ?? "amount";
      }

      await ApiService().placeOrder(orderData);

      final items = List.from(cart.items);
      final total = cart.totalAmount - (discountAmount ?? 0);
      cart.clear();

      if (mounted) {
        showDialog(
          context: context,
          builder: (_) => ReceiptDialog(
            id: "ORD-${DateTime.now().millisecondsSinceEpoch}",
            total: total,
            method: method,
            rec: received,
            chg: change,
            items: items,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('주문 실패: $e')),
        );
      }
    }
  }

  void _logout() {
    context.read<CartProvider>().clear();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isWide = MediaQuery.of(context).size.width > 800;
    final config = context.watch<StoreConfigProvider>();
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(config.storeName.isNotEmpty ? config.storeName : 'TG-POS'),
        actions: [
          // Refresh Menu
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadMenu,
            tooltip: l10n.get('refresh'),
          ),
          // Table Map (Restaurant mode)
          if (config.isRestaurant || config.uiMode == 'TABLE_MANAGER')
            IconButton(
              icon: const Icon(Icons.table_restaurant),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => TableMapScreen(storeId: widget.storeId),
                ),
              ),
              tooltip: l10n.get('table_map'),
            ),
          // Queue (Cafe/Hospital mode)
          if (config.hasQueue)
            IconButton(
              icon: const Icon(Icons.queue),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => QueueScreen(storeId: widget.storeId),
                ),
              ),
              tooltip: l10n.get('queue'),
            ),
          // Inventory (Retail mode or enabled)
          if (config.hasInventory)
            IconButton(
              icon: const Icon(Icons.inventory),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => InventoryScreen(storeId: widget.storeId),
                ),
              ),
              tooltip: l10n.get('inventory'),
            ),
          // Subscription (GYM mode or enabled)
          if (config.hasSubscription)
            IconButton(
              icon: const Icon(Icons.card_membership),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => SubscriptionScreen(storeId: widget.storeId),
                ),
              ),
              tooltip: l10n.get('subscription'),
            ),
          // Product Management
          IconButton(
            icon: const Icon(Icons.inventory_2),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => ProductManagementScreen(storeId: widget.storeId),
              ),
            ).then((_) => _loadMenu()),
            tooltip: l10n.get('menu'),
          ),
          // Order History
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => OrderHistoryScreen(storeId: widget.storeId),
              ),
            ),
            tooltip: l10n.get('order'),
          ),
          // Sales Report
          IconButton(
            icon: const Icon(Icons.bar_chart),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => SalesReportScreen(storeId: widget.storeId),
              ),
            ),
            tooltip: l10n.get('reports'),
          ),
          // Reservations (if enabled)
          if (config.hasReservation)
            IconButton(
              icon: const Icon(Icons.calendar_today),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ReservationScreen(storeId: widget.storeId),
                ),
              ),
              tooltip: l10n.get('reservation'),
            ),
          // Store Settings
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => StoreSettingsScreen(storeId: widget.storeId),
              ),
            ).then((_) => _loadMenu()),
            tooltip: l10n.get('settings'),
          ),
          // Logout
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
            tooltip: l10n.get('logout'),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : isWide
              ? _buildWideLayout()
              : _buildNarrowLayout(),
    );
  }

  // Wide layout (Desktop/Tablet)
  Widget _buildWideLayout() {
    return Row(
      children: [
        // Menu Panel
        Expanded(
          flex: 2,
          child: Column(
            children: [
              _buildCategoryTabs(),
              Expanded(child: _buildProductGrid()),
            ],
          ),
        ),
        // Cart Panel
        SizedBox(
          width: 350,
          child: _buildCartPanel(),
        ),
      ],
    );
  }

  // Narrow layout (Mobile)
  Widget _buildNarrowLayout() {
    return Column(
      children: [
        _buildCategoryTabs(),
        Expanded(child: _buildProductGrid()),
        _buildMobileCartBar(),
      ],
    );
  }

  Widget _buildCategoryTabs() {
    return Container(
      height: 50,
      color: Colors.grey[100],
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: _menuData.length,
        padding: const EdgeInsets.symmetric(horizontal: 10),
        itemBuilder: (context, index) {
          final cat = _menuData[index];
          final isSelected = cat['category_name'] == _selectedCategory;
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 8),
            child: ChoiceChip(
              label: Text(cat['category_name']),
              selected: isSelected,
              onSelected: (_) {
                setState(() => _selectedCategory = cat['category_name']);
              },
              selectedColor: const Color(0xFF3B82F6),
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : Colors.black87,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildProductGrid() {
    final products = _currentProducts;
    if (products.isEmpty) {
      return const Center(child: Text('No products in this category'));
    }

    return GridView.builder(
      padding: const EdgeInsets.all(15),
      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 180,
        childAspectRatio: 0.9,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: products.length,
      itemBuilder: (context, index) {
        final product = products[index];
        return _buildProductCard(product);
      },
    );
  }

  Widget _buildProductCard(dynamic product) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: () {
          context.read<CartProvider>().addToCart(
                product['id'],
                product['name'],
                product['price'],
              );
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('${product['name']} added'),
              duration: const Duration(milliseconds: 500),
            ),
          );
        },
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.fastfood,
                size: 40,
                color: Colors.grey[400],
              ),
              const SizedBox(height: 10),
              Text(
                product['name'],
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 5),
              Text(
                '${_currencyFormat.format(product['price'])}원',
                style: const TextStyle(
                  color: Color(0xFF3B82F6),
                  fontWeight: FontWeight.bold,
                  fontSize: 15,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCartPanel() {
    final l10n = AppLocalizations.of(context);
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 10,
            offset: const Offset(-2, 0),
          ),
        ],
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(15),
            color: const Color(0xFF1E293B),
            child: Row(
              children: [
                const Icon(Icons.shopping_cart, color: Colors.white),
                const SizedBox(width: 10),
                Text(
                  l10n.get('order_list'),
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
          ),
          // Cart Items
          Expanded(
            child: Consumer<CartProvider>(
              builder: (context, cart, _) {
                if (cart.items.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.shopping_cart_outlined,
                            size: 60, color: Colors.grey[300]),
                        const SizedBox(height: 10),
                        Text(l10n.get('empty_cart'),
                            style: TextStyle(color: Colors.grey[500])),
                      ],
                    ),
                  );
                }
                return ListView.builder(
                  itemCount: cart.items.length,
                  padding: const EdgeInsets.all(10),
                  itemBuilder: (context, index) {
                    final item = cart.items[index];
                    return Card(
                      child: ListTile(
                        title: Text(item.name),
                        subtitle: Text(
                          '${_currencyFormat.format(item.price)}원 x ${item.quantity}',
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              '${_currencyFormat.format(item.price * item.quantity)}원',
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            IconButton(
                              icon: const Icon(Icons.remove_circle_outline,
                                  color: Colors.red),
                              onPressed: () => cart.removeFromCart(index),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
          // Footer
          Container(
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              border: Border(top: BorderSide(color: Colors.grey[200]!)),
            ),
            child: Consumer<CartProvider>(
              builder: (context, cart, _) => Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        l10n.get('total'),
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '${_currencyFormat.format(cart.totalAmount)}원',
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF3B82F6),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 15),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: cart.items.isEmpty ? null : cart.clear,
                          child: Text(l10n.get('clear_cart')),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        flex: 2,
                        child: ElevatedButton(
                          onPressed: cart.items.isEmpty ? null : _showPaymentModal,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF3B82F6),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 15),
                          ),
                          child: Text(
                            l10n.get('pay'),
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMobileCartBar() {
    final l10n = AppLocalizations.of(context);
    return Consumer<CartProvider>(
      builder: (context, cart, _) => Container(
        padding: const EdgeInsets.all(15),
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
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '${cart.items.length} items',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  Text(
                    '${_currencyFormat.format(cart.totalAmount)}원',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            ElevatedButton(
              onPressed: cart.items.isEmpty ? null : _showPaymentModal,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF3B82F6),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15),
              ),
              child: Text(
                l10n.get('pay'),
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
