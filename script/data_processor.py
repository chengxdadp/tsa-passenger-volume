import pandas as pd


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


def prepare_data_for_visualization(data_dict):
    """
    为可视化准备数据，添加月-日格式和排序键
    
    参数:
    data_dict: 包含各年份数据的字典
    
    返回:
    处理后的数据字典
    """
    processed_data = {}
    
    for year, data in data_dict.items():
        df = data.copy()
        
        # 创建月-日格式的日期用于横轴显示
        df['month_day'] = df['Date'].dt.strftime('%m-%d')
        
        # 创建用于排序的数值（月*100+日）
        df['sort_key'] = df['Date'].dt.month * 100 + df['Date'].dt.day
        
        # 按月-日排序
        df_sorted = df.sort_values('sort_key').reset_index(drop=True)
        
        # 计算7日滑动平均
        df_sorted['7day_avg'] = df_sorted['Passenger_Numbers'].rolling(window=7, center=True).mean()
        
        processed_data[year] = df_sorted
    
    return processed_data


def get_same_period_data(reference_data, comparison_data):
    """
    获取与参考数据相同时间段的对比数据
    
    参数:
    reference_data: 参考数据DataFrame
    comparison_data: 对比数据DataFrame
    
    返回:
    相同时间段的对比数据
    """
    # 确保两个数据集都有month_day列
    ref_data = ensure_month_day_column(reference_data)
    comp_data = ensure_month_day_column(comparison_data)
    
    available_month_days = set(ref_data['month_day'])
    same_period = comp_data[comp_data['month_day'].isin(available_month_days)]
    return same_period


def filter_data_by_month_range(data, start_month, end_month):
    """
    按月份范围过滤数据
    
    参数:
    data: DataFrame数据
    start_month: 开始月份
    end_month: 结束月份
    
    返回:
    过滤后的数据
    """
    mask = (data['Date'].dt.month >= start_month) & (data['Date'].dt.month <= end_month)
    return data.loc[mask]


def calculate_period_totals(data_dict, reference_year, reference_month_range=None):
    """
    计算各年份在指定时间段的总客流量
    
    参数:
    data_dict: 包含各年份数据的字典
    reference_year: 参考年份（用于确定时间范围）
    reference_month_range: 月份范围元组(start_month, end_month)，如果为None则使用全部数据
    
    返回:
    各年份总客流量字典
    """
    totals = {}
    
    reference_data = data_dict[reference_year]
    
    if reference_month_range:
        start_month, end_month = reference_month_range
        reference_data = filter_data_by_month_range(reference_data, start_month, end_month)
    
    # 获取参考数据的月-日组合
    available_month_days = set(reference_data['month_day'])
    
    for year, data in data_dict.items():
        if reference_month_range:
            start_month, end_month = reference_month_range
            filtered_data = filter_data_by_month_range(data, start_month, end_month)
        else:
            filtered_data = data
        
        # 如果不是参考年份，只计算相同时间段的数据
        if year != reference_year:
            same_period_data = filtered_data[filtered_data['month_day'].isin(available_month_days)]
            totals[year] = same_period_data['Passenger_Numbers'].sum()
        else:
            totals[year] = filtered_data['Passenger_Numbers'].sum()
    
    return totals


if __name__ == "__main__":
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    from data_scraper import load_historical_data

    data_dict = load_historical_data()
    if not data_dict:
        print("数据库中暂无数据，请先运行 update.py 或执行数据迁移")
    else:
        processed_data = prepare_data_for_visualization(data_dict)
        print("数据处理测试成功")
        for year, df in sorted(processed_data.items()):
            print(f"  {year}年数据: {len(df)} 条记录")