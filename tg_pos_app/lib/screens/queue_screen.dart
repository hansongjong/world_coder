import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class QueueScreen extends StatefulWidget {
  final int storeId;
  const QueueScreen({super.key, required this.storeId});

  @override
  State<QueueScreen> createState() => _QueueScreenState();
}

class _QueueScreenState extends State<QueueScreen> {
  List<Map<String, dynamic>> _waitingList = [];
  bool _isLoading = true;
  int _currentNumber = 0;
  final _timeFormat = DateFormat('HH:mm');

  @override
  void initState() {
    super.initState();
    _loadQueue();
  }

  Future<void> _loadQueue() async {
    setState(() => _isLoading = true);
    try {
      // Mock queue data
      await Future.delayed(const Duration(milliseconds: 500));
      setState(() {
        _currentNumber = 15;
        _waitingList = [
          {
            'queue_no': 12,
            'name': 'Kim',
            'phone': '010-****-1234',
            'party_size': 2,
            'status': 'waiting',
            'created_at': DateTime.now().subtract(const Duration(minutes: 45)),
          },
          {
            'queue_no': 13,
            'name': 'Lee',
            'phone': '010-****-5678',
            'party_size': 4,
            'status': 'waiting',
            'created_at': DateTime.now().subtract(const Duration(minutes: 30)),
          },
          {
            'queue_no': 14,
            'name': 'Park',
            'phone': '010-****-9012',
            'party_size': 3,
            'status': 'waiting',
            'created_at': DateTime.now().subtract(const Duration(minutes: 15)),
          },
          {
            'queue_no': 15,
            'name': 'Choi',
            'phone': '010-****-3456',
            'party_size': 2,
            'status': 'called',
            'created_at': DateTime.now().subtract(const Duration(minutes: 5)),
          },
        ];
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load queue: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _addToQueue() {
    final nameController = TextEditingController();
    final phoneController = TextEditingController();
    int partySize = 2;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Add to Queue'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'Name',
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
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Party Size'),
                  Row(
                    children: [
                      IconButton(
                        onPressed: partySize > 1
                            ? () => setDialogState(() => partySize--)
                            : null,
                        icon: const Icon(Icons.remove_circle_outline),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        child: Text(
                          '$partySize',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      IconButton(
                        onPressed: () => setDialogState(() => partySize++),
                        icon: const Icon(Icons.add_circle_outline),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                if (nameController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Please enter name')),
                  );
                  return;
                }
                Navigator.pop(context);
                _createQueueEntry(
                  nameController.text,
                  phoneController.text,
                  partySize,
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF3B82F6),
                foregroundColor: Colors.white,
              ),
              child: const Text('Add'),
            ),
          ],
        ),
      ),
    );
  }

  void _createQueueEntry(String name, String phone, int partySize) {
    setState(() {
      _currentNumber++;
      _waitingList.add({
        'queue_no': _currentNumber,
        'name': name,
        'phone': phone.isNotEmpty ? '${phone.substring(0, 7)}****' : '-',
        'party_size': partySize,
        'status': 'waiting',
        'created_at': DateTime.now(),
      });
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Added #$_currentNumber - $name')),
    );
  }

  void _callNext() {
    final waiting = _waitingList.where((e) => e['status'] == 'waiting').toList();
    if (waiting.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No one in queue')),
      );
      return;
    }

    setState(() {
      final idx = _waitingList.indexOf(waiting.first);
      _waitingList[idx]['status'] = 'called';
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Calling #${waiting.first['queue_no']} - ${waiting.first['name']}')),
    );
  }

  void _markSeated(Map<String, dynamic> entry) {
    setState(() {
      _waitingList.remove(entry);
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('#${entry['queue_no']} has been seated')),
    );
  }

  void _markNoShow(Map<String, dynamic> entry) {
    setState(() {
      final idx = _waitingList.indexOf(entry);
      _waitingList[idx]['status'] = 'no_show';
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('#${entry['queue_no']} marked as no-show')),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'called':
        return Colors.orange;
      case 'no_show':
        return Colors.red;
      default:
        return Colors.blue;
    }
  }

  String _getWaitTime(DateTime createdAt) {
    final diff = DateTime.now().difference(createdAt);
    if (diff.inHours > 0) {
      return '${diff.inHours}h ${diff.inMinutes % 60}m';
    }
    return '${diff.inMinutes}m';
  }

  @override
  Widget build(BuildContext context) {
    final waiting = _waitingList.where((e) => e['status'] == 'waiting').length;
    final called = _waitingList.where((e) => e['status'] == 'called').length;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Queue Management'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadQueue,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Summary Cards
                Container(
                  padding: const EdgeInsets.all(16),
                  color: const Color(0xFF1E293B),
                  child: Row(
                    children: [
                      Expanded(
                        child: _buildSummaryCard(
                          'Current #',
                          '$_currentNumber',
                          Icons.tag,
                          Colors.blue,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildSummaryCard(
                          'Waiting',
                          '$waiting',
                          Icons.hourglass_empty,
                          Colors.orange,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildSummaryCard(
                          'Called',
                          '$called',
                          Icons.campaign,
                          Colors.green,
                        ),
                      ),
                    ],
                  ),
                ),
                // Queue List
                Expanded(
                  child: _waitingList.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.queue, size: 60, color: Colors.grey[300]),
                              const SizedBox(height: 10),
                              Text(
                                'No one in queue',
                                style: TextStyle(color: Colors.grey[500]),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _waitingList.length,
                          itemBuilder: (context, index) {
                            final entry = _waitingList[index];
                            return _buildQueueCard(entry);
                          },
                        ),
                ),
                // Action Buttons
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.1),
                        blurRadius: 10,
                        offset: const Offset(0, -2),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: _addToQueue,
                          icon: const Icon(Icons.person_add),
                          label: const Text('Add to Queue'),
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 14),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _callNext,
                          icon: const Icon(Icons.campaign),
                          label: const Text('Call Next'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF3B82F6),
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
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
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQueueCard(Map<String, dynamic> entry) {
    final status = entry['status'] as String;
    final isCalled = status == 'called';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: isCalled ? Colors.orange : Colors.transparent,
          width: 2,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            // Queue Number
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: _getStatusColor(status).withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Text(
                  '#${entry['queue_no']}',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: _getStatusColor(status),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 16),
            // Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        entry['name'],
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: _getStatusColor(status).withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(
                          status.toUpperCase(),
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: _getStatusColor(status),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${entry['party_size']} guests • ${entry['phone']}',
                    style: TextStyle(color: Colors.grey[600], fontSize: 13),
                  ),
                  Text(
                    'Wait: ${_getWaitTime(entry['created_at'])} (${_timeFormat.format(entry['created_at'])})',
                    style: TextStyle(color: Colors.grey[500], fontSize: 12),
                  ),
                ],
              ),
            ),
            // Actions
            if (status == 'called') ...[
              IconButton(
                onPressed: () => _markSeated(entry),
                icon: const Icon(Icons.check_circle, color: Colors.green),
                tooltip: 'Seated',
              ),
              IconButton(
                onPressed: () => _markNoShow(entry),
                icon: const Icon(Icons.cancel, color: Colors.red),
                tooltip: 'No Show',
              ),
            ],
          ],
        ),
      ),
    );
  }
}
