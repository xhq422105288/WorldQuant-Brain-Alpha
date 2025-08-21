"""Alpha 策略生成模块"""


class AlphaStrategy:
    def get_simulation_data(self, datafields, mode=1):
        """根据模式生成策略列表"""

        if mode == 1:
            return self.generate_basic_strategy(datafields)
        elif mode == 2:
            return self.generate_multi_factor_strategy(datafields)
        elif mode == 3:
            return self.generate_advanced_strategy(datafields)
        elif mode == 4:
            return self.generate_momentum_strategy(datafields)
        elif mode == 5:
            return self.generate_value_strategy(datafields)
        else:
            print("❌ 无效的策略模式")
            return []

    def generate_basic_strategy(self, datafields):
        """生成基础策略"""

        strategies = []
        for field in datafields:
            # 1. 日内策略
            strategies.extend([
                # 日内收益率
                "group_rank((close - open)/open, subindustry)",

                # 隔夜收益率
                "group_rank((open - delay(close, 1))/delay(close, 1), subindustry)",

                # 高低价差异
                "group_rank((high - low)/open, subindustry)",
                
                # 收益率动量
                "group_rank((close/delay(close, 5) - 1), subindustry)"
            ])

            # 2. 波动率策略
            strategies.extend([
                # 波动率偏度
                f"power(ts_std_dev(abs({field}), 30), 2) - power(ts_std_dev({field}, 30), 2)",

                # 波动率动态调整
                f"group_rank(std({field}, 20)/mean({field}, 20) * (1/cap), subindustry)",
                
                # 波动率期限结构
                f"ts_std_dev({field}, 10) / ts_std_dev({field}, 60) - 1"
            ])

            # 3. 成交量策略
            if field in ['volume', 'turnover', 'vwap']:
                strategies.extend([
                    # 成交量异常
                    "group_rank((volume/sharesout - mean(volume/sharesout, 20))/std(volume/sharesout, 20), subindustry)",

                    # 成交量趋势
                    "ts_corr(volume/sharesout, abs(returns), 10)",
                    
                    # 量价配合
                    f"group_rank(ts_corr({field}/sharesout, returns, 10), subindustry)"
                ])

            # 4. 市场微观结构
            strategies.extend([
                # 小单买卖压力
                f"group_neutralize(power(rank({field} - group_mean({field}, 1, subindustry)), 3), bucket(rank(cap), range='0,1,0.1'))",

                # 流动性压力
                f"group_rank(correlation({field}, volume/sharesout, 20), subindustry)",
                
                # 跨字段关系
                f"group_rank(ts_rank({field}/cap, 10), subindustry)"
            ])

            # 5. 条件触发策略
            strategies.extend([
                # 条件触发
                f"trade_when(ts_rank(ts_std_dev(returns, 10), 252) < 0.9, {field}, -1)",

                # 市场状态过滤
                f"trade_when(volume > mean(volume, 20), {field}, -1)",
                
                # 动态权重
                f"if_else(ts_rank({field}, 20) > 0.8, {field}, -{field})"
            ])

        return strategies

    def generate_multi_factor_strategy(self, datafields):
        """生成多因子组合策略"""

        strategies = []
        n = len(datafields)

        for i in range(0, n-1, 2):
            field1 = datafields[i]
            field2 = datafields[i+1]

            # 1. 回归中性化
            strategies.extend([
                f"regression_neut(vector_neut({field1}, {field2}), abs(ts_mean(returns, 252)/ts_std_dev(returns, 252)))",

                # 多重回归
                f"regression_neut(regression_neut({field1}, {field2}), ts_std_dev(returns, 30))",
                
                # 残差效应
                f"{field1} - regression({field1}, {field2})"
            ])

            # 2. 条件组合
            strategies.extend([
                # 条件选择
                f"if_else(rank({field1}) > 0.5, {field2}, -1 * {field2})",

                # 分组组合
                f"group_neutralize({field1} * {field2}, bucket(rank(cap), range='0.1,1,0.1'))",
                
                # 因子择时
                f"if_else(ts_corr({field1}, returns, 20) > 0, {field1}*{field2}, -{field1}*{field2})"
            ])

            # 3. 复杂信号
            strategies.extend([
                # 信号强度
                f"power(rank(group_neutralize(-ts_decay_exp_window(ts_sum(if_else({field1}-group_mean({field1},1,industry)-0.02>0,1,0)*ts_corr({field2},cap,5),3),50),industry)),2)",

                # 市场状态
                f"trade_when(ts_rank(ts_std_dev(returns,10),252)<0.9, {field1} * {field2}, -1)",
                
                # 因子动量
                f"ts_rank({field1}/{field2}, 10) * sign(ts_corr({field1}, returns, 5))"
            ])

        return strategies
        
    def generate_advanced_strategy(self, datafields):
        """生成高级策略"""
        
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
                f"group_neutralize({field}, subindustry) * (1 + ts_rank(volatility, 20))"
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
                f"ts_rank({f1}, 10) * ts_rank({f2}, 10) - ts_rank({f3}, 10)"
            ])
            
        return strategies
        
    def generate_momentum_strategy(self, datafields):
        """生成动量策略"""
        
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
                f"{field} - group_mean({field}, 1, sector)"
            ])
            
        return strategies
        
    def generate_value_strategy(self, datafields):
        """生成价值策略"""
        
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
                f"ts_rank(({field}/mean({field}, 252) - 1), 10)"
            ])
            
        return strategies