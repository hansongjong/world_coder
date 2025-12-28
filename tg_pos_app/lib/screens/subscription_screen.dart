import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class SubscriptionScreen extends StatefulWidget {
  final int storeId;
  const SubscriptionScreen({super.key, required this.storeId});

  @override
  State<SubscriptionScreen> createState() => _SubscriptionScreenState();
}

class _SubscriptionScreenState extends State<SubscriptionScreen> {
  List<Map<String, dynamic>> _subscriptions = [];
  List<Map<String, dynamic>> _plans = [];
  bool _isLoading = true;
  final _currencyFormat = NumberFormat("#,###", "ko_KR");
  final _dateFormat = DateFormat('yyyy-MM-dd');

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      await Future.delayed(const Duration(milliseconds: 500));
      setState(() {
        _plans = [
          {'id': 1, 'name': 'Basic Monthly', 'price': 50000, 'duration_days': 30, 'description': 'Basic gym access'},
          {'id': 2, 'name': 'Premium Monthly', 'price': 80000, 'duration_days': 30, 'description': 'Gym + PT sessions'},
          {'id': 3, 'name': 'Annual Basic', 'price': 500000, 'duration_days': 365, 'description': '12 months basic access'},
          {'id': 4, 'name': 'Annual Premium', 'price': 800000, 'duration_days': 365, 'description': '12 months premium'},
        ];
        _subscriptions = [
          {
            'id': 1,
            'member_name': 'Kim Minsoo',
            'phone': '010-1234-5678',
            'plan_name': 'Premium Monthly',
            'start_date': DateTime.now().subtract(const Duration(days: 15)),
            'end_date': DateTime.now().add(const Duration(days: 15)),
            'status': 'active',
            'auto_renew': true,
          },
          {
            'id': 2,
            'member_name': 'Lee Jiyoung',
            'phone': '010-2345-6789',
            'plan_name': 'Basic Monthly',
            'start_date': DateTime.now().subtract(const Duration(days: 25)),
            'end_date': DateTime.now().add(const Duration(days: 5)),
            'status': 'expiring',
            'auto_renew': false,
          },
          {
            'id': 3,
            'member_name': 'Park Jinho',
            'phone': '010-3456-7890',
            'plan_name': 'Annual Basic',
            'start_date': DateTime.now().subtract(const Duration(days: 100)),
            'end_date': DateTime.now().add(const Duration(days: 265)),
            'status': 'active',
            'auto_renew': true,
          },
          {
            'id': 4,
            'member_name': 'Choi Soyeon',
            'phone': '010-4567-8901',
            'plan_name': 'Premium Monthly',
            'start_date': DateTime.now().subtract(const Duration(days: 35)),
            'end_date': DateTime.now().subtract(const Duration(days: 5)),
            'status': 'expired',
            'auto_renew': false,
          },
        ];
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load subscriptions: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'active':
        return Colors.green;
      case 'expiring':
        return Colors.orange;
      case 'expired':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  int _getDaysRemaining(DateTime endDate) {
    final diff = endDate.difference(DateTime.now()).inDays;
    return diff < 0 ? 0 : diff;
  }

  void _showNewSubscriptionDialog() {
    final nameController = TextEditingController();
    final phoneController = TextEditingController();
    int? selectedPlanId;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('New Subscription'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'Member Name',
                    prefixIcon: Icon(Icons.person),
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: phoneController,
                  decoration: const InputDecoration(
                    labelText: 'Phone',
                    prefixIcon: Icon(Icons.phone),
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.phone,
                ),
                const SizedBox(height: 16),
                const Align(
                  alignment: Alignment.centerLeft,
                  child: Text('Select Plan:', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
                const SizedBox(height: 8),
                ...List.generate(_plans.length, (index) {
                  final plan = _plans[index];
                  final isSelected = selectedPlanId == plan['id'];
                  return Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    color: isSelected ? const Color(0xFF3B82F6).withValues(alpha: 0.1) : null,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                      side: BorderSide(
                        color: isSelected ? const Color(0xFF3B82F6) : Colors.grey.shade300,
                        width: isSelected ? 2 : 1,
                      ),
                    ),
                    child: InkWell(
                      onTap: () => setDialogState(() => selectedPlanId = plan['id']),
                      borderRadius: BorderRadius.circular(8),
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(plan['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
                                  Text(plan['description'], style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                                ],
                              ),
                            ),
                            Text(
                              '${_currencyFormat.format(plan['price'])}원',
                              style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF3B82F6)),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                }),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                if (nameController.text.isEmpty || phoneController.text.isEmpty || selectedPlanId == null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Please fill all fields')),
                  );
                  return;
                }
                Navigator.pop(context);
                _createSubscription(nameController.text, phoneController.text, selectedPlanId!);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF3B82F6),
                foregroundColor: Colors.white,
              ),
              child: const Text('Create'),
            ),
          ],
        ),
      ),
    );
  }

  void _createSubscription(String name, String phone, int planId) {
    final plan = _plans.firstWhere((p) => p['id'] == planId);
    final now = DateTime.now();
    setState(() {
      _subscriptions.insert(0, {
        'id': _subscriptions.length + 1,
        'member_name': name,
        'phone': phone,
        'plan_name': plan['name'],
        'start_date': now,
        'end_date': now.add(Duration(days: plan['duration_days'])),
        'status': 'active',
        'auto_renew': false,
      });
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Subscription created for $name')),
    );
  }

  void _renewSubscription(Map<String, dynamic> sub) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Renew Subscription'),
        content: Text('Renew ${sub['member_name']}\'s subscription for another period?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                final idx = _subscriptions.indexOf(sub);
                final plan = _plans.firstWhere((p) => p['name'] == sub['plan_name'], orElse: () => _plans[0]);
                _subscriptions[idx] = {
                  ...sub,
                  'start_date': DateTime.now(),
                  'end_date': DateTime.now().add(Duration(days: plan['duration_days'])),
                  'status': 'active',
                };
              });
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('${sub['member_name']}\'s subscription renewed')),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF3B82F6),
              foregroundColor: Colors.white,
            ),
            child: const Text('Renew'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final activeCount = _subscriptions.where((s) => s['status'] == 'active').length;
    final expiringCount = _subscriptions.where((s) => s['status'] == 'expiring').length;
    final expiredCount = _subscriptions.where((s) => s['status'] == 'expired').length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Subscriptions'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Summary
                Container(
                  padding: const EdgeInsets.all(16),
                  color: const Color(0xFF1E293B),
                  child: Row(
                    children: [
                      Expanded(
                        child: _buildSummaryCard(
                          'Active',
                          '$activeCount',
                          Icons.check_circle,
                          Colors.green,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildSummaryCard(
                          'Expiring Soon',
                          '$expiringCount',
                          Icons.warning,
                          Colors.orange,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildSummaryCard(
                          'Expired',
                          '$expiredCount',
                          Icons.cancel,
                          Colors.red,
                        ),
                      ),
                    ],
                  ),
                ),
                // Subscription List
                Expanded(
                  child: _subscriptions.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.card_membership, size: 60, color: Colors.grey[300]),
                              const SizedBox(height: 10),
                              Text(
                                'No subscriptions',
                                style: TextStyle(color: Colors.grey[500]),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _subscriptions.length,
                          itemBuilder: (context, index) {
                            final sub = _subscriptions[index];
                            return _buildSubscriptionCard(sub);
                          },
                        ),
                ),
              ],
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showNewSubscriptionDialog,
        backgroundColor: const Color(0xFF3B82F6),
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text('New Subscription', style: TextStyle(color: Colors.white)),
      ),
    );
  }

  Widget _buildSummaryCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildSubscriptionCard(Map<String, dynamic> sub) {
    final status = sub['status'] as String;
    final statusColor = _getStatusColor(status);
    final daysRemaining = _getDaysRemaining(sub['end_date']);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: status == 'expiring' ? Colors.orange : Colors.transparent,
          width: status == 'expiring' ? 2 : 0,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Member Avatar
                CircleAvatar(
                  backgroundColor: statusColor.withValues(alpha: 0.1),
                  child: Icon(Icons.person, color: statusColor),
                ),
                const SizedBox(width: 12),
                // Member Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            sub['member_name'],
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: statusColor.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Text(
                              status.toUpperCase(),
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: statusColor,
                              ),
                            ),
                          ),
                        ],
                      ),
                      Text(
                        sub['phone'],
                        style: TextStyle(color: Colors.grey[600], fontSize: 13),
                      ),
                    ],
                  ),
                ),
                // Renew Button
                if (status == 'expiring' || status == 'expired')
                  ElevatedButton(
                    onPressed: () => _renewSubscription(sub),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF3B82F6),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                    ),
                    child: const Text('Renew'),
                  ),
              ],
            ),
            const Divider(height: 24),
            // Plan Info
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        sub['plan_name'],
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${_dateFormat.format(sub['start_date'])} ~ ${_dateFormat.format(sub['end_date'])}',
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      status == 'expired' ? 'Expired' : '$daysRemaining days left',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: statusColor,
                      ),
                    ),
                    if (sub['auto_renew'] == true)
                      Row(
                        children: [
                          Icon(Icons.autorenew, size: 14, color: Colors.grey[600]),
                          const SizedBox(width: 4),
                          Text(
                            'Auto-renew',
                            style: TextStyle(fontSize: 11, color: Colors.grey[600]),
                          ),
                        ],
                      ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
