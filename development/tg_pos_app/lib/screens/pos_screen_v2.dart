// 기존 pos_screen.dart 내용을 기반으로 수정된 V2 버전입니다.
// 실제 적용 시 기존 파일을 덮어쓰거나 내용을 병합해야 합니다.

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../providers/cart_provider.dart';
import '../widgets/membership_dialog.dart'; // 추가
import 'reservation_screen.dart'; // 추가

class PosScreenV2 extends StatefulWidget {
  final int storeId;
  const PosScreenV2({super.key, required this.storeId});

  @override
  State<PosScreenV2> createState() => _PosScreenV2State();
}

class _PosScreenV2State extends State<PosScreenV2> {
  final ApiService _api = ApiService();
  // ... (기존 변수 및 _loadMenu 유지)

  // ... (기존 _processOrder 수정)
  Future<void> _processPaymentFlow() async {
    final cart = context.read<CartProvider>();
    if (cart.items.isEmpty) return;
    
    // 1. 멤버십 적립 팝업 띄우기
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => MembershipDialog(
        storeId: widget.storeId,
        paymentAmount: cart.totalAmount,
        onCompleted: () => _finalizeOrder(), // 적립 후 또는 건너뛰기 시 호출
      )
    );
  }

  Future<void> _finalizeOrder() async {
    // 2. 실제 주문 전송 (기존 로직)
    // ... (Api call to placeOrder)
    // ... (Success Dialog)
    // 여기서는 코드 중복을 피하기 위해 생략, 기존 _processOrder 로직 사용
    
    // 데모용 단순 알림
    final cart = context.read<CartProvider>();
    cart.clearCart();
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("주문 및 결제 완료!")));
  }

  @override
  Widget build(BuildContext context) {
    final currency = NumberFormat("#,###", "ko_KR");

    return Scaffold(
      appBar: AppBar(title: const Text("TG-POS Pro"), backgroundColor: Colors.indigo),
      drawer: Drawer( // 사이드 메뉴 추가
        child: ListView(
          children: [
            const DrawerHeader(child: Text("TG-POS Menu", style: TextStyle(fontSize: 24))),
            ListTile(
              leading: const Icon(Icons.point_of_sale),
              title: const Text("주문 (POS)"),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.event_note),
              title: const Text("예약 확인 (Booking)"),
              onTap: () {
                Navigator.pop(context); // 닫기
                Navigator.push(context, MaterialPageRoute(builder: (_) => ReservationScreen(storeId: widget.storeId)));
              },
            ),
            ListTile(
              leading: const Icon(Icons.inventory),
              title: const Text("재고 관리 (Stock)"),
              onTap: () {
                // 재고 화면으로 이동 (추후 구현)
              },
            ),
          ],
        ),
      ),
      body: Row(
        // ... (기존 UI 로직 유지)
        // 결제 버튼 onPressed를 _processPaymentFlow로 변경
        children: [
            // Left Panel (Menu Grid) ...
            // Right Panel (Cart)
            Expanded(
              flex: 1,
              child: Column(
                children: [
                  // ... Cart List
                  // Pay Button
                  SizedBox(
                    width: double.infinity, 
                    height: 60,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.indigo),
                      onPressed: () => _processPaymentFlow(), // 변경됨
                      child: const Text("결제 (PAY)", style: TextStyle(fontSize: 20, color: Colors.white)),
                    ),
                  )
                ]
              )
            )
        ]
      ),
    );
  }
}