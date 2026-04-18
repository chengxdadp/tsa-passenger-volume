import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os


def _get_colors(n):
    """
    为 n 个年份生成视觉上互不重复的颜色列表。
    tab10 提供 10 个高对比度颜色，超出时用 tab20 扩充。
    """
    if n <= 10:
        cmap = plt.get_cmap('tab10')
        return [cmap(i) for i in range(n)]
    else:
        cmap = plt.get_cmap('tab20')
        return [cmap(i % 20) for i in range(n)]


def _add_outside_legend(ax, ncol=1):
    """将图例放置在图表右侧外部，避免遮挡数据。"""
    ax.legend(
        loc='upper left',
        bbox_to_anchor=(1.01, 1),
        borderaxespad=0,
        fontsize=11,
        framealpha=0.9,
        ncol=ncol,
    )


def _set_xaxis_month_labels(ax, reference_data, n_ticks=12):
    """按月份均匀设置 x 轴刻度标签。"""
    n = len(reference_data)
    if n == 0:
        return
    step = max(n // n_ticks, 1)
    indices = list(range(0, n, step))
    labels = [reference_data.iloc[i]['month_day'] for i in indices if i < n]
    ax.set_xticks(indices[:len(labels)])
    ax.set_xticklabels(labels, rotation=45, ha='right')


def create_7day_moving_average_chart(processed_data, output_dir='../chart'):
    """
    创建7日移动平均图表

    参数:
    processed_data: 处理后的数据字典（按年份排序）
    output_dir: 输出目录
    """
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(16, 7))

    sorted_years = sorted(processed_data.keys())
    colors = _get_colors(len(sorted_years))

    for color, year in zip(colors, sorted_years):
        data = processed_data[year]
        ax.plot(
            range(len(data)), data['7day_avg'],
            label=year, linewidth=2.2, alpha=0.9, color=color,
        )

    ax.set_title(
        'TSA Daily Passenger Volumes — 7-Day Moving Average',
        fontsize=15, fontweight='bold', pad=12,
    )
    ax.set_xlabel('Month-Day', fontsize=12)
    ax.set_ylabel('Passengers (7-day avg)', fontsize=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
    ax.grid(True, alpha=0.3)

    # x 轴月份标签
    reference_year = max(sorted_years, key=lambda k: len(processed_data[k]))
    _set_xaxis_month_labels(ax, processed_data[reference_year])

    _add_outside_legend(ax)

    chart_path = os.path.join(output_dir, 'tsa_7day_moving_average.png')
    fig.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"图表已保存到: {chart_path}")


def create_monthly_trend_chart(processed_data, output_dir='../chart'):
    """
    创建月度平均客流趋势图

    参数:
    processed_data: 处理后的数据字典
    output_dir: 输出目录
    """
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(16, 7))

    sorted_years = sorted(processed_data.keys())
    colors = _get_colors(len(sorted_years))

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for color, year in zip(colors, sorted_years):
        data = processed_data[year]
        monthly_avg = data.groupby(data['Date'].dt.month)['Passenger_Numbers'].mean()
        ax.plot(
            list(monthly_avg.index), list(monthly_avg.values),
            marker='o', linewidth=2.2, markersize=5,
            label=year, color=color,
        )

    ax.set_title(
        'TSA Monthly Average Passenger Volumes',
        fontsize=15, fontweight='bold', pad=12,
    )
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Avg Passengers', fontsize=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
    ax.grid(True, alpha=0.3)

    _add_outside_legend(ax)

    chart_path = os.path.join(output_dir, 'tsa_monthly_trend.png')
    fig.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"图表已保存到: {chart_path}")


def create_recent_years_chart(processed_data, output_dir='../chart', n_years=3):
    """
    创建近 n 年对比图（默认最近3年）。
    仅保留7日均线，避免与全量图表和散点图重复。

    参数:
    processed_data: 处理后的数据字典
    output_dir: 输出目录
    n_years: 展示最近几年，默认 3
    """
    os.makedirs(output_dir, exist_ok=True)

    all_years = sorted(processed_data.keys())
    recent_years = all_years[-n_years:]          # 取最近 n 年
    colors = _get_colors(len(recent_years))

    fig, ax = plt.subplots(figsize=(16, 7))

    for color, year in zip(colors, recent_years):
        data = processed_data[year]
        # 7日均线（主线）
        ax.plot(
            range(len(data)), data['7day_avg'],
            label=f'{year}', color=color, linewidth=2.5, alpha=0.95,
        )

    ax.set_title(
        f'TSA Daily Passenger Volumes — Recent {n_years} Years',
        fontsize=15, fontweight='bold', pad=12,
    )
    ax.set_xlabel('Month-Day', fontsize=12)
    ax.set_ylabel('Passengers', fontsize=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))
    ax.grid(True, alpha=0.3)

    # x 轴：以数据最完整的近期年份为参考
    reference_year = max(recent_years, key=lambda k: len(processed_data[k]))
    _set_xaxis_month_labels(ax, processed_data[reference_year])

    _add_outside_legend(ax)

    chart_path = os.path.join(output_dir, 'tsa_recent_years.png')
    fig.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"图表已保存到: {chart_path}")


if __name__ == "__main__":
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    from data_scraper import load_historical_data
    from data_processor import prepare_data_for_visualization

    data_dict = load_historical_data()
    if not data_dict:
        print("数据库中暂无数据，请先运行 update.py 或执行数据迁移")
    else:
        processed_data = prepare_data_for_visualization(data_dict)
        chart_dir = os.path.join(os.path.dirname(current_dir), 'chart')
        print("开始创建图表...")
        create_7day_moving_average_chart(processed_data, chart_dir)
        create_monthly_trend_chart(processed_data, chart_dir)
        create_recent_years_chart(processed_data, chart_dir)
        print("图表创建完成")
