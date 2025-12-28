import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class StoreConfigProvider extends ChangeNotifier {
  Map<String, dynamic>? _config;
  bool _isLoading = false;
  String? _error;

  // Getters
  Map<String, dynamic>? get config => _config;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Store Info
  int get storeId => _config?['store_id'] ?? 0;
  String get storeName => _config?['store_name'] ?? '';
  String get bizType => _config?['biz_type'] ?? 'cafe';
  String get uiMode => _config?['ui_mode'] ?? 'KIOSK_LITE';

  // Module flags
  bool get hasPayment => _config?['mod_payment'] ?? true;
  bool get hasQueue => _config?['mod_queue'] ?? false;
  bool get hasReservation => _config?['mod_reservation'] ?? false;
  bool get hasInventory => _config?['mod_inventory'] ?? false;
  bool get hasCrm => _config?['mod_crm'] ?? false;
  bool get hasDelivery => _config?['mod_delivery'] ?? false;
  bool get hasIot => _config?['mod_iot'] ?? false;
  bool get hasSubscription => _config?['mod_subscription'] ?? false;
  bool get hasInvoice => _config?['mod_invoice'] ?? false;

  // UI Settings
  int get tableCount => _config?['table_count'] ?? 0;
  int get depositAmount => _config?['deposit_amount'] ?? 0;

  // Business type checks
  bool get isCafe => bizType == 'cafe';
  bool get isRestaurant => bizType == 'restaurant';
  bool get isRetail => bizType == 'retail';
  bool get isBeauty => bizType == 'beauty';
  bool get isGym => bizType == 'gym';
  bool get isHospital => bizType == 'hospital';

  // UI Mode checks
  bool get isKioskMode => uiMode == 'KIOSK_LITE';
  bool get isTableManagerMode => uiMode == 'TABLE_MANAGER';
  bool get isAdminDashboardMode => uiMode == 'ADMIN_DASHBOARD';
  bool get isErpMode => uiMode == 'ERP_LITE';

  Future<void> loadConfig(int storeId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await ApiService().getStoreConfig(storeId);
      if (result != null) {
        _config = result;
        _error = null;
      } else {
        _error = 'Failed to load store config';
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void clear() {
    _config = null;
    _error = null;
    notifyListeners();
  }

  // Get icon for business type
  String getBizTypeLabel() {
    switch (bizType) {
      case 'cafe':
        return 'Cafe';
      case 'restaurant':
        return 'Restaurant';
      case 'retail':
        return 'Retail';
      case 'beauty':
        return 'Beauty Salon';
      case 'gym':
        return 'Gym';
      case 'hospital':
        return 'Hospital';
      default:
        return 'Store';
    }
  }
}
