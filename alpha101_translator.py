"""Alpha101因子库翻译成Brain语法模块"""

class Alpha101Translator:
    """将经典的Alpha101因子翻译为Brain语法"""
    
    @staticmethod
    def get_alpha101_strategies(datafields):
        """获取Alpha101因子策略"""
        strategies = []
        
        # 选择一些关键字段
        close = "close" 
        open_ = "open"
        high = "high"
        low = "low"
        volume = "volume"
        returns = "returns"
        
        # 动量类因子 (基于价格相对变化)
        strategies.extend([
            # 1日收益率
            "group_rank((close - delay(close, 1))/delay(close, 1), subindustry)",
            # 5日动量
            "group_rank(close/delay(close, 5), subindustry)",
            # 10日动量
            "group_rank(close/delay(close, 10), subindustry)",
            # 20日动量
            "group_rank(close/delay(close, 20), subindustry)",
            # 价格变化率
            "ts_rank((close/delay(close, 1) - 1)*100, 10)"
        ])
        
        # 均值回归类因子 (基于偏离均值)
        strategies.extend([
            # 价格偏离度
            "group_rank((close - ts_mean(close, 20))/ts_std_dev(close, 20), subindustry)",
            # 价格偏离长期均值
            "group_rank((close - ts_mean(close, 60))/ts_std_dev(close, 60), subindustry)",
            # 收盘价相对均值位置
            "(close - ts_min(close, 20))/(ts_max(close, 20) - ts_min(close, 20))",
            # 价格与移动平均的偏离
            "close/ts_mean(close, 20) - 1"
        ])
        
        # 成交量类因子 (基于成交量变化率)
        strategies.extend([
            # 成交量变化率
            "group_rank((volume - delay(volume, 1))/delay(volume, 1), subindustry)",
            # 成交量相对均值
            "group_rank(volume/ts_mean(volume, 20), subindustry)",
            # 成交量偏离度
            "group_rank((volume - ts_mean(volume, 20))/ts_std_dev(volume, 20), subindustry)",
            # 量价配合
            "ts_rank(volume/sharesout * (close - open)/open, 10)"
        ])
        
        # 波动率类因子 (基于高低价差)
        strategies.extend([
            # 真实波幅
            "ts_rank((high - low)/open, 10)",
            # 波动率相对历史水平
            "ts_std_dev(close, 10)/ts_mean(ts_std_dev(close, 10), 60)",
            # 价格波动性
            "ts_rank(ts_std_dev(close/delay(close, 1), 5), 10)",
            # 高低价差比率
            "(high - low)/ts_mean(high - low, 20)"
        ])
        
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
        
        # 使用实际数据字段的因子
        if datafields:
            for field in datafields[:3]:  # 只使用前3个字段避免过多
                strategies.extend([
                    # 基本动量
                    f"group_rank({field}/delay({field}, 5), subindustry)",
                    # 基本均值回归
                    f"group_rank(({field} - ts_mean({field}, 20))/ts_std_dev({field}, 20), subindustry)",
                    # 基本波动率
                    f"ts_rank(ts_std_dev({field}, 10), 10)",
                    # 组合因子
                    f"group_rank({field}/delay({field}, 5), subindustry) - ts_rank(ts_std_dev({field}, 10), 10)"
                ])
        
        return strategies

    @staticmethod
    def get_alpha158_strategies(datafields):
        """获取Alpha158因子策略"""
        strategies = []
        
        # 基于Alpha158的因子思想
        if datafields:
            for field in datafields[:3]:
                strategies.extend([
                    # 价格与成交量关系
                    f"ts_rank({field} * volume/sharesout, 10)",
                    # 价格变化加速度
                    f"ts_rank({field}/delay({field}, 1) - delay({field}/delay({field}, 1), 1), 10)",
                    # 价格相对强势
                    f"group_rank({field}/ts_mean({field}, 20), subindustry)",
                    # 价格波动性调整
                    f"({field} - ts_mean({field}, 20))/ts_std_dev({field}, 20) * ts_rank(volume, 10)"
                ])
        
        return strategies

    @staticmethod
    def get_fundamental_strategies(datafields):
        """获取基本面因子策略"""
        strategies = []
        
        # 基本面因子 (如PE、PB、ROE等)
        if datafields:
            for field in datafields:
                if field in ['pe_ratio', 'pb_ratio', 'market_cap', 'eps', 'dividend_yield', 'assets', 'liabilities', 'revenue', 'netincome']:
                    strategies.extend([
                        # 基本面价值因子
                        f"rank(1/{field})",
                        # 基本面动量因子
                        f"ts_rank({field}/delay({field}, 20), 10)",
                        # 基本面均值回归因子
                        f"({field} - ts_mean({field}, 252))/ts_std_dev({field}, 252)",
                        # 基本面与价量结合因子
                        f"group_rank({field}/cap, subindustry)"
                    ])
        
        return strategies