#!/usr/bin/env python3
"""
测试更新脚本的简化版本
只测试统计功能，不抓取新数据
"""

import os
import sys
from datetime import datetime

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from data_scraper import load_historical_data
from statistics import generate_comprehensive_statistics, print_statistics_report, update_readme


def test_statistics():
    """测试统计功能"""
    print("=" * 60)
    print("测试统计模块")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        # 1. 加载历史数据
        print("\n步骤1: 加载历史数据...")
        historical_data = load_historical_data()

        if not historical_data:
            print("数据库中暂无数据，请先运行 update.py 或执行数据迁移")
            sys.exit(1)

        print(f"已加载数据年份: {sorted(historical_data.keys())}")
        for year, data in sorted(historical_data.items()):
            print(f"  {year}年: {len(data)} 条记录")

        # 自动选取最新年份作为当前年份
        current_year = max(historical_data.keys())
        print(f"\n使用 {current_year} 作为当前年份进行统计测试")

        # 2. 生成统计报告
        print("\n步骤2: 生成统计报告...")
        chart_dir = os.path.join(os.path.dirname(current_dir), 'chart')

        statistics = generate_comprehensive_statistics(historical_data, current_year)

        readme_path = os.path.join(os.path.dirname(current_dir), 'README.md')
        update_readme(statistics, readme_path)

        print_statistics_report(statistics)

        print("\n" + "=" * 60)
        print("统计模块测试完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_statistics()
