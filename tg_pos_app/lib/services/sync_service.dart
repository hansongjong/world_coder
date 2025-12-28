import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

/// 오프라인 → 온라인 동기화 서비스
/// GENESIS_PLANNER 정책: lastSyncAt 기반 증분 동기화
class SyncService {
  final String cloudApiBase;
  final String? Function() getToken;

  // 오프라인 큐
  final List<SyncQueueItem> _pendingQueue = [];

  // 동기화 상태
  DateTime? _lastSyncAt;
  bool _isSyncing = false;

  // 콜백
  Function(String message)? onSyncLog;
  Function(bool isOnline)? onConnectivityChange;

  SyncService({
    required this.cloudApiBase,
    required this.getToken,
  });

  /// 초기화 - 마지막 동기화 시간 로드
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    final lastSyncStr = prefs.getString('lastSyncAt');
    if (lastSyncStr != null) {
      _lastSyncAt = DateTime.parse(lastSyncStr);
    }
    _log('SyncService initialized. Last sync: $_lastSyncAt');
  }

  /// 오프라인 큐에 추가
  void queueForSync(SyncQueueItem item) {
    _pendingQueue.add(item);
    _log('Queued: ${item.type} - ${item.id}');
  }

  /// 동기화 실행
  Future<SyncResult> sync() async {
    if (_isSyncing) {
      return SyncResult(success: false, message: 'Sync already in progress');
    }

    _isSyncing = true;
    int synced = 0;
    int failed = 0;
    final errors = <String>[];

    try {
      // 1. 온라인 체크
      final isOnline = await _checkConnectivity();
      if (!isOnline) {
        return SyncResult(
          success: false,
          message: 'Offline - sync pending',
          pendingCount: _pendingQueue.length,
        );
      }

      onConnectivityChange?.call(true);
      _log('Starting sync. Pending items: ${_pendingQueue.length}');

      // 2. 대기 큐 처리
      final itemsToSync = List<SyncQueueItem>.from(_pendingQueue);

      for (var item in itemsToSync) {
        try {
          final success = await _syncItem(item);
          if (success) {
            _pendingQueue.remove(item);
            synced++;
          } else {
            failed++;
            errors.add('${item.type}:${item.id} failed');
          }
        } catch (e) {
          failed++;
          errors.add('${item.type}:${item.id} error: $e');
        }
      }

      // 3. 마지막 동기화 시간 저장
      _lastSyncAt = DateTime.now();
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('lastSyncAt', _lastSyncAt!.toIso8601String());

      _log('Sync complete. Synced: $synced, Failed: $failed');

      return SyncResult(
        success: failed == 0,
        message: 'Synced: $synced, Failed: $failed',
        syncedCount: synced,
        failedCount: failed,
        errors: errors,
      );
    } catch (e) {
      _log('Sync error: $e');
      return SyncResult(success: false, message: 'Sync error: $e');
    } finally {
      _isSyncing = false;
    }
  }

  /// 단일 항목 동기화
  Future<bool> _syncItem(SyncQueueItem item) async {
    final token = getToken();
    final headers = {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };

    try {
      late http.Response response;

      switch (item.type) {
        case SyncType.order:
          response = await http.post(
            Uri.parse('$cloudApiBase/sync/order'),
            headers: headers,
            body: jsonEncode(item.data),
          );
          break;

        case SyncType.payment:
          response = await http.post(
            Uri.parse('$cloudApiBase/sync/payment'),
            headers: headers,
            body: jsonEncode(item.data),
          );
          break;

        case SyncType.inventory:
          response = await http.post(
            Uri.parse('$cloudApiBase/sync/inventory'),
            headers: headers,
            body: jsonEncode(item.data),
          );
          break;
      }

      return response.statusCode >= 200 && response.statusCode < 300;
    } catch (e) {
      _log('Sync item error: $e');
      return false;
    }
  }

  /// 연결 상태 확인
  Future<bool> _checkConnectivity() async {
    try {
      final response = await http
          .get(Uri.parse('$cloudApiBase/health'))
          .timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      onConnectivityChange?.call(false);
      return false;
    }
  }

  /// 대기 중인 항목 수
  int get pendingCount => _pendingQueue.length;

  /// 마지막 동기화 시간
  DateTime? get lastSyncAt => _lastSyncAt;

  /// 동기화 중 여부
  bool get isSyncing => _isSyncing;

  void _log(String message) {
    print('[SyncService] $message');
    onSyncLog?.call(message);
  }
}

/// 동기화 큐 항목
class SyncQueueItem {
  final SyncType type;
  final String id;
  final Map<String, dynamic> data;
  final DateTime createdAt;

  SyncQueueItem({
    required this.type,
    required this.id,
    required this.data,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();
}

/// 동기화 유형
enum SyncType {
  order,
  payment,
  inventory,
}

/// 동기화 결과
class SyncResult {
  final bool success;
  final String message;
  final int syncedCount;
  final int failedCount;
  final int pendingCount;
  final List<String> errors;

  SyncResult({
    required this.success,
    required this.message,
    this.syncedCount = 0,
    this.failedCount = 0,
    this.pendingCount = 0,
    this.errors = const [],
  });
}
