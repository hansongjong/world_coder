import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  // 에뮬레이터 사용 시 10.0.2.2, 실제 기기는 서버 IP 필요
  static const String baseUrl = "http://127.0.0.1:8001"; 
  final storage = const FlutterSecureStorage();

  // 1. 로그인
  Future<Map<String, dynamic>> login(String username, String password) async {
    final url = Uri.parse("$baseUrl/auth/token");
    final response = await http.post(
      url,
      headers: {"Content-Type": "application/x-www-form-urlencoded"},
      body: {"username": username, "password": password},
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await storage.write(key: "access_token", value: data["access_token"]);
      return data;
    } else {
      throw Exception("Login Failed: ${response.body}");
    }
  }

  // 2. 메뉴 조회
  Future<List<dynamic>> getMenu(int storeId) async {
    final token = await storage.read(key: "access_token");
    final url = Uri.parse("$baseUrl/products/menu/$storeId");
    
    final response = await http.get(
      url,
      headers: {"Authorization": "Bearer $token"},
    );

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes));
    } else {
      throw Exception("Failed to load menu");
    }
  }

  // 3. 주문 전송
  Future<Map<String, dynamic>> placeOrder(Map<String, dynamic> orderData) async {
    final token = await storage.read(key: "access_token");
    final url = Uri.parse("$baseUrl/orders/place");

    final response = await http.post(
      url,
      headers: {
        "Authorization": "Bearer $token",
        "Content-Type": "application/json"
      },
      body: jsonEncode(orderData),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Order Failed: ${response.body}");
    }
  }
}