import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../l10n/app_localizations.dart';

class SalesReportScreen extends StatefulWidget {
  final int storeId;
  const SalesReportScreen({super.key, required this.storeId});

  @override
  State<SalesReportScreen> createState() => _SalesReportScreenState();
}

class _SalesReportScreenState extends State<SalesReportScreen>
    with SingleTickerProviderStateMixin {
  final _currencyFormat = NumberFormat("#,###", "ko_KR");
  final _dateFormat = DateFormat("yyyy-MM-dd");

  late TabController _tabController;

  // 기간 선택
  String _selectedPeriod = 'today'; // today, yesterday, week, month, custom
  DateTime _startDate = DateTime.now();
  DateTime _endDate = DateTime.now();

  // 데이터
  Map<String, dynamic>? _summary;
  List<dynamic> _salesTrend = [];
  List<dynamic> _productRanking = [];
  List<dynamic> _categoryStats = [];
  List<dynamic> _hourlyTrend = [];
  Map<String, dynamic>? _paymentStats;
  bool _isLoading = true;

  final List<Map<String, String>> _periodOptions = [
    {'value': 'today', 'label': '오늘'},
    {'value': 'yesterday', 'label': '어제'},
    {'value': 'week', 'label': '이번 주'},
    {'value': 'month', 'label': '이번 달'},
    {'value': 'custom', 'label': '기간 선택'},
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _updateDateRange() {
    final now = DateTime.now();
    switch (_selectedPeriod) {
      case 'today':
        _startDate = DateTime(now.year, now.month, now.day);
        _endDate = now;
        break;
      case 'yesterday':
        final yesterday = now.subtract(const Duration(days: 1));
        _startDate = DateTime(yesterday.year, yesterday.month, yesterday.day);
        _endDate = DateTime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59);
        break;
      case 'week':
        // 이번 주 월요일부터
        final weekday = now.weekday;
        _startDate = DateTime(now.year, now.month, now.day - weekday + 1);
        _endDate = now;
        break;
      case 'month':
        _startDate = DateTime(now.year, now.month, 1);
        _endDate = now;
        break;
    }
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    _updateDateRange();

    try {
      final startParam = _dateFormat.format(_startDate);
      final endParam = _dateFormat.format(_endDate);

      // 디버그 로그
      debugPrint('[SalesReport] storeId=${widget.storeId}, period=$_selectedPeriod');
      debugPrint('[SalesReport] range: $startParam ~ $endParam');

      final results = await Future.wait([
        ApiService().getRangeReport(widget.storeId, startParam, endParam),
        ApiService().getSalesTrend(widget.storeId, days: 7),
        ApiService().getProductRanking(widget.storeId, limit: 10),
        ApiService().getHourlyTrend(widget.storeId, date: startParam),
      ]);

      setState(() {
        _summary = results[0] as Map<String, dynamic>?;
        debugPrint('[SalesReport] summary: $_summary');
        _salesTrend = results[1] as List<dynamic>;
        _productRanking = results[2] as List<dynamic>;
        _hourlyTrend = results[3] as List<dynamic>;

        // 결제수단별 통계 (range report에서 추출)
        final paymentMethods = _summary?['payment_methods'] as Map<String, dynamic>? ?? {};
        int cardTotal = 0;
        int cashTotal = 0;
        paymentMethods.forEach((method, data) {
          final revenue = (data['revenue'] as num?)?.toInt() ?? 0;
          if (method.toUpperCase() == 'CARD') {
            cardTotal += revenue;
          } else if (method.toUpperCase() == 'CASH') {
            cashTotal += revenue;
          } else {
            // 기타 결제수단은 카드로 분류
            cardTotal += revenue;
          }
        });
        _paymentStats = {'card': cardTotal, 'cash': cashTotal};

        // 카테고리별 통계
        final categorySales = _summary?['category_sales'] as Map<String, dynamic>? ?? {};
        _categoryStats = categorySales.entries.map((e) {
          final data = e.value as Map<String, dynamic>? ?? {};
          return {
            'category_name': e.key,
            'revenue': data['revenue'] ?? 0,
            'count': data['count'] ?? 0,
          };
        }).toList();
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('로드 오류: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _selectDateRange() async {
    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
      initialDateRange: DateTimeRange(start: _startDate, end: _endDate),
      locale: const Locale('ko'),
    );

    if (picked != null) {
      setState(() {
        _selectedPeriod = 'custom';
        _startDate = picked.start;
        _endDate = picked.end;
      });
      _loadData();
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.get('reports')),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
            tooltip: l10n.get('refresh'),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: const [
            Tab(text: '요약'),
            Tab(text: '상품별'),
            Tab(text: '시간대별'),
            Tab(text: '추이'),
          ],
        ),
      ),
      body: Column(
        children: [
          // 기간 선택 바
          _buildPeriodSelector(),

          // 탭 컨텐츠
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : TabBarView(
                    controller: _tabController,
                    children: [
                      _buildSummaryTab(),
                      _buildProductTab(),
                      _buildHourlyTab(),
                      _buildTrendTab(),
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  String _getDateRangeLabel() {
    final displayFormat = DateFormat("M/d(E)", "ko_KR");
    switch (_selectedPeriod) {
      case 'today':
        return displayFormat.format(_startDate);
      case 'yesterday':
        return displayFormat.format(_startDate);
      case 'week':
      case 'month':
      case 'custom':
        if (_startDate.year == _endDate.year &&
            _startDate.month == _endDate.month &&
            _startDate.day == _endDate.day) {
          return displayFormat.format(_startDate);
        }
        return '${displayFormat.format(_startDate)} ~ ${displayFormat.format(_endDate)}';
      default:
        return '';
    }
  }

  Widget _buildPeriodSelector() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      color: Colors.grey[100],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 기간 선택 칩
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: _periodOptions.map((option) {
                final isSelected = _selectedPeriod == option['value'];
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(option['label']!),
                    selected: isSelected,
                    onSelected: (selected) {
                      if (option['value'] == 'custom') {
                        _selectDateRange();
                      } else {
                        setState(() => _selectedPeriod = option['value']!);
                        _loadData();
                      }
                    },
                    selectedColor: const Color(0xFF3B82F6),
                    labelStyle: TextStyle(
                      color: isSelected ? Colors.white : Colors.black87,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          // 선택된 날짜 범위 표시
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFF3B82F6).withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.calendar_today, size: 14, color: Color(0xFF3B82F6)),
                const SizedBox(width: 6),
                Text(
                  _getDateRangeLabel(),
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF3B82F6),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ==================== 요약 탭 ====================
  Widget _buildSummaryTab() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildMainStats(),
            const SizedBox(height: 20),
            _buildPaymentMethodStats(),
            const SizedBox(height: 20),
            _buildCategoryStats(),
          ],
        ),
      ),
    );
  }

  Widget _buildMainStats() {
    final totalRevenue = _summary?['total_revenue'] ?? _summary?['today_revenue'] ?? 0;
    final totalOrders = _summary?['total_orders'] ?? _summary?['today_orders'] ?? 0;
    final avgOrder = totalOrders > 0 ? (totalRevenue / totalOrders).round() : 0;
    final prevRevenue = _summary?['prev_revenue'] ?? _summary?['yesterday_revenue'] ?? 0;
    final growthRate = prevRevenue > 0
        ? ((totalRevenue - prevRevenue) / prevRevenue * 100)
        : 0.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.analytics, color: Color(0xFF3B82F6)),
            const SizedBox(width: 8),
            Text(
              _getPeriodLabel(),
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // 메인 매출 카드
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF3B82F6), Color(0xFF1D4ED8)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF3B82F6).withValues(alpha: 0.3),
                blurRadius: 10,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '총 매출',
                style: TextStyle(color: Colors.white70, fontSize: 14),
              ),
              const SizedBox(height: 8),
              Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    _currencyFormat.format(totalRevenue),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Text(
                    '원',
                    style: TextStyle(color: Colors.white, fontSize: 18),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: growthRate >= 0
                          ? Colors.green.withValues(alpha: 0.2)
                          : Colors.red.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          growthRate >= 0 ? Icons.arrow_upward : Icons.arrow_downward,
                          color: growthRate >= 0 ? Colors.greenAccent : Colors.redAccent,
                          size: 14,
                        ),
                        Text(
                          '${growthRate >= 0 ? '+' : ''}${growthRate.toStringAsFixed(1)}%',
                          style: TextStyle(
                            color: growthRate >= 0 ? Colors.greenAccent : Colors.redAccent,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '전일 대비',
                    style: TextStyle(color: Colors.white.withValues(alpha: 0.7), fontSize: 12),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // 상세 통계 그리드
        Row(
          children: [
            Expanded(
              child: _buildSmallStatCard(
                '주문 수',
                '$totalOrders건',
                Icons.receipt_long,
                Colors.purple,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildSmallStatCard(
                '객단가',
                '${_currencyFormat.format(avgOrder)}원',
                Icons.person,
                Colors.teal,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSmallStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: TextStyle(color: Colors.grey[600], fontSize: 12),
              ),
              Icon(icon, color: color, size: 18),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPaymentMethodStats() {
    final cardAmount = _paymentStats?['card'] ?? 0;
    final cashAmount = _paymentStats?['cash'] ?? 0;
    final totalAmount = cardAmount + cashAmount;

    if (totalAmount == 0) {
      return const SizedBox.shrink();
    }

    final int cardPercent = (cardAmount / totalAmount * 100).round();
    final int cashPercent = cardPercent < 100 ? 100 - cardPercent : 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.payment, color: Colors.orange),
            SizedBox(width: 8),
            Text(
              '결제수단별',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey[200]!),
          ),
          child: Column(
            children: [
              // 바 차트
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Row(
                  children: [
                    Expanded(
                      flex: cardPercent > 0 ? cardPercent : 1,
                      child: Container(
                        height: 24,
                        color: const Color(0xFF3B82F6),
                        alignment: Alignment.center,
                        child: Text(
                          cardPercent > 10 ? '카드 $cardPercent%' : '',
                          style: const TextStyle(color: Colors.white, fontSize: 11),
                        ),
                      ),
                    ),
                    Expanded(
                      flex: cashPercent > 0 ? cashPercent : 1,
                      child: Container(
                        height: 24,
                        color: Colors.green,
                        alignment: Alignment.center,
                        child: Text(
                          cashPercent > 10 ? '현금 $cashPercent%' : '',
                          style: const TextStyle(color: Colors.white, fontSize: 11),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _buildPaymentItem('카드', cardAmount, const Color(0xFF3B82F6)),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildPaymentItem('현금', cashAmount, Colors.green),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPaymentItem(String label, int amount, Color color) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(3),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              Text(
                '${_currencyFormat.format(amount)}원',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildCategoryStats() {
    if (_categoryStats.isEmpty) {
      return const SizedBox.shrink();
    }

    final totalRevenue = _categoryStats.fold<int>(
      0,
      (sum, cat) => sum + ((cat['revenue'] as num?)?.toInt() ?? 0),
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.category, color: Colors.purple),
            SizedBox(width: 8),
            Text(
              '카테고리별',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey[200]!),
          ),
          child: Column(
            children: _categoryStats.asMap().entries.map((entry) {
              final index = entry.key;
              final cat = entry.value;
              final revenue = (cat['revenue'] as num?)?.toInt() ?? 0;
              final percent = totalRevenue > 0 ? (revenue / totalRevenue * 100) : 0.0;
              final colors = [Colors.blue, Colors.purple, Colors.teal, Colors.orange, Colors.pink];

              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          cat['category_name'] ?? '',
                          style: const TextStyle(fontWeight: FontWeight.w500),
                        ),
                        Text(
                          '${_currencyFormat.format(revenue)}원 (${percent.toStringAsFixed(1)}%)',
                          style: TextStyle(color: Colors.grey[600], fontSize: 13),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: percent / 100,
                        backgroundColor: Colors.grey[200],
                        valueColor: AlwaysStoppedAnimation(colors[index % colors.length]),
                        minHeight: 8,
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  // ==================== 상품별 탭 ====================
  Widget _buildProductTab() {
    if (_productRanking.isEmpty) {
      return const Center(child: Text('판매 데이터가 없습니다'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _productRanking.length,
      itemBuilder: (context, index) {
        final item = _productRanking[index];
        final rank = index + 1;
        final revenue = (item['revenue'] as num?)?.toInt() ?? 0;
        final soldQty = item['sold_qty'] ?? 0;

        Color rankColor;
        IconData rankIcon;
        if (rank == 1) {
          rankColor = Colors.amber;
          rankIcon = Icons.emoji_events;
        } else if (rank == 2) {
          rankColor = Colors.grey;
          rankIcon = Icons.workspace_premium;
        } else if (rank == 3) {
          rankColor = Colors.brown;
          rankIcon = Icons.military_tech;
        } else {
          rankColor = Colors.grey[400]!;
          rankIcon = Icons.tag;
        }

        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: rankColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: rank <= 3
                  ? Icon(rankIcon, color: rankColor)
                  : Center(
                      child: Text(
                        '#$rank',
                        style: TextStyle(
                          color: rankColor,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
            ),
            title: Text(
              item['product_name'] ?? '',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
            subtitle: Text('판매 $soldQty개'),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${_currencyFormat.format(revenue)}원',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF3B82F6),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  // ==================== 시간대별 탭 ====================
  Widget _buildHourlyTab() {
    if (_hourlyTrend.isEmpty) {
      return const Center(child: Text('시간대별 데이터가 없습니다'));
    }

    final maxOrders = _hourlyTrend.fold<int>(
      0,
      (max, h) => ((h['orders'] as num?)?.toInt() ?? 0) > max ? (h['orders'] as num).toInt() : max,
    );

    // 피크타임 찾기
    final peakHour = _hourlyTrend.reduce((a, b) =>
        ((a['orders'] as num?)?.toInt() ?? 0) >= ((b['orders'] as num?)?.toInt() ?? 0) ? a : b);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 피크타임 카드
          if (maxOrders > 0)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange[50],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.orange[200]!),
              ),
              child: Row(
                children: [
                  Icon(Icons.access_time, color: Colors.orange[700], size: 32),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '피크타임',
                        style: TextStyle(color: Colors.orange[700], fontSize: 12),
                      ),
                      Text(
                        '${peakHour['hour']}시',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.orange[800],
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '${peakHour['orders']}건',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.orange[800],
                        ),
                      ),
                      Text(
                        '${_currencyFormat.format(peakHour['revenue'] ?? 0)}원',
                        style: TextStyle(color: Colors.orange[700], fontSize: 12),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          const SizedBox(height: 20),

          // 시간대별 차트
          const Text(
            '시간대별 주문',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          Container(
            height: 200,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey[200]!),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: _hourlyTrend.map((h) {
                final orders = (h['orders'] as num?)?.toInt() ?? 0;
                final hour = h['hour']?.toString() ?? '0';
                final heightRatio = maxOrders > 0 ? orders / maxOrders : 0.0;
                final isPeak = orders == maxOrders && maxOrders > 0;

                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        if (orders > 0)
                          Text(
                            orders.toString(),
                            style: TextStyle(
                              fontSize: 9,
                              fontWeight: isPeak ? FontWeight.bold : FontWeight.normal,
                              color: isPeak ? Colors.orange : Colors.grey,
                            ),
                          ),
                        const SizedBox(height: 4),
                        Container(
                          height: 120 * heightRatio,
                          decoration: BoxDecoration(
                            color: isPeak
                                ? Colors.orange
                                : orders > 0
                                    ? const Color(0xFF3B82F6)
                                    : Colors.grey[200],
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          hour.padLeft(2, '0'),
                          style: TextStyle(
                            fontSize: 9,
                            color: isPeak ? Colors.orange : Colors.grey[600],
                            fontWeight: isPeak ? FontWeight.bold : FontWeight.normal,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  // ==================== 추이 탭 ====================
  Widget _buildTrendTab() {
    if (_salesTrend.isEmpty) {
      return const Center(child: Text('추이 데이터가 없습니다'));
    }

    final maxRevenue = _salesTrend.fold<int>(
      0,
      (max, item) => ((item['revenue'] as num?)?.toInt() ?? 0) > max
          ? (item['revenue'] as num).toInt()
          : max,
    );

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.show_chart, color: Color(0xFF3B82F6)),
              SizedBox(width: 8),
              Text(
                '7일간 매출 추이',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            height: 250,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey[200]!),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: _salesTrend.asMap().entries.map((entry) {
                final index = entry.key;
                final item = entry.value;
                final revenue = (item['revenue'] as num?)?.toInt() ?? 0;
                final date = item['date']?.toString() ?? '';
                final heightRatio = maxRevenue > 0 ? revenue / maxRevenue : 0.0;
                final isToday = index == _salesTrend.length - 1;

                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text(
                          '${(revenue / 10000).toStringAsFixed(0)}만',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: isToday ? FontWeight.bold : FontWeight.normal,
                            color: isToday ? const Color(0xFF3B82F6) : Colors.grey,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          height: 150 * heightRatio,
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: isToday
                                  ? [const Color(0xFF3B82F6), const Color(0xFF1D4ED8)]
                                  : [Colors.grey[400]!, Colors.grey[500]!],
                              begin: Alignment.topCenter,
                              end: Alignment.bottomCenter,
                            ),
                            borderRadius: BorderRadius.circular(6),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          date.length >= 5 ? date.substring(5) : date,
                          style: TextStyle(
                            fontSize: 11,
                            color: isToday ? const Color(0xFF3B82F6) : Colors.grey[600],
                            fontWeight: isToday ? FontWeight.bold : FontWeight.normal,
                          ),
                        ),
                        Text(
                          _getWeekday(date),
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.grey[500],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),

          const SizedBox(height: 20),

          // 일별 상세 리스트
          const Text(
            '일별 상세',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          ...(_salesTrend.reversed.map((item) {
            final date = item['date']?.toString() ?? '';
            final revenue = (item['revenue'] as num?)?.toInt() ?? 0;
            final orders = item['orders'] ?? 0;

            return Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: ListTile(
                leading: Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        date.length >= 8 ? date.substring(8) : '',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        _getWeekday(date),
                        style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
                title: Text(
                  '${_currencyFormat.format(revenue)}원',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle: Text('주문 ${orders}건'),
                trailing: Icon(
                  Icons.chevron_right,
                  color: Colors.grey[400],
                ),
              ),
            );
          })),
        ],
      ),
    );
  }

  String _getPeriodLabel() {
    switch (_selectedPeriod) {
      case 'today':
        return '오늘 매출';
      case 'yesterday':
        return '어제 매출';
      case 'week':
        return '이번 주 매출';
      case 'month':
        return '이번 달 매출';
      case 'custom':
        return '${_dateFormat.format(_startDate)} ~ ${_dateFormat.format(_endDate)}';
      default:
        return '매출';
    }
  }

  String _getWeekday(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      const weekdays = ['월', '화', '수', '목', '금', '토', '일'];
      return weekdays[date.weekday - 1];
    } catch (e) {
      return '';
    }
  }
}
