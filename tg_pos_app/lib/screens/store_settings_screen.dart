import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/store_config_provider.dart';
import '../services/api_service.dart';

class StoreSettingsScreen extends StatefulWidget {
  final int storeId;
  const StoreSettingsScreen({super.key, required this.storeId});

  @override
  State<StoreSettingsScreen> createState() => _StoreSettingsScreenState();
}

class _StoreSettingsScreenState extends State<StoreSettingsScreen> {
  bool _isLoading = true;

  // Module switches
  bool _modPayment = true;
  bool _modQueue = false;
  bool _modReservation = false;
  bool _modInventory = false;
  bool _modCrm = false;
  bool _modDelivery = false;
  bool _modIot = false;
  bool _modSubscription = false;
  bool _modInvoice = false;

  // Store info
  String _storeName = '';
  String _bizType = 'cafe';
  String _uiMode = 'KIOSK_LITE';

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    setState(() => _isLoading = true);
    try {
      final config = await ApiService().getStoreConfig(widget.storeId);
      if (config != null && mounted) {
        setState(() {
          _storeName = config['store_name'] ?? '';
          _bizType = config['biz_type'] ?? 'cafe';
          _uiMode = config['ui_mode'] ?? 'KIOSK_LITE';
          _modPayment = config['mod_payment'] ?? true;
          _modQueue = config['mod_queue'] ?? false;
          _modReservation = config['mod_reservation'] ?? false;
          _modInventory = config['mod_inventory'] ?? false;
          _modCrm = config['mod_crm'] ?? false;
          _modDelivery = config['mod_delivery'] ?? false;
          _modIot = config['mod_iot'] ?? false;
          _modSubscription = config['mod_subscription'] ?? false;
          _modInvoice = config['mod_invoice'] ?? false;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load settings: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _saveSettings() async {
    setState(() => _isLoading = true);
    try {
      final result = await ApiService().updateStoreConfig(widget.storeId, {
        'biz_type': _bizType,
        'ui_mode': _uiMode,
        'mod_payment': _modPayment,
        'mod_queue': _modQueue,
        'mod_reservation': _modReservation,
        'mod_inventory': _modInventory,
        'mod_crm': _modCrm,
        'mod_delivery': _modDelivery,
        'mod_iot': _modIot,
        'mod_subscription': _modSubscription,
        'mod_invoice': _modInvoice,
      });

      if (result != null && mounted) {
        await context.read<StoreConfigProvider>().loadConfig(widget.storeId);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Settings saved successfully!')),
        );
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to save settings')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _applyTemplate(String template) {
    setState(() {
      switch (template) {
        case 'cafe':
          _bizType = 'cafe';
          _uiMode = 'KIOSK_LITE';
          _modPayment = true;
          _modQueue = true;
          _modReservation = false;
          _modInventory = false;
          _modCrm = false;
          _modDelivery = true;
          _modIot = false;
          _modSubscription = false;
          _modInvoice = false;
          break;
        case 'restaurant':
          _bizType = 'restaurant';
          _uiMode = 'TABLE_MANAGER';
          _modPayment = true;
          _modQueue = true;
          _modReservation = true;
          _modInventory = true;
          _modCrm = true;
          _modDelivery = true;
          _modIot = false;
          _modSubscription = false;
          _modInvoice = false;
          break;
        case 'retail':
          _bizType = 'retail';
          _uiMode = 'KIOSK_LITE';
          _modPayment = true;
          _modQueue = false;
          _modReservation = false;
          _modInventory = true;
          _modCrm = true;
          _modDelivery = true;
          _modIot = false;
          _modSubscription = false;
          _modInvoice = true;
          break;
        case 'gym':
          _bizType = 'gym';
          _uiMode = 'ADMIN_DASHBOARD';
          _modPayment = true;
          _modQueue = false;
          _modReservation = true;
          _modInventory = false;
          _modCrm = true;
          _modDelivery = false;
          _modIot = true;
          _modSubscription = true;
          _modInvoice = false;
          break;
        case 'hospital':
          _bizType = 'hospital';
          _uiMode = 'ADMIN_DASHBOARD';
          _modPayment = true;
          _modQueue = true;
          _modReservation = true;
          _modInventory = true;
          _modCrm = true;
          _modDelivery = false;
          _modIot = false;
          _modSubscription = false;
          _modInvoice = true;
          break;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Store Settings'),
        actions: [
          TextButton.icon(
            onPressed: _saveSettings,
            icon: const Icon(Icons.save, color: Colors.white),
            label: const Text('Save', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Quick Templates
                  _buildSection(
                    'Quick Templates',
                    'Choose a template to quickly configure your store',
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _buildTemplateChip('cafe', 'Cafe', Icons.coffee),
                        _buildTemplateChip('restaurant', 'Restaurant', Icons.restaurant),
                        _buildTemplateChip('retail', 'Retail', Icons.store),
                        _buildTemplateChip('gym', 'Gym', Icons.fitness_center),
                        _buildTemplateChip('hospital', 'Hospital', Icons.local_hospital),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Store Info
                  _buildSection(
                    'Store Information',
                    'Basic store details',
                    child: Column(
                      children: [
                        TextField(
                          controller: TextEditingController(text: _storeName),
                          decoration: const InputDecoration(
                            labelText: 'Store Name',
                            border: OutlineInputBorder(),
                          ),
                          onChanged: (v) => _storeName = v,
                        ),
                        const SizedBox(height: 16),
                        DropdownButtonFormField<String>(
                          value: _bizType,
                          decoration: const InputDecoration(
                            labelText: 'Business Type',
                            border: OutlineInputBorder(),
                          ),
                          items: const [
                            DropdownMenuItem(value: 'cafe', child: Text('Cafe')),
                            DropdownMenuItem(value: 'restaurant', child: Text('Restaurant')),
                            DropdownMenuItem(value: 'retail', child: Text('Retail')),
                            DropdownMenuItem(value: 'beauty', child: Text('Beauty Salon')),
                            DropdownMenuItem(value: 'gym', child: Text('Gym/Fitness')),
                            DropdownMenuItem(value: 'hospital', child: Text('Hospital/Clinic')),
                            DropdownMenuItem(value: 'other', child: Text('Other')),
                          ],
                          onChanged: (v) => setState(() => _bizType = v!),
                        ),
                        const SizedBox(height: 16),
                        DropdownButtonFormField<String>(
                          value: _uiMode,
                          decoration: const InputDecoration(
                            labelText: 'UI Mode',
                            border: OutlineInputBorder(),
                          ),
                          items: const [
                            DropdownMenuItem(value: 'KIOSK_LITE', child: Text('Kiosk (Simple)')),
                            DropdownMenuItem(value: 'TABLE_MANAGER', child: Text('Table Manager')),
                            DropdownMenuItem(value: 'ADMIN_DASHBOARD', child: Text('Admin Dashboard')),
                            DropdownMenuItem(value: 'ERP_LITE', child: Text('ERP Lite')),
                          ],
                          onChanged: (v) => setState(() => _uiMode = v!),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Modules
                  _buildSection(
                    'Feature Modules',
                    'Enable or disable features for your store',
                    child: Column(
                      children: [
                        _buildModuleSwitch(
                          'Payment Processing',
                          'Accept payments via card, cash, etc.',
                          Icons.payment,
                          _modPayment,
                          (v) => setState(() => _modPayment = v),
                        ),
                        _buildModuleSwitch(
                          'Queue Management',
                          'Waiting list and number system',
                          Icons.queue,
                          _modQueue,
                          (v) => setState(() => _modQueue = v),
                        ),
                        _buildModuleSwitch(
                          'Reservations',
                          'Table/appointment booking',
                          Icons.calendar_today,
                          _modReservation,
                          (v) => setState(() => _modReservation = v),
                        ),
                        _buildModuleSwitch(
                          'Inventory',
                          'Stock management',
                          Icons.inventory_2,
                          _modInventory,
                          (v) => setState(() => _modInventory = v),
                        ),
                        _buildModuleSwitch(
                          'CRM',
                          'Customer relationship management',
                          Icons.people,
                          _modCrm,
                          (v) => setState(() => _modCrm = v),
                        ),
                        _buildModuleSwitch(
                          'Delivery',
                          'Delivery order management',
                          Icons.delivery_dining,
                          _modDelivery,
                          (v) => setState(() => _modDelivery = v),
                        ),
                        _buildModuleSwitch(
                          'IoT Integration',
                          'Smart device control',
                          Icons.devices,
                          _modIot,
                          (v) => setState(() => _modIot = v),
                        ),
                        _buildModuleSwitch(
                          'Subscriptions',
                          'Recurring membership/plans',
                          Icons.card_membership,
                          _modSubscription,
                          (v) => setState(() => _modSubscription = v),
                        ),
                        _buildModuleSwitch(
                          'Invoicing',
                          'B2B invoices and wholesale',
                          Icons.receipt_long,
                          _modInvoice,
                          (v) => setState(() => _modInvoice = v),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildSection(String title, String subtitle, {required Widget child}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          subtitle,
          style: TextStyle(
            fontSize: 13,
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 16),
        child,
      ],
    );
  }

  Widget _buildTemplateChip(String value, String label, IconData icon) {
    final isSelected = _bizType == value;
    return FilterChip(
      selected: isSelected,
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 18, color: isSelected ? Colors.white : Colors.grey[700]),
          const SizedBox(width: 6),
          Text(label),
        ],
      ),
      selectedColor: const Color(0xFF3B82F6),
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : Colors.black87,
      ),
      onSelected: (_) => _applyTemplate(value),
    );
  }

  Widget _buildModuleSwitch(
    String title,
    String subtitle,
    IconData icon,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: SwitchListTile(
        secondary: Icon(icon, color: value ? const Color(0xFF3B82F6) : Colors.grey),
        title: Text(title),
        subtitle: Text(subtitle, style: const TextStyle(fontSize: 12)),
        value: value,
        onChanged: onChanged,
        activeColor: const Color(0xFF3B82F6),
      ),
    );
  }
}
