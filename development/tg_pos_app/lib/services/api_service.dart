import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static const String baseUrl = "http://127.0.0.1:8001";
  final storage = const FlutterSecureStorage();

  Future<String> _getToken() async {
    return await storage.read(key: "access_token") ?? "";
  }

  Future<bool> login(String username, String password) async {
    try {
      final url = Uri.parse("$baseUrl/auth/token");
      final response = await http.post(
        url,
        body: {"username": username, "password": password},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await storage.write(key: "access_token", value: data["access_token"]);
        return true;
      }
      return false;
    } catch (e) {
      print("Login Error: $e");
      return false;
    }
  }

  Future<List<dynamic>> getMenu(int storeId) async {
    try {
      final token = await _getToken();
      final url = Uri.parse("$baseUrl/products/menu/$storeId");
      final response = await http.get(url, headers: {"Authorization": "Bearer $token"});
      
      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes));
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  Future<void> placeOrder(Map<String, dynamic> data) async {
    final token = await _getToken();
    final url = Uri.parse("$baseUrl/orders/place");
    await http.post(
      url,
      headers: {
        "Authorization": "Bearer $token",
        "Content-Type": "application/json"
      },
      body: jsonEncode(data),
    );
  }
}