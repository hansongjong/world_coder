import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = "http://127.0.0.1:8001";

  Future<String> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString("access_token") ?? "";
  }

  Future<bool> login(String u, String p) async {
    try {
      final res = await http.post(Uri.parse("$baseUrl/auth/token"), body: {"username": u, "password": p});
      if (res.statusCode == 200) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString("access_token", jsonDecode(res.body)["access_token"]);
        return true;
      }
      return false;
    } catch(e) { return false; }
  }

  Future<List<dynamic>> getMenu(int id) async {
    final t = await _getToken();
    final res = await http.get(Uri.parse("$baseUrl/products/menu/$id"), headers: {"Authorization": "Bearer $t"});
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : [];
  }

  Future<void> placeOrder(Map<String, dynamic> d) async {
    final t = await _getToken();
    await http.post(Uri.parse("$baseUrl/orders/place"), headers: {"Authorization": "Bearer $t", "Content-Type": "application/json"}, body: jsonEncode(d));
  }

  Future<List<dynamic>> getReservations(int id) async {
    final t = await _getToken();
    final res = await http.get(Uri.parse("$baseUrl/booking/list/$id"), headers: {"Authorization": "Bearer $t"});
    return res.statusCode == 200 ? jsonDecode(res.body) : [];
  }

  Future<void> earnPoints(int id, String p, int a) async {
    final t = await _getToken();
    await http.post(Uri.parse("$baseUrl/membership/earn"), headers: {"Authorization": "Bearer $t", "Content-Type": "application/json"}, body: jsonEncode({"store_id": id, "user_phone": p, "amount": a}));
  }
}
