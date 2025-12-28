import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = "http://127.0.0.1:8001";

  Future<String> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString("access_token") ?? "";
  }

  Map<String, String> _authHeaders(String token) => {
    "Authorization": "Bearer $token",
    "Content-Type": "application/json",
  };

  // =====================================================
  // Auth
  // =====================================================

  /// 1단계: 로그인 (유저 확인 + 접근 가능한 매장 목록 반환)
  Future<Map<String, dynamic>?> loginWithStores(String username, String password) async {
    try {
      final res = await http.post(
        Uri.parse("$baseUrl/auth/login"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"username": username, "password": password}),
      );
      if (res.statusCode == 200) {
        return jsonDecode(utf8.decode(res.bodyBytes));
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  /// 2단계: 매장 선택 → JWT 토큰 발급
  Future<Map<String, dynamic>?> selectStore(int userId, int storeId) async {
    try {
      final res = await http.post(
        Uri.parse("$baseUrl/auth/select-store"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"user_id": userId, "store_id": storeId}),
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        // 토큰 저장
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString("access_token", data["access_token"]);
        await prefs.setInt("user_id", data["user_id"]);
        await prefs.setInt("store_id", data["store_id"]);
        await prefs.setString("username", data["username"]);
        await prefs.setString("store_name", data["store_name"]);
        await prefs.setString("role", data["role"]);
        return data;
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  /// 로그아웃 (토큰 삭제)
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove("access_token");
    await prefs.remove("user_id");
    await prefs.remove("store_id");
    await prefs.remove("username");
    await prefs.remove("store_name");
    await prefs.remove("role");
  }

  /// 현재 저장된 store_id 가져오기
  Future<int?> getCurrentStoreId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt("store_id");
  }

  /// 현재 저장된 user_id 가져오기
  Future<int?> getCurrentUserId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt("user_id");
  }

  /// 기존 OAuth2 호환 로그인 (단일 매장용 - 첫 번째 매장 자동 선택)
  Future<bool> login(String u, String p) async {
    try {
      final res = await http.post(
        Uri.parse("$baseUrl/auth/token"),
        body: {"username": u, "password": p},
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString("access_token", data["access_token"]);
        await prefs.setInt("store_id", data["store_id"]);
        await prefs.setInt("user_id", data["user_id"]);
        await prefs.setString("role", data["role"]);
        if (data["store_name"] != null) {
          await prefs.setString("store_name", data["store_name"]);
        }
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  // =====================================================
  // Products & Menu
  // =====================================================

  Future<List<dynamic>> getMenu(int storeId) async {
    final t = await _getToken();
    final res = await http.get(
      Uri.parse("$baseUrl/products/menu/$storeId"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : [];
  }

  Future<List<dynamic>> getAllProducts(int storeId, {bool includeSoldout = true}) async {
    final t = await _getToken();
    final res = await http.get(
      Uri.parse("$baseUrl/products/list/$storeId?include_soldout=$includeSoldout"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : [];
  }

  Future<Map<String, dynamic>?> createProduct(Map<String, dynamic> data) async {
    final t = await _getToken();
    final res = await http.post(
      Uri.parse("$baseUrl/products/"),
      headers: _authHeaders(t),
      body: jsonEncode(data),
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  Future<Map<String, dynamic>?> updateProduct(int productId, Map<String, dynamic> data) async {
    final t = await _getToken();
    final res = await http.put(
      Uri.parse("$baseUrl/products/$productId"),
      headers: _authHeaders(t),
      body: jsonEncode(data),
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  Future<bool> deleteProduct(int productId) async {
    final t = await _getToken();
    final res = await http.delete(
      Uri.parse("$baseUrl/products/$productId"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200;
  }

  Future<bool> toggleSoldout(int productId) async {
    final t = await _getToken();
    final res = await http.put(
      Uri.parse("$baseUrl/products/$productId/soldout"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200;
  }

  // =====================================================
  // Categories
  // =====================================================

  Future<List<dynamic>> getCategories(int storeId) async {
    final t = await _getToken();
    final res = await http.get(
      Uri.parse("$baseUrl/products/categories/$storeId"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : [];
  }

  Future<Map<String, dynamic>?> createCategory(Map<String, dynamic> data) async {
    final t = await _getToken();
    final res = await http.post(
      Uri.parse("$baseUrl/products/categories/"),
      headers: _authHeaders(t),
      body: jsonEncode(data),
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  Future<Map<String, dynamic>?> updateCategory(int categoryId, Map<String, dynamic> data) async {
    final t = await _getToken();
    final res = await http.put(
      Uri.parse("$baseUrl/products/categories/$categoryId"),
      headers: _authHeaders(t),
      body: jsonEncode(data),
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  Future<bool> deleteCategory(int categoryId) async {
    final t = await _getToken();
    final res = await http.delete(
      Uri.parse("$baseUrl/products/categories/$categoryId"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200;
  }

  Future<bool> reorderCategories(List<int> categoryIds) async {
    final t = await _getToken();
    final res = await http.put(
      Uri.parse("$baseUrl/products/categories/reorder"),
      headers: _authHeaders(t),
      body: jsonEncode({"category_ids": categoryIds}),
    );
    return res.statusCode == 200;
  }

  // =====================================================
  // Orders
  // =====================================================

  Future<Map<String, dynamic>?> placeOrder(Map<String, dynamic> d) async {
    final t = await _getToken();
    final res = await http.post(
      Uri.parse("$baseUrl/orders/place"),
      headers: _authHeaders(t),
      body: jsonEncode(d),
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  Future<List<dynamic>> getActiveOrders(int storeId) async {
    final t = await _getToken();
    final res = await http.get(
      Uri.parse("$baseUrl/orders/list/$storeId"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : [];
  }

  Future<bool> updateOrderStatus(String orderId, String status) async {
    final t = await _getToken();
    final res = await http.put(
      Uri.parse("$baseUrl/orders/$orderId/status"),
      headers: _authHeaders(t),
      body: jsonEncode({"status": status}),
    );
    return res.statusCode == 200;
  }

  Future<Map<String, dynamic>> getOrderHistory(
    int storeId, {
    String? date,
    String? status,
    int limit = 50,
    int offset = 0,
  }) async {
    final t = await _getToken();
    var url = "$baseUrl/orders/history/$storeId?limit=$limit&offset=$offset";
    if (date != null) url += "&date=$date";
    if (status != null && status.isNotEmpty) url += "&status=$status";

    final res = await http.get(
      Uri.parse(url),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200
        ? jsonDecode(utf8.decode(res.bodyBytes))
        : {"total": 0, "orders": []};
  }

  Future<Map<String, dynamic>?> getOrderDetail(String orderId) async {
    final t = await _getToken();
    final res = await http.get(
      Uri.parse("$baseUrl/orders/$orderId"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  Future<Map<String, dynamic>?> refundOrder(String orderId, String reason, {int? partialAmount}) async {
    final t = await _getToken();
    final body = <String, dynamic>{"reason": reason};
    if (partialAmount != null) {
      body["partial_amount"] = partialAmount;
    }
    final res = await http.post(
      Uri.parse("$baseUrl/orders/refund/$orderId"),
      headers: _authHeaders(t),
      body: jsonEncode(body),
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  // =====================================================
  // Reservations
  // =====================================================

  Future<List<dynamic>> getReservations(int storeId) async {
    final t = await _getToken();
    final res = await http.get(
      Uri.parse("$baseUrl/booking/list/$storeId"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(res.body) : [];
  }

  // =====================================================
  // Membership
  // =====================================================

  Future<void> earnPoints(int storeId, String phone, int amount) async {
    final t = await _getToken();
    await http.post(
      Uri.parse("$baseUrl/membership/earn"),
      headers: _authHeaders(t),
      body: jsonEncode({
        "store_id": storeId,
        "user_phone": phone,
        "amount": amount,
      }),
    );
  }

  // =====================================================
  // Stats
  // =====================================================

  Future<Map<String, dynamic>?> getDailyReport(int storeId, {String? date}) async {
    final t = await _getToken();
    var url = "$baseUrl/stats/daily?store_id=$storeId";
    if (date != null) url += "&date=$date";

    final res = await http.get(
      Uri.parse(url),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  Future<Map<String, dynamic>?> getRangeReport(int storeId, String startDate, String endDate) async {
    final t = await _getToken();
    final url = "$baseUrl/stats/range?store_id=$storeId&start_date=$startDate&end_date=$endDate";

    final res = await http.get(
      Uri.parse(url),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  Future<Map<String, dynamic>?> getDashboardSummary(int storeId) async {
    final t = await _getToken();
    final res = await http.get(
      Uri.parse("$baseUrl/stats/summary?store_id=$storeId"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  Future<List<dynamic>> getSalesTrend(int storeId, {int days = 7}) async {
    final t = await _getToken();
    final res = await http.get(
      Uri.parse("$baseUrl/stats/sales/daily?store_id=$storeId&days=$days"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : [];
  }

  Future<List<dynamic>> getProductRanking(int storeId, {int limit = 10}) async {
    final t = await _getToken();
    final res = await http.get(
      Uri.parse("$baseUrl/stats/products/rank?store_id=$storeId&limit=$limit"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : [];
  }

  Future<List<dynamic>> getHourlyTrend(int storeId, {String? date}) async {
    final t = await _getToken();
    var url = "$baseUrl/stats/hourly?store_id=$storeId";
    if (date != null) url += "&date=$date";

    final res = await http.get(
      Uri.parse(url),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : [];
  }

  // =====================================================
  // Store Config
  // =====================================================

  Future<Map<String, dynamic>?> getStoreConfig(int storeId) async {
    final t = await _getToken();
    final res = await http.get(
      Uri.parse("$baseUrl/store/config/$storeId"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  Future<Map<String, dynamic>?> updateStoreConfig(int storeId, Map<String, dynamic> data) async {
    final t = await _getToken();
    final res = await http.put(
      Uri.parse("$baseUrl/store/config/$storeId"),
      headers: _authHeaders(t),
      body: jsonEncode(data),
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
  }

  Future<List<dynamic>> getStoreTemplates() async {
    final t = await _getToken();
    final res = await http.get(
      Uri.parse("$baseUrl/store/templates"),
      headers: {"Authorization": "Bearer $t"},
    );
    return res.statusCode == 200 ? jsonDecode(utf8.decode(res.bodyBytes)) : [];
  }
}
