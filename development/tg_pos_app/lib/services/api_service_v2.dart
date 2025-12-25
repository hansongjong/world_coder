import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// 기존 ApiService를 상속하거나 확장하여 V2 기능 추가
class ApiServiceV2 {
  static const String baseUrl = "http://127.0.0.1:8001";
  final storage = const FlutterSecureStorage();

  Future<String> _getToken() async {
    return await storage.read(key: "access_token") ?? "";
  }

  // --- Membership ---
  Future<Map<String, dynamic>> checkPoints(int storeId, String phone) async {
    final token = await _getToken();
    final url = Uri.parse("$baseUrl/membership/check/$storeId/$phone");
    final response = await http.get(url, headers: {"Authorization": "Bearer $token"});
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return {"exists": false, "points": 0};
  }

  Future<void> earnPoints(int storeId, String phone, int amount) async {
    final token = await _getToken();
    final url = Uri.parse("$baseUrl/membership/earn");
    
    await http.post(
      url,
      headers: {
        "Authorization": "Bearer $token",
        "Content-Type": "application/json"
      },
      body: jsonEncode({
        "store_id": storeId,
        "user_phone": phone,
        "amount": amount
      }),
    );
  }

  // --- Booking ---
  Future<List<dynamic>> getReservations(int storeId) async {
    final token = await _getToken();
    final url = Uri.parse("$baseUrl/booking/list/$storeId");
    final response = await http.get(url, headers: {"Authorization": "Bearer $token"});

    if (response.statusCode == 200) {
      return jsonDecode(response.body); // JSON String -> List
    } else {
      throw Exception("Failed to load reservations");
    }
  }

  // --- Inventory (SCM) ---
  // 주문 시 재고 차감은 백엔드에서 Order 처리 시 자동 수행되므로,
  // 여기서는 재고 부족 알림을 확인하는 용도 등으로 사용 가능
  Future<List<dynamic>> getInventoryList(int storeId) async {
    final token = await _getToken();
    final url = Uri.parse("$baseUrl/inventory/list/$storeId");
    final response = await http.get(url, headers: {"Authorization": "Bearer $token"});
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return [];
  }
}