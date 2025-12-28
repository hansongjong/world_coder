import 'package:flutter/material.dart';

/// 다국어 지원 클래스 (한국어/영어)
class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  static final Map<String, Map<String, String>> _localizedValues = {
    'ko': {
      // Common
      'app_name': 'TG POS',
      'loading': '로딩 중...',
      'save': '저장',
      'cancel': '취소',
      'confirm': '확인',
      'delete': '삭제',
      'edit': '수정',
      'add': '추가',
      'close': '닫기',
      'search': '검색',
      'refresh': '새로고침',
      'settings': '설정',
      'logout': '로그아웃',
      'back': '뒤로',
      'next': '다음',
      'done': '완료',
      'error': '오류',
      'success': '성공',
      'warning': '경고',

      // Login
      'login': '로그인',
      'username': '아이디',
      'password': '비밀번호',
      'login_title': 'TG POS 로그인',
      'login_button': '로그인',
      'login_failed': '로그인 실패',
      'user_not_found': '사용자를 찾을 수 없습니다',
      'invalid_password': '비밀번호가 올바르지 않습니다',

      // Store Selection
      'select_store': '매장 선택',
      'select_store_subtitle': '접속할 매장을 선택하세요',
      'no_stores': '접근 가능한 매장이 없습니다',
      'owner': '점주',
      'manager': '매니저',
      'staff': '직원',

      // POS
      'menu': '메뉴',
      'cart': '장바구니',
      'order': '주문',
      'payment': '결제',
      'total': '합계',
      'quantity': '수량',
      'price': '가격',
      'add_to_cart': '담기',
      'clear_cart': '비우기',
      'place_order': '주문하기',
      'order_complete': '주문 완료',
      'order_number': '주문번호',
      'won': '원',

      // Payment
      'payment_method': '결제 수단',
      'cash': '현금',
      'card': '카드',
      'received': '받은 금액',
      'change': '거스름돈',
      'pay': '결제',
      'payment_complete': '결제 완료',

      // Tables
      'tables': '테이블',
      'table_map': '테이블 배치도',
      'available': '이용가능',
      'occupied': '사용중',
      'reserved': '예약됨',
      'guests': '손님',
      'open_table': '테이블 열기',
      'close_table': '테이블 닫기',

      // Queue
      'queue': '대기',
      'waiting_list': '대기자 명단',
      'waiting_number': '대기번호',
      'call_next': '다음 호출',
      'no_waiting': '대기자 없음',

      // Inventory
      'inventory': '재고',
      'stock': '재고량',
      'low_stock': '재고 부족',
      'out_of_stock': '품절',
      'update_stock': '재고 수정',

      // Reports
      'reports': '보고서',
      'daily_sales': '일일 매출',
      'sales_summary': '매출 요약',
      'total_orders': '총 주문',
      'total_revenue': '총 매출',
      'best_sellers': '인기 메뉴',

      // Settings
      'store_settings': '매장 설정',
      'business_type': '업종',
      'cafe': '카페',
      'restaurant': '음식점',
      'retail': '소매점',
      'gym': '헬스장',
      'beauty': '미용실',
      'hospital': '병원',
      'modules': '모듈',
      'language': '언어',
      'korean': '한국어',
      'english': 'English',

      // Subscription (Gym)
      'subscription': '회원권',
      'membership': '멤버십',
      'active_members': '활성 회원',
      'expired': '만료됨',
      'days_left': '일 남음',

      // Reservation
      'reservation': '예약',
      'reservations': '예약 목록',
      'new_reservation': '새 예약',
      'reservation_date': '예약 날짜',
      'reservation_time': '예약 시간',
      'party_size': '인원',
      'customer_name': '고객명',
      'customer_phone': '연락처',

      // Product Management
      'product_management': '상품 관리',
      'category': '카테고리',
      'product_name': '상품명',
      'product_price': '가격',
      'soldout': '품절',
      'add_category': '카테고리 추가',
      'add_product': '상품 추가',

      // Order History
      'order_history': '주문 내역',
      'order_date': '주문 일시',
      'order_status': '주문 상태',
      'pending': '대기중',
      'paid': '결제완료',
      'preparing': '준비중',
      'ready': '준비완료',
      'completed': '완료',
      'canceled': '취소됨',

      // Cart
      'empty_cart': '장바구니가 비었습니다',
      'order_list': '주문 목록',

      // Discount
      'discount': '할인',
      'discount_type': '할인 유형',
      'discount_amount': '할인 금액',
      'discount_percent': '할인율',
      'apply_discount': '할인 적용',
      'coupon_code': '쿠폰 코드',
      'original_price': '원래 금액',
      'discounted_price': '할인된 금액',
      'no_discount': '할인 없음',
      'percent': '%',

      // Split Bill
      'split_bill': '분할 결제',
      'split_equally': '균등 분할',
      'split_by_item': '메뉴별 분할',
      'number_of_people': '인원수',
      'per_person': '1인당',
      'remaining': '남은 금액',

      // Refund
      'refund': '환불',
      'refund_reason': '환불 사유',
      'refund_amount': '환불 금액',
      'process_refund': '환불 처리',
      'refund_complete': '환불 완료',
      'customer_request': '고객 요청',
      'wrong_order': '잘못된 주문',
      'product_issue': '상품 문제',
    },
    'en': {
      // Common
      'app_name': 'TG POS',
      'loading': 'Loading...',
      'save': 'Save',
      'cancel': 'Cancel',
      'confirm': 'Confirm',
      'delete': 'Delete',
      'edit': 'Edit',
      'add': 'Add',
      'close': 'Close',
      'search': 'Search',
      'refresh': 'Refresh',
      'settings': 'Settings',
      'logout': 'Logout',
      'back': 'Back',
      'next': 'Next',
      'done': 'Done',
      'error': 'Error',
      'success': 'Success',
      'warning': 'Warning',

      // Login
      'login': 'Login',
      'username': 'Username',
      'password': 'Password',
      'login_title': 'TG POS Login',
      'login_button': 'Login',
      'login_failed': 'Login Failed',
      'user_not_found': 'User not found',
      'invalid_password': 'Invalid password',

      // Store Selection
      'select_store': 'Select Store',
      'select_store_subtitle': 'Choose a store to access',
      'no_stores': 'No accessible stores',
      'owner': 'Owner',
      'manager': 'Manager',
      'staff': 'Staff',

      // POS
      'menu': 'Menu',
      'cart': 'Cart',
      'order': 'Order',
      'payment': 'Payment',
      'total': 'Total',
      'quantity': 'Qty',
      'price': 'Price',
      'add_to_cart': 'Add',
      'clear_cart': 'Clear',
      'place_order': 'Place Order',
      'order_complete': 'Order Complete',
      'order_number': 'Order #',
      'won': 'KRW',

      // Payment
      'payment_method': 'Payment Method',
      'cash': 'Cash',
      'card': 'Card',
      'received': 'Received',
      'change': 'Change',
      'pay': 'Pay',
      'payment_complete': 'Payment Complete',

      // Tables
      'tables': 'Tables',
      'table_map': 'Table Map',
      'available': 'Available',
      'occupied': 'Occupied',
      'reserved': 'Reserved',
      'guests': 'Guests',
      'open_table': 'Open Table',
      'close_table': 'Close Table',

      // Queue
      'queue': 'Queue',
      'waiting_list': 'Waiting List',
      'waiting_number': 'Waiting #',
      'call_next': 'Call Next',
      'no_waiting': 'No one waiting',

      // Inventory
      'inventory': 'Inventory',
      'stock': 'Stock',
      'low_stock': 'Low Stock',
      'out_of_stock': 'Out of Stock',
      'update_stock': 'Update Stock',

      // Reports
      'reports': 'Reports',
      'daily_sales': 'Daily Sales',
      'sales_summary': 'Sales Summary',
      'total_orders': 'Total Orders',
      'total_revenue': 'Total Revenue',
      'best_sellers': 'Best Sellers',

      // Settings
      'store_settings': 'Store Settings',
      'business_type': 'Business Type',
      'cafe': 'Cafe',
      'restaurant': 'Restaurant',
      'retail': 'Retail',
      'gym': 'Gym',
      'beauty': 'Beauty',
      'hospital': 'Hospital',
      'modules': 'Modules',
      'language': 'Language',
      'korean': '한국어',
      'english': 'English',

      // Subscription (Gym)
      'subscription': 'Subscription',
      'membership': 'Membership',
      'active_members': 'Active Members',
      'expired': 'Expired',
      'days_left': 'days left',

      // Reservation
      'reservation': 'Reservation',
      'reservations': 'Reservations',
      'new_reservation': 'New Reservation',
      'reservation_date': 'Date',
      'reservation_time': 'Time',
      'party_size': 'Party Size',
      'customer_name': 'Customer Name',
      'customer_phone': 'Phone',

      // Product Management
      'product_management': 'Product Management',
      'category': 'Category',
      'product_name': 'Product Name',
      'product_price': 'Price',
      'soldout': 'Sold Out',
      'add_category': 'Add Category',
      'add_product': 'Add Product',

      // Order History
      'order_history': 'Order History',
      'order_date': 'Order Date',
      'order_status': 'Status',
      'pending': 'Pending',
      'paid': 'Paid',
      'preparing': 'Preparing',
      'ready': 'Ready',
      'completed': 'Completed',
      'canceled': 'Canceled',

      // Cart
      'empty_cart': 'Cart is empty',
      'order_list': 'Order List',

      // Discount
      'discount': 'Discount',
      'discount_type': 'Discount Type',
      'discount_amount': 'Discount Amount',
      'discount_percent': 'Discount %',
      'apply_discount': 'Apply Discount',
      'coupon_code': 'Coupon Code',
      'original_price': 'Original Price',
      'discounted_price': 'Discounted Price',
      'no_discount': 'No Discount',
      'percent': '%',

      // Split Bill
      'split_bill': 'Split Bill',
      'split_equally': 'Split Equally',
      'split_by_item': 'Split by Item',
      'number_of_people': 'Number of People',
      'per_person': 'Per Person',
      'remaining': 'Remaining',

      // Refund
      'refund': 'Refund',
      'refund_reason': 'Refund Reason',
      'refund_amount': 'Refund Amount',
      'process_refund': 'Process Refund',
      'refund_complete': 'Refund Complete',
      'customer_request': 'Customer Request',
      'wrong_order': 'Wrong Order',
      'product_issue': 'Product Issue',
    },
  };

  String get(String key) {
    return _localizedValues[locale.languageCode]?[key] ?? key;
  }

  // Shortcut getters for common strings
  String get appName => get('app_name');
  String get loading => get('loading');
  String get save => get('save');
  String get cancel => get('cancel');
  String get confirm => get('confirm');
  String get login => get('login');
  String get logout => get('logout');
  String get settings => get('settings');
  String get selectStore => get('select_store');
  String get menu => get('menu');
  String get cart => get('cart');
  String get payment => get('payment');
  String get total => get('total');
  String get won => get('won');
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return ['ko', 'en'].contains(locale.languageCode);
  }

  @override
  Future<AppLocalizations> load(Locale locale) async {
    return AppLocalizations(locale);
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}
