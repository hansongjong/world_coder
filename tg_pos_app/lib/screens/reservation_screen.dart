import 'package:flutter/material.dart';
import '../services/api_service.dart';
class ReservationScreen extends StatefulWidget { final int storeId; const ReservationScreen({super.key, required this.storeId}); @override State<ReservationScreen> createState() => _S(); }
class _S extends State<ReservationScreen> {
  List _l = []; @override void initState() { super.initState(); _f(); }
  Future<void> _f() async { try { final d = await ApiService().getReservations(widget.storeId); setState(() => _l = d); } catch(e) {} }
  @override Widget build(BuildContext context) { return Scaffold(appBar: AppBar(title: const Text("Reservations")), body: ListView.builder(itemCount: _l.length, itemBuilder: (ctx, i) => ListTile(title: Text(_l[i]['guest_name']), subtitle: Text(_l[i]['reserved_at'])))); }
}
