import 'package:flutter/material.dart';
import '../services/api_service.dart';

/// Table shape types
enum TableShape { rect2, rect4, rect6, round4, round6, bar }

/// Single table data model
class TableData {
  String id;
  String name;
  TableShape shape;
  double x;
  double y;
  int capacity;

  TableData({
    required this.id,
    required this.name,
    required this.shape,
    required this.x,
    required this.y,
    required this.capacity,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'shape': shape.name,
    'x': x,
    'y': y,
    'capacity': capacity,
  };

  factory TableData.fromJson(Map<String, dynamic> json) => TableData(
    id: json['id'],
    name: json['name'],
    shape: TableShape.values.firstWhere(
      (e) => e.name == json['shape'],
      orElse: () => TableShape.rect4,
    ),
    x: (json['x'] as num).toDouble(),
    y: (json['y'] as num).toDouble(),
    capacity: json['capacity'] ?? 4,
  );

  Size get size {
    switch (shape) {
      case TableShape.rect2:
        return const Size(60, 40);
      case TableShape.rect4:
        return const Size(80, 60);
      case TableShape.rect6:
        return const Size(120, 60);
      case TableShape.round4:
        return const Size(70, 70);
      case TableShape.round6:
        return const Size(90, 90);
      case TableShape.bar:
        return const Size(40, 80);
    }
  }
}

class TableLayoutEditor extends StatefulWidget {
  final int storeId;
  const TableLayoutEditor({super.key, required this.storeId});

  @override
  State<TableLayoutEditor> createState() => _TableLayoutEditorState();
}

class _TableLayoutEditorState extends State<TableLayoutEditor> {
  List<TableData> _tables = [];
  String? _selectedTableId;
  bool _isLoading = true;
  bool _isDirty = false;
  int _nextTableNumber = 1;

  @override
  void initState() {
    super.initState();
    _loadLayout();
  }

  Future<void> _loadLayout() async {
    setState(() => _isLoading = true);
    try {
      final config = await ApiService().getStoreConfig(widget.storeId);
      if (config != null && config['extra_settings'] != null) {
        final extra = config['extra_settings'];
        if (extra is Map && extra['table_layout'] != null) {
          final layoutList = extra['table_layout'] as List;
          setState(() {
            _tables = layoutList.map((t) => TableData.fromJson(t)).toList();
            _nextTableNumber = _tables.length + 1;
          });
        }
      }

      // If no layout, create default
      if (_tables.isEmpty) {
        _createDefaultLayout();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load layout: $e')),
        );
      }
      _createDefaultLayout();
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _createDefaultLayout() {
    setState(() {
      _tables = [];
      for (int i = 0; i < 8; i++) {
        final row = i ~/ 4;
        final col = i % 4;
        _tables.add(TableData(
          id: 'T${(i + 1).toString().padLeft(2, '0')}',
          name: 'T${i + 1}',
          shape: TableShape.rect4,
          x: 50.0 + col * 120,
          y: 50.0 + row * 100,
          capacity: 4,
        ));
      }
      _nextTableNumber = 9;
      _isDirty = true;
    });
  }

  Future<void> _saveLayout() async {
    setState(() => _isLoading = true);
    try {
      final layoutJson = _tables.map((t) => t.toJson()).toList();

      // Get current config and update extra_settings
      final config = await ApiService().getStoreConfig(widget.storeId);
      Map<String, dynamic> extraSettings = {};
      if (config != null && config['extra_settings'] != null) {
        extraSettings = Map<String, dynamic>.from(config['extra_settings']);
      }
      extraSettings['table_layout'] = layoutJson;

      final result = await ApiService().updateStoreConfig(widget.storeId, {
        'extra_settings': extraSettings,
        'table_count': _tables.length,
      });

      if (result != null && mounted) {
        setState(() => _isDirty = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Layout saved!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Save failed: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _addTable(TableShape shape) {
    final newTable = TableData(
      id: 'T${_nextTableNumber.toString().padLeft(2, '0')}',
      name: 'T$_nextTableNumber',
      shape: shape,
      x: 100,
      y: 100,
      capacity: _getCapacityForShape(shape),
    );
    setState(() {
      _tables.add(newTable);
      _selectedTableId = newTable.id;
      _nextTableNumber++;
      _isDirty = true;
    });
  }

  int _getCapacityForShape(TableShape shape) {
    switch (shape) {
      case TableShape.rect2:
        return 2;
      case TableShape.rect4:
      case TableShape.round4:
        return 4;
      case TableShape.rect6:
      case TableShape.round6:
        return 6;
      case TableShape.bar:
        return 1;
    }
  }

  void _deleteSelectedTable() {
    if (_selectedTableId == null) return;
    setState(() {
      _tables.removeWhere((t) => t.id == _selectedTableId);
      _selectedTableId = null;
      _isDirty = true;
    });
  }

  void _updateTablePosition(String id, double dx, double dy) {
    setState(() {
      final table = _tables.firstWhere((t) => t.id == id);
      table.x = (table.x + dx).clamp(0, 800);
      table.y = (table.y + dy).clamp(0, 600);
      _isDirty = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Table Layout Editor'),
        actions: [
          if (_isDirty)
            TextButton.icon(
              onPressed: _saveLayout,
              icon: const Icon(Icons.save, color: Colors.white),
              label: const Text('Save', style: TextStyle(color: Colors.white)),
            ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadLayout,
            tooltip: 'Reset',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Row(
              children: [
                // Toolbox
                Container(
                  width: 120,
                  color: Colors.grey[100],
                  child: Column(
                    children: [
                      const Padding(
                        padding: EdgeInsets.all(12),
                        child: Text(
                          'Add Table',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                      _buildToolButton('2-Seat', TableShape.rect2, Icons.table_bar),
                      _buildToolButton('4-Seat', TableShape.rect4, Icons.table_restaurant),
                      _buildToolButton('6-Seat', TableShape.rect6, Icons.table_restaurant),
                      _buildToolButton('Round 4', TableShape.round4, Icons.circle_outlined),
                      _buildToolButton('Round 6', TableShape.round6, Icons.circle),
                      _buildToolButton('Bar', TableShape.bar, Icons.local_bar),
                      const Divider(),
                      if (_selectedTableId != null)
                        Padding(
                          padding: const EdgeInsets.all(8),
                          child: ElevatedButton.icon(
                            onPressed: _deleteSelectedTable,
                            icon: const Icon(Icons.delete, size: 18),
                            label: const Text('Delete'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.red,
                              foregroundColor: Colors.white,
                            ),
                          ),
                        ),
                      const Spacer(),
                      Padding(
                        padding: const EdgeInsets.all(12),
                        child: Text(
                          '${_tables.length} tables',
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                      ),
                    ],
                  ),
                ),
                // Canvas
                Expanded(
                  child: Container(
                    color: Colors.grey[200],
                    child: Stack(
                      children: [
                        // Grid background
                        CustomPaint(
                          size: Size.infinite,
                          painter: GridPainter(),
                        ),
                        // Tables
                        ..._tables.map((table) => _buildDraggableTable(table)),
                      ],
                    ),
                  ),
                ),
                // Properties panel
                if (_selectedTableId != null)
                  Container(
                    width: 180,
                    color: Colors.white,
                    padding: const EdgeInsets.all(16),
                    child: _buildPropertiesPanel(),
                  ),
              ],
            ),
    );
  }

  Widget _buildToolButton(String label, TableShape shape, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: ElevatedButton(
        onPressed: () => _addTable(shape),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white,
          foregroundColor: Colors.black87,
          padding: const EdgeInsets.symmetric(vertical: 12),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 24),
            const SizedBox(height: 4),
            Text(label, style: const TextStyle(fontSize: 11)),
          ],
        ),
      ),
    );
  }

  Widget _buildDraggableTable(TableData table) {
    final isSelected = table.id == _selectedTableId;
    final size = table.size;

    return Positioned(
      left: table.x,
      top: table.y,
      child: GestureDetector(
        onTap: () => setState(() => _selectedTableId = table.id),
        onPanUpdate: (details) {
          _updateTablePosition(table.id, details.delta.dx, details.delta.dy);
        },
        child: Container(
          width: size.width,
          height: size.height,
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF3B82F6) : Colors.brown[300],
            borderRadius: table.shape == TableShape.round4 ||
                          table.shape == TableShape.round6
                ? BorderRadius.circular(size.width / 2)
                : BorderRadius.circular(8),
            border: Border.all(
              color: isSelected ? Colors.blue[800]! : Colors.brown[600]!,
              width: isSelected ? 3 : 2,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.2),
                blurRadius: 4,
                offset: const Offset(2, 2),
              ),
            ],
          ),
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  table.name,
                  style: TextStyle(
                    color: isSelected ? Colors.white : Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
                Text(
                  '${table.capacity}P',
                  style: TextStyle(
                    color: isSelected ? Colors.white70 : Colors.white70,
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPropertiesPanel() {
    final table = _tables.firstWhere((t) => t.id == _selectedTableId);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Properties',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const Divider(),
        const SizedBox(height: 8),
        Text('ID: ${table.id}', style: TextStyle(color: Colors.grey[600])),
        const SizedBox(height: 12),
        TextField(
          controller: TextEditingController(text: table.name),
          decoration: const InputDecoration(
            labelText: 'Name',
            border: OutlineInputBorder(),
            isDense: true,
          ),
          onChanged: (v) {
            setState(() {
              table.name = v;
              _isDirty = true;
            });
          },
        ),
        const SizedBox(height: 12),
        DropdownButtonFormField<int>(
          value: table.capacity,
          decoration: const InputDecoration(
            labelText: 'Capacity',
            border: OutlineInputBorder(),
            isDense: true,
          ),
          items: [1, 2, 4, 6, 8, 10].map((c) =>
            DropdownMenuItem(value: c, child: Text('$c people'))
          ).toList(),
          onChanged: (v) {
            if (v != null) {
              setState(() {
                table.capacity = v;
                _isDirty = true;
              });
            }
          },
        ),
        const SizedBox(height: 12),
        Text('Position', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
        Text('X: ${table.x.toInt()}, Y: ${table.y.toInt()}'),
        const Spacer(),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: _deleteSelectedTable,
            icon: const Icon(Icons.delete, color: Colors.red),
            label: const Text('Delete Table', style: TextStyle(color: Colors.red)),
          ),
        ),
      ],
    );
  }
}

/// Grid painter for the canvas background
class GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.grey[300]!
      ..strokeWidth = 1;

    const gridSize = 20.0;

    // Vertical lines
    for (double x = 0; x < size.width; x += gridSize) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }

    // Horizontal lines
    for (double y = 0; y < size.height; y += gridSize) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
