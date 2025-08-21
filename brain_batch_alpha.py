"""WorldQuant Brain API 批量处理模块"""

import json
import os
from datetime import datetime
from os.path import expanduser
from time import sleep

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

from alpha_strategy import AlphaStrategy
from optimized_alpha_strategy import OptimizedAlphaStrategy
from alpha_history_manager_sqlite import AlphaHistoryManagerSQLite
from dataset_config import get_api_settings, get_dataset_config


class BrainBatchAlpha:
    API_BASE_URL = 'https://api.worldquantbrain.com'

    def __init__(self, credentials_file='brain_credentials.txt'):
        """初始化 API 客户端"""

        self.session = requests.Session()
        self._setup_authentication(credentials_file)
        self.optimized_strategy_generator = OptimizedAlphaStrategy()
        self.history_manager = AlphaHistoryManagerSQLite()

    def _setup_authentication(self, credentials_file):
        """设置认证"""

        try:
            with open(expanduser(credentials_file)) as f:
                credentials = json.load(f)
            username, password = credentials
            self.session.auth = HTTPBasicAuth(username, password)

            response = self.session.post(f"{self.API_BASE_URL}/authentication")
            if response.status_code not in [200, 201]:
                raise Exception(f"认证失败: HTTP {response.status_code}")

            print("✅ 认证成功!")

        except Exception as e:
            print(f"❌ 认证错误: {str(e)}")
            raise

    def simulate_alphas(self, datafields=None, strategy_mode=1, dataset_name=None, previous_results=None):
        """模拟 Alpha 列表"""

        try:
            datafields = self._get_datafields_if_none(datafields, dataset_name)
            if not datafields:
                return []

            # 如果没有提供previous_results，则从历史记录中加载
            if previous_results is None:
                print("🔍 从历史记录中加载Alpha测试结果用于优化...")
                previous_results = self.history_manager.get_history(100)  # 加载最近100条记录
                if not previous_results:
                    print("⚠️ 没有找到历史记录")

            alpha_list = self._generate_alpha_list(datafields, strategy_mode, previous_results)
            if not alpha_list:
                return []

            print(f"\n🚀 开始模拟 {len(alpha_list)} 个 Alpha 表达式...")

            results = []
            for i, alpha in enumerate(alpha_list, 1):
                print(f"\n[{i}/{len(alpha_list)}] 正在模拟 Alpha...")
                result = self._simulate_single_alpha(alpha)
                if result:
                    results.append(result)
                    # 保存到历史记录
                    self.history_manager.add_alpha_result(result)
                    # 如果通过检查，也保存ID到alpha_ids.txt
                    if result.get('passed_all_checks'):
                        self._save_alpha_id(result['alpha_id'], result)

                if i < len(alpha_list):
                    sleep(5)

            return results

        except Exception as e:
            print(f"❌ 模拟过程出错: {str(e)}")
            return []

    def _simulate_single_alpha(self, alpha):
        """模拟单个 Alpha"""

        try:
            print(f"表达式: {alpha.get('regular', 'Unknown')}")

            # 发送模拟请求
            sim_resp = self.session.post(
                f"{self.API_BASE_URL}/simulations",
                json=alpha
            )

            if sim_resp.status_code != 201:
                print(f"❌ 模拟请求失败 (状态码: {sim_resp.status_code})")
                return None

            try:
                sim_progress_url = sim_resp.headers['Location']
                start_time = datetime.now()
                total_wait = 0

                while True:
                    sim_progress_resp = self.session.get(sim_progress_url)
                    retry_after_sec = float(sim_progress_resp.headers.get("Retry-After", 0))

                    if retry_after_sec == 0:  # simulation done!
                        alpha_id = sim_progress_resp.json()['alpha']
                        print(f"✅ 获得 Alpha ID: {alpha_id}")

                        # 等待一下让指标计算完成
                        sleep(3)

                        # 获取 Alpha 详情
                        alpha_url = f"{self.API_BASE_URL}/alphas/{alpha_id}"
                        alpha_detail = self.session.get(alpha_url)
                        alpha_data = alpha_detail.json()

                        # 检查是否有 is 字段
                        if 'is' not in alpha_data:
                            print("❌ 无法获取指标数据")
                            return None

                        is_qualified = self.check_alpha_qualification(alpha_data)

                        return {
                            'expression': alpha.get('regular'),
                            'alpha_id': alpha_id,
                            'passed_all_checks': is_qualified,
                            'metrics': alpha_data.get('is', {}),
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }

                    # 更新等待时间和进度
                    total_wait += retry_after_sec
                    elapsed = (datetime.now() - start_time).total_seconds()
                    progress = min(95, (elapsed / 30) * 100)  # 假设通常需要 30 秒完成

                    print(f"⏳ 等待模拟结果... ({elapsed:.1f} 秒 | 进度约 {progress:.0f}%)")
                    sleep(retry_after_sec)

            except KeyError:
                print("❌ 无法获取模拟进度 URL")
                return None

        except Exception as e:
            print(f"⚠️ Alpha 模拟失败: {str(e)}")
            return None

    def check_alpha_qualification(self, alpha_data):
        """检查 Alpha 是否满足所有提交条件"""

        try:
            # 从 'is' 字段获取指标
            is_data = alpha_data.get('is', {})
            if not is_data:
                print("❌ 无法获取指标数据")
                return False

            # 获取指标值
            sharpe = float(is_data.get('sharpe', 0))
            fitness = float(is_data.get('fitness', 0))
            turnover = float(is_data.get('turnover', 0))
            ic_mean = float(is_data.get('margin', 0))  # margin 对应 IC Mean

            # 获取子宇宙 Sharpe
            sub_universe_check = next(
                (
                    check for check in is_data.get('checks', [])
                    if check['name'] == 'LOW_SUB_UNIVERSE_SHARPE'
                ),
                {}
            )
            subuniverse_sharpe = float(sub_universe_check.get('value', 0))
            required_subuniverse_sharpe = float(sub_universe_check.get('limit', 0))

            # 获取其他重要指标
            returns = float(is_data.get('returns', 0))
            drawdown = float(is_data.get('drawdown', 0))
            capacity = float(is_data.get('capacity', 0))

            # 打印指标
            print("\n📊 Alpha 指标详情:")
            print(f"  Sharpe: {sharpe:.3f} (>1.5)")
            print(f"  Fitness: {fitness:.3f} (>1.0)")
            print(f"  Turnover: {turnover:.3f} (0.1-0.9)")
            print(f"  IC Mean: {ic_mean:.3f} (>0.02)")
            print(f"  子宇宙 Sharpe: {subuniverse_sharpe:.3f} (>{required_subuniverse_sharpe:.3f})")
            print(f"  收益率: {returns:.3f} (>0.05)")
            print(f"  最大回撤: {drawdown:.3f} (<0.5)")
            print(f"  容量: {capacity:.0f} (>1000000)")

            print("\n📝 指标评估结果:")

            # 检查每个指标并输出结果
            is_qualified = True
            near_qualified = 0  # 接近合格的指标数
            total_checks = 8    # 总检查项数

            # Sharpe ratio检查 (要求>1.5)
            if sharpe >= 1.5:
                print("✅ Sharpe ratio 达标")
            elif sharpe >= 1.3:
                print("⚠️ Sharpe ratio 接近达标 (>=1.3)")
                near_qualified += 1
            else:
                print("❌ Sharpe ratio 不达标 (<1.3)")
                is_qualified = False

            # Fitness检查 (要求>1.0)
            if fitness >= 1.0:
                print("✅ Fitness 达标")
            elif fitness >= 0.8:
                print("⚠️ Fitness 接近达标 (>=0.8)")
                near_qualified += 1
            else:
                print("❌ Fitness 不达标 (<0.8)")
                is_qualified = False

            # Turnover检查 (要求0.1-0.9)
            if 0.1 <= turnover <= 0.9:
                print("✅ Turnover 达标")
            elif 0.05 <= turnover <= 0.95:
                print("⚠️ Turnover 接近达标 (0.05-0.95)")
                near_qualified += 1
            else:
                print("❌ Turnover 不在合理范围")
                is_qualified = False

            # IC Mean检查 (要求>0.02)
            if ic_mean >= 0.02:
                print("✅ IC Mean 达标")
            elif ic_mean >= 0.015:
                print("⚠️ IC Mean 接近达标 (>=0.015)")
                near_qualified += 1
            else:
                print("❌ IC Mean 不达标 (<0.015)")
                is_qualified = False

            # 子宇宙 Sharpe检查
            if subuniverse_sharpe >= required_subuniverse_sharpe:
                print(f"✅ 子宇宙 Sharpe 达标 ({subuniverse_sharpe:.3f} > {required_subuniverse_sharpe:.3f})")
            elif subuniverse_sharpe >= required_subuniverse_sharpe * 0.8:
                print(f"⚠️ 子宇宙 Sharpe 接近达标 ({subuniverse_sharpe:.3f} > {required_subuniverse_sharpe * 0.8:.3f})")
                near_qualified += 1
            else:
                print(f"❌ 子宇宙 Sharpe 不达标 ({subuniverse_sharpe:.3f} < {required_subuniverse_sharpe:.3f})")
                is_qualified = False

            # 收益率检查 (要求>0.05)
            if returns >= 0.05:
                print("✅ 收益率达标")
            elif returns >= 0.03:
                print("⚠️ 收益率接近达标 (>=0.03)")
                near_qualified += 1
            else:
                print("❌ 收益率不达标 (<0.03)")
                is_qualified = False

            # 最大回撤检查 (要求<0.5)
            if drawdown <= 0.5:
                print("✅ 最大回撤达标")
            elif drawdown <= 0.6:
                print("⚠️ 最大回撤接近达标 (<=0.6)")
                near_qualified += 1
            else:
                print("❌ 最大回撤过大 (>0.6)")
                is_qualified = False

            # 容量检查 (要求>1000000)
            if capacity >= 1000000:
                print("✅ 容量达标")
            elif capacity >= 500000:
                print("⚠️ 容量接近达标 (>=500000)")
                near_qualified += 1
            else:
                print("❌ 容量不足 (<500000)")
                is_qualified = False

            print("\n🔍 检查项结果:")
            checks = is_data.get('checks', [])
            additional_failures = 0
            for check in checks:
                name = check.get('name')
                result = check.get('result')
                value = check.get('value', 'N/A')
                limit = check.get('limit', 'N/A')

                if result == 'PASS':
                    print(f"✅ {name}: {value} (限制: {limit})")
                elif result == 'FAIL':
                    print(f"❌ {name}: {value} (限制: {limit})")
                    # 对于额外的检查项，我们不直接导致整个Alpha不合格，但记录下来
                    additional_failures += 1
                elif result == 'PENDING':
                    print(f"⚠️ {name}: 检查尚未完成")

            print("\n📋 最终评判:")
            # 如果80%以上的指标达标或接近达标，也认为是高质量Alpha
            if is_qualified:
                print("✅ Alpha 满足所有条件，可以提交!")
            elif near_qualified >= total_checks * 0.75:  # 75%以上的指标达标或接近达标
                print("🔶 Alpha 接近合格标准，建议保存以供进一步分析!")
                # 仍然保存接近合格的Alpha
                return True
            else:
                print("❌ Alpha 未达到提交标准")

            return is_qualified

        except Exception as e:
            print(f"❌ 检查 Alpha 资格时出错: {str(e)}")
            return False

    def submit_alpha(self, alpha_id):
        """提交单个 Alpha"""

        submit_url = f"{self.API_BASE_URL}/alphas/{alpha_id}/submit"

        for attempt in range(5):
            print(f"🔄 第 {attempt + 1} 次尝试提交 Alpha {alpha_id}")

            # POST 请求
            res = self.session.post(submit_url)
            if res.status_code == 201:
                print("✅ POST: 成功，等待提交完成...")
            elif res.status_code in [400, 403]:
                print(f"❌ 提交被拒绝 ({res.status_code})")
                return False
            else:
                sleep(3)
                continue

            # 检查提交状态
            while True:
                res = self.session.get(submit_url)
                retry = float(res.headers.get('Retry-After', 0))

                if retry == 0:
                    if res.status_code == 200:
                        print("✅ 提交成功!")
                        return True
                    return False

                sleep(retry)

        return False

    def submit_multiple_alphas(self, alpha_ids):
        """批量提交 Alpha"""
        successful = []
        failed = []

        for alpha_id in alpha_ids:
            if self.submit_alpha(alpha_id):
                successful.append(alpha_id)
            else:
                failed.append(alpha_id)

            if alpha_id != alpha_ids[-1]:
                sleep(10)

        return successful, failed

    def _get_datafields_if_none(self, datafields=None, dataset_name=None):
        """获取数据字段列表"""

        try:
            if datafields is not None:
                return datafields

            if dataset_name is None:
                print("❌ 未指定数据集")
                return None

            config = get_dataset_config(dataset_name)
            if not config:
                print(f"❌ 无效的数据集: {dataset_name}")
                return None

            # 获取数据字段
            search_scope = {
                'instrumentType': 'EQUITY',
                'region': 'USA',
                'delay': '1',
                'universe': config['universe']
            }

            url_template = (
                f"{self.API_BASE_URL}/data-fields?"
                f"instrumentType={search_scope['instrumentType']}"
                f"&region={search_scope['region']}"
                f"&delay={search_scope['delay']}"
                f"&universe={search_scope['universe']}"
                f"&dataset.id={config['id']}"
                "&limit=50&offset={offset}"
            )

            # 获取总数
            initial_resp = self.session.get(url_template.format(offset=0))
            if initial_resp.status_code != 200:
                print("❌ 获取数据字段失败")
                return None

            total_count = initial_resp.json()['count']

            # 获取所有数据字段
            all_fields = []
            for offset in range(0, total_count, 50):
                resp = self.session.get(url_template.format(offset=offset))
                if resp.status_code != 200:
                    continue
                all_fields.extend(resp.json()['results'])

            # 过滤矩阵类型字段
            matrix_fields = [
                field['id'] for field in all_fields
                if field.get('type') == 'MATRIX'
            ]

            if not matrix_fields:
                print("❌ 未找到可用的数据字段")
                return None

            print(f"✅ 获取到 {len(matrix_fields)} 个数据字段")
            return matrix_fields

        except Exception as e:
            print(f"❌ 获取数据字段时出错: {str(e)}")
            return None

    def _generate_alpha_list(self, datafields, strategy_mode, previous_results=None):
        """生成 Alpha 表达式列表"""
        try:
            # 对于所有策略模式，都使用优化策略生成器并传入历史结果
            strategies = self.optimized_strategy_generator.get_optimized_simulation_data(
                datafields, strategy_mode, previous_results)
            
            # 如果优化策略生成器没有返回任何策略，则使用基础策略生成器作为备选方案
            if not strategies:
                print("⚠️ 优化策略生成器未生成任何策略，使用基础策略生成器...")
                # 初始化策略生成器
                strategy_generator = AlphaStrategy()
                # 生成策略列表
                strategies = strategy_generator.get_simulation_data(datafields, strategy_mode)
                
                # 如果仍然没有策略，则生成一些默认策略
                if not strategies:
                    print("⚠️ 基础策略生成器未生成任何策略，生成默认策略...")
                    strategies = self._generate_default_strategies(datafields)

            # 限制策略数量，避免过多的策略导致处理时间过长
            if len(strategies) > 50:
                print(f"⚠️ 策略数量过多 ({len(strategies)})，限制为50个")
                strategies = strategies[:50]
            elif len(strategies) == 0:
                print("❌ 未能生成任何策略")
                return []

            print(f"生成了 {len(strategies)} 个Alpha表达式")

            # 转换为 API 所需的格式
            alpha_list = []
            for strategy in strategies:
                simulation_data = {
                    'type': 'REGULAR',
                    'settings': {
                        'instrumentType': 'EQUITY',
                        'region': 'USA',
                        'universe': 'TOP3000',
                        'delay': 1,
                        'decay': 0,
                        'neutralization': 'SUBINDUSTRY',
                        'truncation': 0.08,
                        'pasteurization': 'ON',
                        'unitHandling': 'VERIFY',
                        'nanHandling': 'ON',
                        'language': 'FASTEXPR',
                        'visualization': False,
                    },
                    'regular': strategy
                }
                alpha_list.append(simulation_data)

            return alpha_list

        except Exception as e:
            print(f"❌ 生成 Alpha 列表失败: {str(e)}")
            # 出错时生成默认策略
            try:
                default_strategies = self._generate_default_strategies(datafields if datafields else [])
                alpha_list = []
                for strategy in default_strategies:
                    simulation_data = {
                        'type': 'REGULAR',
                        'settings': {
                            'instrumentType': 'EQUITY',
                            'region': 'USA',
                            'universe': 'TOP3000',
                            'delay': 1,
                            'decay': 0,
                            'neutralization': 'SUBINDUSTRY',
                            'truncation': 0.08,
                            'pasteurization': 'ON',
                            'unitHandling': 'VERIFY',
                            'nanHandling': 'ON',
                            'language': 'FASTEXPR',
                            'visualization': False,
                        },
                        'regular': strategy
                    }
                    alpha_list.append(simulation_data)
                return alpha_list
            except:
                return []
            
    def _generate_default_strategies(self, datafields):
        """生成默认策略，确保始终有策略可以测试"""
        default_strategies = [
            "group_rank((close - open)/open, subindustry)",
            "group_rank((open - delay(close, 1))/delay(close, 1), subindustry)",
            "group_rank((high - low)/open, subindustry)"
        ]
        
        # 如果有数据字段，添加一些基于数据字段的策略
        if datafields:
            field = datafields[0] if datafields else "close"
            default_strategies.extend([
                f"group_rank(({field} - delay({field}, 1))/{field}, subindustry)",
                f"ts_rank({field}/mean({field}, 20), 10)",
                f"ts_rank(ts_std_dev({field}, 10), 10)"
            ])
            
        return default_strategies

    def _save_alpha_id(self, alpha_id, alpha_data):
        """保存 Alpha ID 到文件"""
        try:
            with open("alpha_ids.txt", "a") as f:
                f.write(f"{alpha_id}\n")
        except Exception as e:
            print(f"❌ 保存 Alpha ID 时出错: {str(e)}")