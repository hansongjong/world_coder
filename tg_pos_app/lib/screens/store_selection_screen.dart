import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../providers/store_config_provider.dart';
import 'pos_screen.dart';
import 'login_screen.dart';

/// 매장 선택 화면 (다중 매장 사용자용)
class StoreSelectionScreen extends StatelessWidget {
  final int userId;
  final String username;
  final List<Map<String, dynamic>> stores;

  const StoreSelectionScreen({
    super.key,
    required this.userId,
    required this.username,
    required this.stores,
  });

  String _getRoleLabel(String role) {
    switch (role.toLowerCase()) {
      case 'owner':
        return '점주';
      case 'manager':
        return '매니저';
      case 'staff':
        return '직원';
      default:
        return role;
    }
  }

  Color _getRoleColor(String role) {
    switch (role.toLowerCase()) {
      case 'owner':
        return Colors.purple;
      case 'manager':
        return Colors.blue;
      case 'staff':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  IconData _getBizTypeIcon(String bizType) {
    switch (bizType.toLowerCase()) {
      case 'cafe':
        return Icons.coffee;
      case 'restaurant':
        return Icons.restaurant;
      case 'gym':
        return Icons.fitness_center;
      case 'retail':
        return Icons.store;
      case 'beauty':
        return Icons.face;
      case 'hospital':
        return Icons.local_hospital;
      default:
        return Icons.storefront;
    }
  }

  Future<void> _selectStore(BuildContext context, Map<String, dynamic> store) async {
    final storeId = store['store_id'] as int;

    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator()),
    );

    try {
      final result = await ApiService().selectStore(userId, storeId);
      if (!context.mounted) return;
      Navigator.pop(context); // Close loading

      if (result != null) {
        // Load store config before navigating
        await context.read<StoreConfigProvider>().loadConfig(storeId);

        if (!context.mounted) return;

        // Navigate to POS screen
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => PosScreen(storeId: storeId),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('매장 선택 실패')),
        );
      }
    } catch (e) {
      if (!context.mounted) return;
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('오류: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      body: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 600),
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Logo
              const Icon(
                Icons.point_of_sale,
                size: 64,
                color: Color(0xFF3B82F6),
              ),
              const SizedBox(height: 16),
              const Text(
                'TG POS',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '안녕하세요, $username님',
                style: const TextStyle(
                  fontSize: 18,
                  color: Color(0xFF6B7280),
                ),
              ),
              const SizedBox(height: 32),

              // Title
              const Text(
                '매장 선택',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1F2937),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                '접속할 매장을 선택하세요',
                style: TextStyle(
                  fontSize: 14,
                  color: Color(0xFF6B7280),
                ),
              ),
              const SizedBox(height: 24),

              // Store List
              Flexible(
                child: ListView.builder(
                  shrinkWrap: true,
                  itemCount: stores.length,
                  itemBuilder: (context, index) {
                    final store = stores[index];
                    final bizType = store['biz_type'] ?? 'other';
                    final role = store['role'] ?? 'staff';

                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      elevation: 2,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: InkWell(
                        onTap: () => _selectStore(context, store),
                        borderRadius: BorderRadius.circular(12),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Row(
                            children: [
                              // Icon
                              Container(
                                width: 56,
                                height: 56,
                                decoration: BoxDecoration(
                                  color: const Color(0xFF3B82F6).withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Icon(
                                  _getBizTypeIcon(bizType),
                                  size: 28,
                                  color: const Color(0xFF3B82F6),
                                ),
                              ),
                              const SizedBox(width: 16),

                              // Store Info
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      store['store_name'] ?? 'Unknown Store',
                                      style: const TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                        color: Color(0xFF1F2937),
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Row(
                                      children: [
                                        Container(
                                          padding: const EdgeInsets.symmetric(
                                            horizontal: 8,
                                            vertical: 2,
                                          ),
                                          decoration: BoxDecoration(
                                            color: _getRoleColor(role).withValues(alpha: 0.1),
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                          child: Text(
                                            _getRoleLabel(role),
                                            style: TextStyle(
                                              fontSize: 12,
                                              color: _getRoleColor(role),
                                              fontWeight: FontWeight.w500,
                                            ),
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Text(
                                          bizType.toUpperCase(),
                                          style: const TextStyle(
                                            fontSize: 12,
                                            color: Color(0xFF9CA3AF),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),

                              // Arrow
                              const Icon(
                                Icons.arrow_forward_ios,
                                size: 16,
                                color: Color(0xFF9CA3AF),
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),

              const SizedBox(height: 24),

              // Logout button
              TextButton.icon(
                onPressed: () {
                  ApiService().logout();
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                  );
                },
                icon: const Icon(Icons.logout, size: 18),
                label: const Text('다른 계정으로 로그인'),
                style: TextButton.styleFrom(
                  foregroundColor: const Color(0xFF6B7280),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
