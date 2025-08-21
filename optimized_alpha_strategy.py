"""优化Alpha策略生成模块 - 基于历史Alpha质量反馈进行策略优化"""

from alpha101_translator import Alpha101Translator


class OptimizedAlphaStrategy:
    def __init__(self):
        """初始化优化策略生成器"""
        # 存储历史策略表现数据
        self.strategy_performance = {}
        
    def update_strategy_performance(self, strategy_expr, metrics):
        """更新策略表现数据"""
        self.strategy_performance[strategy_expr] = metrics
        
    def get_optimized_simulation_data(self, datafields, mode=1, previous_results=None):
        """根据历史表现优化生成策略列表"""
        
        # 即使没有历史结果也使用优化生成器
        if previous_results and len(previous_results) > 0:
            # 根据历史结果优化策略
            return self.generate_optimized_strategy(datafields, previous_results)
        else:
            # 首次生成策略，但仍使用优化方法
            strategies = self.generate_initial_optimized_strategy(datafields, mode)
            # 确保至少生成一些策略
            if not strategies:
                strategies = self.generate_basic_optimized_strategy(datafields)
            return strategies
            
    def generate_initial_optimized_strategy(self, datafields, mode=1):
        """首次生成优化策略"""
        if mode == 1:
            return self.generate_basic_optimized_strategy(datafields)
        elif mode == 2:
            return self.generate_multi_factor_optimized_strategy(datafields)
        elif mode == 3:
            return self.generate_advanced_optimized_strategy(datafields)
        elif mode == 4:
            return self.generate_momentum_optimized_strategy(datafields)
        elif mode == 5:
            return self.generate_value_optimized_strategy(datafields)
        elif mode == 6:  # 新增Alpha101模式
            return self.generate_alpha101_strategy(datafields)
        elif mode == 7:  # 新增组合型Alpha模式
            return self.generate_combined_alpha_strategy(datafields)
        else:
            print("❌ 无效的策略模式")
            return []

    def generate_optimized_strategy(self, datafields, previous_results):
        """基于历史结果优化生成策略"""
        strategies = []
        
        # 分析历史结果，找出表现好的因子组合
        good_strategies = [result for result in previous_results if result.get('passed_all_checks', False)]
        failed_strategies = [result for result in previous_results if not result.get('passed_all_checks', True)]
        
        # 如果有表现好的策略，增加类似策略的权重
        if good_strategies:
            for result in good_strategies:
                expr = result.get('expression', '')
                metrics = result.get('metrics', {})
                
                # 保存策略表现数据
                self.update_strategy_performance(expr, metrics)
                
                # 基于优秀策略生成变体
                variants = self.generate_variants(expr, datafields)
                strategies.extend(variants)
        
        # 如果大多数策略失败，尝试不同的策略类型
        if len(failed_strategies) > len(good_strategies):
            # 添加更多创新性策略
            strategies.extend(self.generate_innovative_strategies(datafields))
        
        # 添加一些全新的策略尝试
        strategies.extend(self.generate_exploration_strategies(datafields))
        
        # 添加Alpha101经典因子
        strategies.extend(Alpha101Translator.get_alpha101_strategies(datafields))
        
        # 添加组合型Alpha
        strategies.extend(self.generate_combined_alpha_strategy(datafields))
        
        # 如果没有生成足够的策略，使用初始策略补充
        if len(strategies) < 5:  # 至少生成5个策略
            strategies.extend(self.generate_basic_optimized_strategy(datafields))
            
        # 确保至少有一些策略
        if not strategies:
            strategies = self.generate_basic_optimized_strategy(datafields)
            
        return strategies

    def generate_variants(self, base_expr, datafields):
        """基于基础表达式生成变体"""
        variants = []
        
        # 简单变体（调整参数）
        # 例如，如果原表达式有ts_rank(..., 10)，生成ts_rank(..., 5)和ts_rank(..., 20)
        if 'ts_rank(' in base_expr and ', 10)' in base_expr:
            variants.append(base_expr.replace(', 10)', ', 5)'))
            variants.append(base_expr.replace(', 10)', ', 20)'))
            
        if 'ts_zscore(' in base_expr and ', 10)' in base_expr:
            variants.append(base_expr.replace(', 10)', ', 5)'))
            variants.append(base_expr.replace(', 10)', ', 20)'))
            
        # 添加更多基于历史优秀表现的变体策略
        for field in datafields[:3]:  # 只使用前几个字段避免过多
            # 基于原始表达式的字段替换
            if 'close' in base_expr:
                variants.append(base_expr.replace('close', field))
            elif 'volume' in base_expr:
                variants.append(base_expr.replace('volume', field))
                
        return variants

    def generate_innovative_strategies(self, datafields):
        """生成创新性策略（当多数策略失败时使用）"""
        strategies = []
        
        # 使用更多非线性组合
        for i in range(min(3, len(datafields))):
            field = datafields[i]
            strategies.extend([
                f"ts_rank(power({field}/mean({field}, 10), 2), 10)",
                f"sign({field}) * log(abs({field} + 1))",
                f"ts_rank({field}, 5) * (1 + ts_rank(volatility, 10))",
                f"rank({field}) * ts_rank(turnover, 10)"
            ])
            
        # 尝试更多复杂的多因子组合
        if len(datafields) >= 2:
            f1, f2 = datafields[0], datafields[1]
            strategies.extend([
                f"ts_rank({f1}/{f2}, 10) * sign(ts_corr({f1}, returns, 10))",
                f"group_neutralize(power({f1}, 2), subindustry) / group_mean({f2}, 1, subindustry)",
                f"if_else(ts_rank({f1}, 10) > 0.8, {f2}, -{f2})"
            ])
            
        return strategies

    def generate_exploration_strategies(self, datafields):
        """生成探索性策略（用于发现新的有效因子组合）"""
        strategies = []
        
        # 时间序列的创新组合
        for field in datafields[:2]:
            strategies.extend([
                f"ts_rank({field} - delay({field}, 10), 5)",
                f"ts_rank({field}/delay({field}, 1) - 1, 10)",
                f"ts_rank(ts_std_dev({field}, 10) / mean({field}, 10), 10)",
                f"zscore(ts_rank({field}, 10)) * zscore(ts_rank(volume, 10))"
            ])
            
        # 跨字段创新组合
        if len(datafields) >= 3:
            f1, f2, f3 = datafields[0], datafields[1], datafields[2]
            strategies.extend([
                f"({f1} * {f2}) / ({f3} + 1)",
                f"ts_rank({f1}, 10) + ts_rank({f2}, 10) - 2 * ts_rank({f3}, 10)",
                f"sign(ts_corr({f1}, {f2}, 20)) * ts_rank({f3}, 10)"
            ])
            
        return strategies

    def generate_basic_optimized_strategy(self, datafields):
        """生成基础优化策略"""
        strategies = []
        for field in datafields:
            # 基础价格因子
            strategies.extend([
                "group_rank((close - open)/open, subindustry)",
                "group_rank((open - delay(close, 1))/delay(close, 1), subindustry)",
                "group_rank((high - low)/open, subindustry)",
                "group_rank((close/delay(close, 5) - 1), subindustry)"
            ])

            # 波动率和风险调整因子
            strategies.extend([
                f"power(ts_std_dev(abs({field}), 30), 2) - power(ts_std_dev({field}, 30), 2)",
                f"group_rank(std({field}, 20)/mean({field}, 20) * (1/cap), subindustry)",
                f"ts_std_dev({field}, 10) / ts_std_dev({field}, 60) - 1",
                f"zscore({field}) / ts_std_dev({field}, 20)"
            ])

            # 成交量相关因子
            if field in ['volume', 'turnover', 'vwap']:
                strategies.extend([
                    "group_rank((volume/sharesout - mean(volume/sharesout, 20))/std(volume/sharesout, 20), subindustry)",
                    "ts_corr(volume/sharesout, abs(returns), 10)",
                    f"group_rank(ts_corr({field}/sharesout, returns, 10), subindustry)",
                    f"ts_rank({field}/mean({field}, 20), 10) - 1"
                ])

            # 市场微观结构因子
            strategies.extend([
                f"group_neutralize(power(rank({field} - group_mean({field}, 1, subindustry)), 3), bucket(rank(cap), range='0,1,0.1'))",
                f"group_rank(correlation({field}, volume/sharesout, 20), subindustry)",
                f"group_rank(ts_rank({field}/cap, 10), subindustry)",
                f"rank({field}) * (1/ts_rank(cap, 10))"
            ])

            # 条件触发因子
            strategies.extend([
                f"trade_when(ts_rank(ts_std_dev(returns, 10), 252) < 0.9, {field}, -1)",
                f"trade_when(volume > mean(volume, 20), {field}, -1)",
                f"if_else(ts_rank({field}, 20) > 0.8, {field}, -{field})",
                f"if_else(ts_rank({field}, 5) > 0.9, -1, 1) * {field}"
            ])

        return strategies

    def generate_multi_factor_optimized_strategy(self, datafields):
        """生成优化的多因子组合策略"""
        strategies = []
        n = len(datafields)

        for i in range(0, n-1, 2):
            field1 = datafields[i]
            field2 = datafields[i+1]

            # 回归中性化策略
            strategies.extend([
                f"regression_neut(vector_neut({field1}, {field2}), abs(ts_mean(returns, 252)/ts_std_dev(returns, 252)))",
                f"regression_neut(regression_neut({field1}, {field2}), ts_std_dev(returns, 30))",
                f"{field1} - regression({field1}, {field2})",
                f"regression_neut({field1}, {field2}) / ts_std_dev({field2}, 20)"
            ])

            # 条件组合策略
            strategies.extend([
                f"if_else(rank({field1}) > 0.5, {field2}, -1 * {field2})",
                f"group_neutralize({field1} * {field2}, bucket(rank(cap), range='0.1,1,0.1'))",
                f"if_else(ts_corr({field1}, returns, 20) > 0, {field1}*{field2}, -{field1}*{field2})",
                f"sign(ts_corr({field1}, {field2}, 20)) * ({field1} + {field2})"
            ])

            # 复杂信号策略
            strategies.extend([
                f"power(rank(group_neutralize(-ts_decay_exp_window(ts_sum(if_else({field1}-group_mean({field1},1,industry)-0.02>0,1,0)*ts_corr({field2},cap,5),3),50),industry)),2)",
                f"trade_when(ts_rank(ts_std_dev(returns,10),252)<0.9, {field1} * {field2}, -1)",
                f"ts_rank({field1}/{field2}, 10) * sign(ts_corr({field1}, returns, 5))",
                f"ts_rank({field1}, 10) * ts_rank({field2}, 10) * sign(ts_corr({field1}, {field2}, 10))"
            ])

        return strategies

    def generate_advanced_optimized_strategy(self, datafields):
        """生成高级优化策略"""
        strategies = []
        n = len(datafields)
        
        # 多维度因子合成
        for i in range(min(5, n)):
            field = datafields[i]
            strategies.extend([
                # 多时间尺度融合
                f"0.5 * ts_zscore({field}, 10) + 0.3 * ts_zscore({field}, 20) + 0.2 * ts_zscore({field}, 60)",
                
                # 非线性变换
                f"ts_rank(power({field}/mean({field}, 20) - 1, 2), 10)",
                
                # 分位数调整
                f"rank({field}) - 0.5",
                
                # 动态中性化
                f"group_neutralize({field}, subindustry) * (1 + ts_rank(volatility, 20))",
                
                # 创新性组合
                f"ts_rank(log(abs({field} + 1)), 10)"
            ])
            
        # 多因子组合
        if n >= 3:
            f1, f2, f3 = datafields[0], datafields[1], datafields[2]
            strategies.extend([
                # 三因子交互
                f"({f1} - mean({f1}, 20)) * ({f2} - mean({f2}, 20)) / std({f3}, 20)",
                
                # 因子择时模型
                f"if_else(ts_corr({f1}, returns, 10) > ts_corr({f2}, returns, 10), {f1}, {f2})",
                
                # 动态权重组合
                f"ts_rank({f1}, 10) * ts_rank({f2}, 10) - ts_rank({f3}, 10)",
                
                # 创新性三因子组合
                f"sign(ts_corr({f1}, {f2}, 20)) * ts_rank({f3}, 10)"
            ])
            
        return strategies
        
    def generate_momentum_optimized_strategy(self, datafields):
        """生成优化的动量策略"""
        
        strategies = []
        for field in datafields:
            strategies.extend([
                # 不同周期动量
                f"ts_rank({field}/delay({field}, 5), 10)",
                f"ts_rank({field}/delay({field}, 20), 5)",
                f"ts_rank({field}/delay({field}, 60), 3)",
                
                # 动量反转组合
                f"if_else(ts_rank({field}, 20) > 0.9, -{field}, {field})",
                
                # 动量加速
                f"ts_rank({field}/delay({field}, 5) - delay({field}/delay({field}, 5), 5), 10)",
                
                # 交叉资产动量
                f"{field} - group_mean({field}, 1, sector)",
                
                # 优化的动量因子
                f"ts_rank({field}/delay({field}, 1) - 1, 10) * sign(ts_rank(returns, 10))"
            ])
            
        return strategies
        
    def generate_value_optimized_strategy(self, datafields):
        """生成优化的价值策略"""
        
        strategies = []
        for field in datafields:
            strategies.extend([
                # 价值因子标准化
                f"rank({field}/cap)",
                f"ts_rank({field}/bookvalue, 20)",
                
                # 价值动量结合
                f"if_else(rank({field}) < 0.3, ts_rank(returns, 10), -ts_rank(returns, 10))",
                
                # 相对价值
                f"({field} - group_mean({field}, 1, industry)) / group_std_dev({field}, 1, industry)",
                
                # 价值回归
                f"ts_rank(({field}/mean({field}, 252) - 1), 10)",
                
                # 优化的价值因子
                f"rank({field}) * (1/ts_rank(cap, 10)) * sign(ts_rank(returns, 20))"
            ])
            
        return strategies
        
    def generate_alpha101_strategy(self, datafields):
        """生成Alpha101策略"""
        return Alpha101Translator.get_alpha101_strategies(datafields)
        
    def generate_combined_alpha_strategy(self, datafields):
        """生成组合型Alpha策略"""
        strategies = []
        
        # 组合型Alpha (多个信号组合)
        strategies.extend([
            # 动量与波动率组合
            "group_rank(close/delay(close, 5), subindustry) - group_rank(ts_std_dev(returns, 10), subindustry)",
            # 价格位置与成交量组合
            "((close - ts_min(close, 20))/(ts_max(close, 20) - ts_min(close, 20))) * ts_rank(volume, 10)",
            # 均值回归与动量组合
            "group_rank((close - ts_mean(close, 20))/ts_std_dev(close, 20), subindustry) - group_rank(close/delay(close, 10), subindustry)",
            # 价格与成交量相关性
            "ts_rank(ts_corr(close, volume/sharesout, 10), 10)"
        ])
        
        # 使用实际数据字段的组合因子
        if datafields and len(datafields) >= 2:
            f1, f2 = datafields[0], datafields[1]
            strategies.extend([
                # 基本组合因子
                f"rank(ts_corr({f1}, {f2}, 10)) - rank(ts_delta({f1}, 10))",
                f"ts_rank({f1}, 10) - ts_rank({f2}, 10)",
                f"group_rank({f1}, subindustry) * ts_rank({f2}/ts_mean({f2}, 20), 10)",
                f"ts_rank(ts_std_dev({f1}, 10), 10) + ts_rank(ts_std_dev({f2}, 10), 10)"
            ])
            
        return strategies