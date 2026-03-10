import pandas as pd
import os
from datetime import datetime
from data_processor import get_same_period_data, filter_data_by_month_range


def _resolve_year(year):
    """将年份统一转为字符串；None 时返回当前年份字符串"""
    if year is None:
        return str(datetime.now().year)
    return str(year)


def ensure_month_day_column(data):
    """
    确保数据包含month_day列
    
    参数:
    data: DataFrame数据
    
    返回:
    包含month_day列的DataFrame
    """
    df = data.copy()
    if 'month_day' not in df.columns:
        df['month_day'] = df['Date'].dt.strftime('%m-%d')
    return df


def calculate_growth_rate(current_total, previous_total):
    """
    计算增长率
    
    参数:
    current_total: 当前期间总量
    previous_total: 对比期间总量
    
    返回:
    增长率（百分比）
    """
    if previous_total > 0:
        return ((current_total - previous_total) / previous_total) * 100
    return None


def calculate_ytd_growth(data_dict, current_year, comparison_year):
    """
    计算年初至今(YTD)增长率
    
    参数:
    data_dict: 包含各年份数据的字典
    current_year: 当前年份
    comparison_year: 对比年份
    
    返回:
    增长率统计字典
    """
    current_data = ensure_month_day_column(data_dict[current_year])
    comparison_data = ensure_month_day_column(data_dict[comparison_year])
    
    # 获取当前年份同期数据
    same_period_comparison = get_same_period_data(current_data, comparison_data)
    
    total_current = current_data['Passenger_Numbers'].sum()
    total_comparison = same_period_comparison['Passenger_Numbers'].sum()
    
    growth_rate = calculate_growth_rate(total_current, total_comparison)
    
    return {
        'current_year': current_year,
        'comparison_year': comparison_year,
        'current_total': total_current,
        'comparison_total': total_comparison,
        'growth_rate': growth_rate,
        'period_type': 'YTD'
    }


def calculate_period_growth(data_dict, current_year, comparison_year, start_month, end_month):
    """
    计算指定月份期间的增长率
    
    参数:
    data_dict: 包含各年份数据的字典
    current_year: 当前年份
    comparison_year: 对比年份
    start_month: 开始月份
    end_month: 结束月份
    
    返回:
    增长率统计字典
    """
    current_data = ensure_month_day_column(data_dict[current_year])
    comparison_data = ensure_month_day_column(data_dict[comparison_year])
    
    # 过滤指定月份期间的数据
    current_period = filter_data_by_month_range(current_data, start_month, end_month)
    comparison_period = filter_data_by_month_range(comparison_data, start_month, end_month)
    
    # 如果是当前年份数据，需要找到对应的同期数据
    if current_year > comparison_year:
        comparison_same_period = get_same_period_data(current_period, comparison_period)
        comparison_total = comparison_same_period['Passenger_Numbers'].sum()
    else:
        comparison_total = comparison_period['Passenger_Numbers'].sum()
    
    current_total = current_period['Passenger_Numbers'].sum()
    growth_rate = calculate_growth_rate(current_total, comparison_total)
    
    return {
        'current_year': current_year,
        'comparison_year': comparison_year,
        'current_total': current_total,
        'comparison_total': comparison_total,
        'growth_rate': growth_rate,
        'period_type': f'{start_month}-{end_month}月',
        'start_month': start_month,
        'end_month': end_month
    }


def generate_comprehensive_statistics(data_dict, current_year=None):
    """
    生成综合统计报告
    
    参数:
    data_dict: 包含各年份数据的字典
    current_year: 当前年份
    
    返回:
    统计结果字典
    """
    current_year = _resolve_year(current_year)
    statistics = {}

    available_years = sorted(data_dict.keys())

    if current_year in available_years:
        # YTD增长率对比
        ytd_stats = []
        for year in available_years:
            if year < current_year:
                ytd_stat = calculate_ytd_growth(data_dict, current_year, year)
                ytd_stats.append(ytd_stat)
        
        statistics['ytd_growth'] = ytd_stats
        
        # 分期间增长率分析
        period_stats = []
        
        # 1-6月增长率
        if len(available_years) > 1:
            for year in available_years:
                if year < current_year:
                    jan_jun_stat = calculate_period_growth(data_dict, current_year, year, 1, 6)
                    period_stats.append(jan_jun_stat)
        
        # 7月至今增长率
        for year in available_years:
            if year < current_year:
                july_stat = calculate_period_growth(data_dict, current_year, year, 7, 12)
                period_stats.append(july_stat)
        
        statistics['period_growth'] = period_stats
        
        # 基本统计信息
        basic_stats = {}
        for year, data in data_dict.items():
            basic_stats[year] = {
                'total_records': len(data),
                'total_passengers': data['Passenger_Numbers'].sum(),
                'daily_average': data['Passenger_Numbers'].mean(),
                'date_range': {
                    'start': data['Date'].min().strftime('%Y-%m-%d'),
                    'end': data['Date'].max().strftime('%Y-%m-%d')
                }
            }
        
        statistics['basic_stats'] = basic_stats
    
    return statistics


def _build_stats_block(statistics):
    """
    构建写入 README.md 动态区域的 Markdown 文本块。
    """
    now = datetime.now()
    update_date = now.strftime('%Y-%m-%d')

    lines = []

    # ---- 数据截至时间 ----
    if 'basic_stats' in statistics:
        current_year = max(statistics['basic_stats'].keys())
        data_end = statistics['basic_stats'][current_year]['date_range']['end']
        lines.append(f'> **数据截至** {data_end} &nbsp;·&nbsp; **更新于** {update_date}')
        lines.append('')

    # ---- 各年份数据概览 ----
    if 'basic_stats' in statistics:
        lines.append('### 各年份数据概览')
        lines.append('')
        lines.append('| 年份 | 天数 | 累计客流 | 日均客流 | 数据区间 |')
        lines.append('|:----:|-----:|---------:|---------:|---------|')
        for year, s in sorted(statistics['basic_stats'].items(), reverse=True):
            bold = '**' if year == current_year else ''
            total = f"{s['total_passengers']:,}"
            avg   = f"{s['daily_average']:,.0f}"
            rng   = f"{s['date_range']['start']} ~ {s['date_range']['end']}"
            lines.append(f"| {bold}{year}{bold} | {s['total_records']} | {total} | {avg} | {rng} |")
        lines.append('')

    # ---- YTD 增长率 ----
    ytd = [s for s in statistics.get('ytd_growth', []) if s.get('growth_rate') is not None]
    if ytd:
        cy = ytd[0]['current_year']
        lines.append(f'### {cy} 年 YTD 增长率（vs 历年同期）')
        lines.append('')
        lines.append('| 对比年份 | 增长率 | 当前 YTD | 同期客流 |')
        lines.append('|:--------:|:------:|---------:|---------:|')
        for s in ytd:
            arrow = '▲' if s['growth_rate'] > 0 else '▼'
            rate  = f"**{arrow} {s['growth_rate']:+.2f}%**"
            lines.append(f"| vs {s['comparison_year']} | {rate} | {s['current_total']:,} | {s['comparison_total']:,} |")
        lines.append('')

    # ---- 分时段增长率（仅展示有数据的时段）----
    period = statistics.get('period_growth', [])
    h1 = [s for s in period if s.get('growth_rate') is not None and '1-6' in s.get('period_type', '')]
    h2 = [s for s in period if s.get('growth_rate') is not None and '7-12' in s.get('period_type', '')]

    # 若上半年数据与 YTD 完全相同（当前年份尚未进入下半年），则跳过上半年表避免重复
    ytd_totals = {s['comparison_year']: s['current_total'] for s in ytd}
    h1_totals  = {s['comparison_year']: s['current_total'] for s in h1}
    h1_same_as_ytd = ytd_totals == h1_totals

    for label, rows in [('上半年（1–6 月）增长率', h1), ('下半年（7–12 月）增长率', h2)]:
        if not rows:
            continue
        if label.startswith('上半年') and h1_same_as_ytd:
            continue   # 与 YTD 重复，跳过
        cy = rows[0]['current_year']
        lines.append(f'### {cy} 年{label}（vs 历年同期）')
        lines.append('')
        lines.append('| 对比年份 | 增长率 | 当前 | 同期 |')
        lines.append('|:--------:|:------:|-----:|-----:|')
        for s in rows:
            arrow = '▲' if s['growth_rate'] > 0 else '▼'
            rate  = f"**{arrow} {s['growth_rate']:+.2f}%**"
            lines.append(f"| vs {s['comparison_year']} | {rate} | {s['current_total']:,} | {s['comparison_total']:,} |")
        lines.append('')

    return '\n'.join(lines)


def update_readme(statistics, readme_path):
    """
    将最新统计数据写入 README.md 的动态区域。

    README.md 中需包含以下两个 HTML 注释标记：
        <!-- STATS_START -->
        （此处内容将被自动替换）
        <!-- STATS_END -->

    参数:
    statistics: generate_comprehensive_statistics() 返回的统计字典
    readme_path: README.md 的绝对路径

    返回:
    readme_path
    """
    START = '<!-- STATS_START -->'
    END   = '<!-- STATS_END -->'

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if START not in content or END not in content:
        print(f"警告: README.md 中未找到统计标记，跳过更新")
        return readme_path

    block = _build_stats_block(statistics)
    new_content = (
        content[:content.index(START) + len(START)]
        + '\n'
        + block
        + '\n'
        + content[content.index(END):]
    )

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"README.md 已更新: {readme_path}")
    return readme_path


def print_statistics_report(statistics):
    """
    打印统计报告到控制台
    
    参数:
    statistics: 统计结果字典
    """
    print("=" * 60)
    print("TSA客流量统计报告")
    print("=" * 60)
    
    # 基本统计信息
    if 'basic_stats' in statistics:
        print("\n基本统计信息:")
        print("-" * 40)
        for year, stats in statistics['basic_stats'].items():
            print(f"{year}年:")
            print(f"  记录数量: {stats['total_records']} 条")
            print(f"  总客流量: {stats['total_passengers']:,}")
            print(f"  日均客流: {stats['daily_average']:,.0f}")
            print(f"  数据范围: {stats['date_range']['start']} 至 {stats['date_range']['end']}")
    
    # YTD增长率
    if 'ytd_growth' in statistics and statistics['ytd_growth']:
        print("\n年初至今(YTD)增长率:")
        print("-" * 40)
        for stat in statistics['ytd_growth']:
            if stat['growth_rate'] is not None:
                print(f"{stat['current_year']}年YTD较{stat['comparison_year']}年增长率: {stat['growth_rate']:.2f}%")
    
    # 分期间增长率
    if 'period_growth' in statistics and statistics['period_growth']:
        print("\n分期间增长率:")
        print("-" * 40)
        for stat in statistics['period_growth']:
            if stat['growth_rate'] is not None:
                print(f"{stat['current_year']}年{stat['period_type']}较{stat['comparison_year']}年增长率: {stat['growth_rate']:.2f}%")
                print(f"  当前期间总客流: {stat['current_total']:,}")
                print(f"  对比期间总客流: {stat['comparison_total']:,}")


if __name__ == "__main__":
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    from data_scraper import load_historical_data

    data_dict = load_historical_data()
    if not data_dict:
        print("数据库中暂无数据，请先运行 update.py 或执行数据迁移")
    else:
        print("生成统计报告...")
        stats = generate_comprehensive_statistics(data_dict)
        print_statistics_report(stats)