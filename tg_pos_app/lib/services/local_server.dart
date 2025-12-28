import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:shelf/shelf.dart';
import 'package:shelf/shelf_io.dart' as shelf_io;
import 'package:shelf_router/shelf_router.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

/// POS 로컬 서버 - KDS/키오스크/테이블오더 연결용
class LocalServer {
  HttpServer? _server;
  final int port;
  final List<WebSocket> _wsClients = [];

  // 콜백: 외부에서 데이터 제공
  Future<List<Map<String, dynamic>>> Function()? onGetOrders;
  Future<List<Map<String, dynamic>>> Function()? onGetProducts;
  Future<Map<String, dynamic>> Function(Map<String, dynamic>)? onPlaceOrder;
  Future<bool> Function(String orderId, String status)? onUpdateOrderStatus;

  LocalServer({this.port = 8080});

  /// 서버 시작
  Future<void> start() async {
    final router = Router();

    // CORS 미들웨어
    Handler corsMiddleware(Handler handler) {
      return (Request request) async {
        if (request.method == 'OPTIONS') {
          return Response.ok('', headers: _corsHeaders);
        }
        final response = await handler(request);
        return response.change(headers: _corsHeaders);
      };
    }

    // API 라우트 설정
    router.get('/orders/list/<storeId>', _handleGetOrders);
    router.get('/products/menu/<storeId>', _handleGetProducts);
    router.post('/orders/place', _handlePlaceOrder);
    router.put('/orders/<orderId>/status', _handleUpdateStatus);
    router.get('/health', _handleHealth);

    // WebSocket 엔드포인트는 별도 처리
    final handler = const Pipeline()
        .addMiddleware(corsMiddleware)
        .addHandler(router.call);

    _server = await shelf_io.serve(handler, '0.0.0.0', port);
    print('[LocalServer] Running on http://${_server!.address.host}:${_server!.port}');
  }

  /// 서버 중지
  Future<void> stop() async {
    for (var ws in _wsClients) {
      await ws.close();
    }
    _wsClients.clear();
    await _server?.close();
    _server = null;
    print('[LocalServer] Stopped');
  }

  /// 서버 실행 중 여부
  bool get isRunning => _server != null;

  /// 서버 주소
  String? get address => _server != null
      ? 'http://${_server!.address.host}:${_server!.port}'
      : null;

  /// 모든 KDS 클라이언트에 주문 브로드캐스트
  void broadcastOrder(Map<String, dynamic> order) {
    final message = jsonEncode({
      'type': 'NEW_ORDER',
      'data': order,
      'timestamp': DateTime.now().toIso8601String(),
    });

    for (var ws in _wsClients) {
      try {
        ws.add(message);
      } catch (e) {
        print('[LocalServer] WS broadcast error: $e');
      }
    }
  }

  /// 주문 상태 변경 브로드캐스트
  void broadcastStatusUpdate(String orderId, String status) {
    final message = jsonEncode({
      'type': 'STATUS_UPDATE',
      'data': {'order_id': orderId, 'status': status},
      'timestamp': DateTime.now().toIso8601String(),
    });

    for (var ws in _wsClients) {
      try {
        ws.add(message);
      } catch (e) {
        print('[LocalServer] WS broadcast error: $e');
      }
    }
  }

  // === API Handlers ===

  Future<Response> _handleGetOrders(Request request, String storeId) async {
    try {
      final orders = await onGetOrders?.call() ?? [];
      return Response.ok(
        jsonEncode(orders),
        headers: {'Content-Type': 'application/json'},
      );
    } catch (e) {
      return Response.internalServerError(body: jsonEncode({'error': e.toString()}));
    }
  }

  Future<Response> _handleGetProducts(Request request, String storeId) async {
    try {
      final products = await onGetProducts?.call() ?? [];
      return Response.ok(
        jsonEncode(products),
        headers: {'Content-Type': 'application/json'},
      );
    } catch (e) {
      return Response.internalServerError(body: jsonEncode({'error': e.toString()}));
    }
  }

  Future<Response> _handlePlaceOrder(Request request) async {
    try {
      final body = await request.readAsString();
      final orderData = jsonDecode(body) as Map<String, dynamic>;

      final result = await onPlaceOrder?.call(orderData);
      if (result != null) {
        // 새 주문 브로드캐스트
        broadcastOrder(result);
        return Response.ok(
          jsonEncode(result),
          headers: {'Content-Type': 'application/json'},
        );
      }
      return Response.internalServerError(body: '{"error": "Order handler not set"}');
    } catch (e) {
      return Response.internalServerError(body: jsonEncode({'error': e.toString()}));
    }
  }

  Future<Response> _handleUpdateStatus(Request request, String orderId) async {
    try {
      final body = await request.readAsString();
      final data = jsonDecode(body) as Map<String, dynamic>;
      final status = data['status'] as String;

      final success = await onUpdateOrderStatus?.call(orderId, status) ?? false;
      if (success) {
        broadcastStatusUpdate(orderId, status);
        return Response.ok(
          jsonEncode({'success': true, 'new_state': status}),
          headers: {'Content-Type': 'application/json'},
        );
      }
      return Response.notFound('{"error": "Order not found"}');
    } catch (e) {
      return Response.internalServerError(body: jsonEncode({'error': e.toString()}));
    }
  }

  Response _handleHealth(Request request) {
    return Response.ok(
      jsonEncode({
        'status': 'ok',
        'server': 'TG-POS Local Server',
        'version': '1.0.0',
        'connected_clients': _wsClients.length,
      }),
      headers: {'Content-Type': 'application/json'},
    );
  }

  Map<String, String> get _corsHeaders => {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Origin, Content-Type, Authorization',
  };
}
