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
}

class CartProvider with ChangeNotifier {
  final List<CartItem> _items = [];

  List<CartItem> get items => _items;

  int get totalAmount {
    return _items.fold(0, (sum, item) => sum + (item.price * item.quantity));
  }

  void addToCart(int id, String name, int price) {
    final index = _items.indexWhere((item) => item.productId == id);
    if (index >= 0) {
      _items[index].quantity++;
    } else {
      _items.add(CartItem(productId: id, name: name, price: price));
    }
    notifyListeners();
  }

  void removeFromCart(int index) {
    _items.removeAt(index);
    notifyListeners();
  }

  void clear() {
    _items.clear();
    notifyListeners();
  }
}