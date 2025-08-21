"""WorldQuant Brain 批量 Alpha 生成系统"""

import os
import json

from brain_batch_alpha import BrainBatchAlpha
from dataset_config import get_dataset_by_index, get_dataset_list, get_dataset_recommendation
from alpha_history_manager_sqlite import AlphaHistoryManagerSQLite

STORAGE_ALPHA_ID_PATH = "alpha_ids.txt"


def submit_alpha_ids(brain, num_to_submit=2):
    """提交保存的 Alpha ID"""
    try:
        if not os.path.exists(STORAGE_ALPHA_ID_PATH):
            print("❌ 没有找到保存的Alpha ID文件")
            return

        with open(STORAGE_ALPHA_ID_PATH, 'r') as f:
            alpha_ids = [line.strip() for line in f.readlines() if line.strip()]

        if not alpha_ids:
            print("❌ 没有可提交的Alpha ID")
            return

        print("\n📝 已保存的Alpha ID列表:")
        for i, alpha_id in enumerate(alpha_ids, 1):
            print(f"{i}. {alpha_id}")

        if num_to_submit > len(alpha_ids):
            num_to_submit = len(alpha_ids)

        selected_ids = alpha_ids[:num_to_submit]
        successful, failed = brain.submit_multiple_alphas(selected_ids)

        # 更新 alpha_ids.txt
        remaining_ids = [id for id in alpha_ids if id not in successful]
        with open(STORAGE_ALPHA_ID_PATH, 'w') as f:
            f.writelines([f"{id}\n" for id in remaining_ids])

    except Exception as e:
        print(f"❌ 提交 Alpha 时出错: {str(e)}")


def view_alpha_history():
    """查看Alpha历史记录"""
    try:
        history_manager = AlphaHistoryManagerSQLite()
        history = history_manager.get_history(10)  # 获取最近10条记录
        
        if not history:
            print("❌ 没有找到历史记录")
            return
            
        print(f"\n📋 Alpha 历史记录 (最近10条):")
        for i, record in enumerate(history, 1):
            status = "✅" if record.get('passed_all_checks', False) else "❌"
            expression = record.get('expression', 'Unknown')[:50] + "..." if len(record.get('expression', '')) > 50 else record.get('expression', 'Unknown')
            print(f"{i}. {status} {expression}")
            
        # 显示统计信息
        stats = history_manager.get_statistics()
        print("\n📈 统计信息:")
        print(f"  总测试数: {stats['total_count']}")
        print(f"  成功数: {stats['success_count']}")
        print(f"  成功率: {stats['success_rate']*100:.1f}%")
        
    except Exception as e:
        print(f"❌ 查看历史记录时出错: {str(e)}")


def print_strategy_mode_tips():
    """打印策略模式选择建议"""
    print("\n💡 策略模式选择建议:")
    print("  1. 基础策略模式      - 适合初学者，生成简单但有效的策略")
    print("  2. 多因子组合模式    - 适合有一定经验的用户，生成复杂的多因子策略")
    print("  3. 高级合成模式      - 适合高级用户，生成创新性的因子合成策略")
    print("  4. 动量策略模式      - 专注于价格动量相关的因子")
    print("  5. 价值策略模式      - 专注于价值投资相关的因子")
    print("  6. Alpha101模式      - 基于经典Alpha101因子库的策略")
    print("  7. 组合型Alpha模式    - 生成多个信号组合的Alpha")
    print("  建议: 如果长时间没有合格Alpha，可以尝试不同模式")


def print_dataset_tips(dataset_name):
    """打印数据集使用建议"""
    recommendation = get_dataset_recommendation(dataset_name)
    if recommendation:
        print(f"\n💡 数据集使用建议:")
        print(f"  {recommendation}")


def main():
    """主程序入口"""
    try:
        print("🚀 启动 WorldQuant Brain 批量 Alpha 生成系统")

        print("\n📋 请选择运行模式:")
        print("1: 自动模式 (测试并自动提交 2 个合格 Alpha)")
        print("2: 仅测试模式 (测试并保存合格 Alpha ID)")
        print("3: 仅提交模式 (提交已保存的合格 Alpha ID)")
        print("4: 查看历史记录")

        mode = int(input("\n请选择模式 (1-4): "))
        if mode not in [1, 2, 3, 4]:
            print("❌ 无效的模式选择")
            return

        brain = BrainBatchAlpha()

        if mode in [1, 2]:
            print("\n📊 可用数据集列表:")
            for dataset in get_dataset_list():
                print(dataset)

            dataset_index = input("\n请选择数据集编号: ")
            dataset_name = get_dataset_by_index(dataset_index)
            if not dataset_name:
                print("❌ 无效的数据集编号")
                return

            # 显示数据集使用建议
            print_dataset_tips(dataset_name)

            print("\n📈 可用策略模式:")
            print("1: 基础策略模式")
            print("2: 多因子组合模式")
            print("3: 高级合成策略模式")
            print("4: 动量策略模式")
            print("5: 价值策略模式")
            print("6: Alpha101模式")
            print("7: 组合型Alpha模式")
            
            print_strategy_mode_tips()

            strategy_mode = int(input("\n请选择策略模式 (1-7): "))
            if strategy_mode not in [1, 2, 3, 4, 5, 6, 7]:
                print("❌ 无效的策略模式")
                return

            # 如果选择优化策略模式，尝试加载历史结果
            previous_results = None
            print("\n🔍 尝试加载历史Alpha测试结果用于优化...")

            results = brain.simulate_alphas(None, strategy_mode, dataset_name, previous_results)

            if mode == 1:
                submit_alpha_ids(brain, 2)
                
        elif mode == 3:
            num_to_submit = int(input("\n请输入要提交的 Alpha 数量: "))
            if num_to_submit <= 0:
                print("❌ 无效的提交数量")
                return
            submit_alpha_ids(brain, num_to_submit)
            
        elif mode == 4:
            view_alpha_history()

    except Exception as e:
        print(f"❌ 程序运行出错: {str(e)}")


if __name__ == "__main__":
    main()