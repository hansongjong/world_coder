import 'package:flutter/material.dart';

class CartItem {
  final int productId;
  final String name;
  final int price;
  int quantity;

  CartItem({
    required this.productId,
    required this.name,
    required this.price,
    this.quantity = 1,
  });

  int get total => price * quantity;
}

class CartProvider with ChangeNotifier {
  final List<CartItem> _items = [];

  List<CartItem> get items => _items;

  int get totalAmount {
    return _items.fold(0, (sum, item) => sum + item.total);
  }

  void addToCart(int id, String name, int price) {
    // 이미 있는 상품인지 확인
    final existingIndex = _items.indexWhere((item) => item.productId == id);
    
    if (existingIndex >= 0) {
      _items[existingIndex].quantity++;
    } else {
      _items.add(CartItem(productId: id, name: name, price: price));
    }
    notifyListeners();
  }

  void removeFromCart(int index) {
    _items.removeAt(index);
    notifyListeners();
  }

  void clearCart() {
    _items.clear();
    notifyListeners();
  }
}