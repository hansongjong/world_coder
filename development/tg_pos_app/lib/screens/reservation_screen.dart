import 'package:flutter/material.dart';
import '../services/api_service_v2.dart';
import 'package:intl/intl.dart';

class ReservationScreen extends StatefulWidget {
  final int storeId;
  const ReservationScreen({super.key, required this.storeId});

  @override
  State<ReservationScreen> createState() => _ReservationScreenState();
}

class _ReservationScreenState extends State<ReservationScreen> {
  final ApiServiceV2 _api = ApiServiceV2();
  List<dynamic> _reservations = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final list = await _api.getReservations(widget.storeId);
      setState(() {
        _reservations = list;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      // 에러 처리 생략
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("예약 현황 (Booking)")),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: _reservations.length,
              itemBuilder: (ctx, i) {
                final res = _reservations[i];
                // 날짜 포맷팅
                final dateStr = res['reserved_at'] ?? "";
                final dt = DateTime.tryParse(dateStr);
                final formattedDate = dt != null ? DateFormat('MM/dd HH:mm').format(dt) : dateStr;

                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  child: ListTile(
                    leading: const Icon(Icons.calendar_today, color: Colors.blue),
                    title: Text("${res['guest_name']} (${res['guest_count']}명)"),
                    subtitle: Text(formattedDate),
                    trailing: Chip(
                      label: Text(res['status']),
                      backgroundColor: res['status'] == 'CONFIRMED' ? Colors.green[100] : Colors.grey[200],
                    ),
                  ),
                );
              },
            ),
    );
  }
}