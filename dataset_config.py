"""数据集配置管理模块"""

DATASET_CONFIGS = {
    'fundamental6': {
        'id': 'fundamental6',
        'universe': 'TOP3000',
        'description': '基础财务数据 (稳健但信号偏弱)',
        'api_settings': {
            'instrumentType': 'EQUITY',
            'region': 'USA',
            'delay': 1,
            'decay': 0,
            'neutralization': 'SUBINDUSTRY',
            'truncation': 0.08,
            'pasteurization': 'ON',
            'unitHandling': 'VERIFY',
            'nanHandling': 'ON',
            'language': 'FASTEXPR'
        },
        'fields': [
            'assets', 'liabilities', 'revenue', 'netincome',
            'cash', 'debt', 'equity', 'eps', 'pe_ratio',
            'pb_ratio', 'market_cap', 'dividend_yield'
        ]
    },
    'analyst4': {
        'id': 'analyst4',
        'universe': 'TOP1000',
        'description': '分析师预测数据 (高IC但易过拟合)',
        'api_settings': {
            'instrumentType': 'EQUITY',
            'region': 'USA',
            'delay': 1,
            'decay': 0,
            'neutralization': 'SUBINDUSTRY',
            'truncation': 0.08,
            'pasteurization': 'ON',
            'unitHandling': 'VERIFY',
            'nanHandling': 'ON',
            'language': 'FASTEXPR'
        },
        'fields': [
            'anl4_tbvps_low', 'anl4_tbvps_high',
            'anl4_tbvps_mean', 'anl4_tbvps_median'
        ]
    },
    'pv1': {
        'id': 'pv1',
        'universe': 'TOP1000',
        'description': '股市成交量数据 (噪声大，不建议单独使用)',
        'api_settings': {
            'instrumentType': 'EQUITY',
            'region': 'USA',
            'delay': 1,
            'decay': 0,
            'neutralization': 'SUBINDUSTRY',
            'truncation': 0.08,
            'pasteurization': 'ON',
            'unitHandling': 'VERIFY',
            'nanHandling': 'ON',
            'language': 'FASTEXPR'
        },
        'fields': [
            'volume', 'close', 'open', 'high', 'low',
            'vwap', 'returns', 'turnover', 'volatility'
        ]
    },
    # 添加混合数据集支持
    'mixed_pv_fund': {
        'id': 'mixed',
        'universe': 'TOP3000',
        'description': '混合数据集(价量+基本面) → 合格率显著提高',
        'api_settings': {
            'instrumentType': 'EQUITY',
            'region': 'USA',
            'delay': 1,
            'decay': 0,
            'neutralization': 'SUBINDUSTRY',
            'truncation': 0.08,
            'pasteurization': 'ON',
            'unitHandling': 'VERIFY',
            'nanHandling': 'ON',
            'language': 'FASTEXPR'
        },
        'fields': [
            # 价量数据
            'volume', 'close', 'open', 'high', 'low',
            'vwap', 'returns', 'turnover', 'volatility',
            # 基本面数据
            'assets', 'liabilities', 'revenue', 'netincome',
            'cash', 'debt', 'equity', 'eps', 'pe_ratio',
            'pb_ratio', 'market_cap', 'dividend_yield'
        ]
    },
    'mixed_analyst_fund': {
        'id': 'mixed',
        'universe': 'TOP1000',
        'description': '混合数据集(分析师+基本面) → 平衡IC和覆盖范围',
        'api_settings': {
            'instrumentType': 'EQUITY',
            'region': 'USA',
            'delay': 1,
            'decay': 0,
            'neutralization': 'SUBINDUSTRY',
            'truncation': 0.08,
            'pasteurization': 'ON',
            'unitHandling': 'VERIFY',
            'nanHandling': 'ON',
            'language': 'FASTEXPR'
        },
        'fields': [
            # 分析师数据
            'anl4_tbvps_low', 'anl4_tbvps_high',
            'anl4_tbvps_mean', 'anl4_tbvps_median',
            # 基本面数据
            'assets', 'liabilities', 'revenue', 'netincome',
            'cash', 'debt', 'equity', 'eps', 'pe_ratio',
            'pb_ratio', 'market_cap', 'dividend_yield'
        ]
    }
}


def get_dataset_list():
    """获取所有可用数据集列表"""

    return [
        f"{idx+1}: {name} ({config['universe']}) - {config['description']}"
        for idx, (name, config) in enumerate(DATASET_CONFIGS.items())
    ]


def get_dataset_config(dataset_name):
    """获取指定数据集的配置"""

    return DATASET_CONFIGS.get(dataset_name)


def get_dataset_by_index(index):
    """通过索引获取数据集名称"""

    try:
        return list(DATASET_CONFIGS.keys())[int(index)-1]
    except (IndexError, ValueError):
        return None


def get_dataset_fields(dataset_name):
    """获取指定数据集的字段列表"""

    config = DATASET_CONFIGS.get(dataset_name)
    return config['fields'] if config else []


def get_dataset_recommendation(dataset_name):
    """获取数据集使用建议"""
    
    recommendations = {
        'fundamental6': '稳健但信号偏弱，建议与其他数据集混合使用',
        'analyst4': '高IC但易过拟合，覆盖股票少，建议谨慎使用',
        'pv1': '噪声大，不建议单独使用',
        'mixed_pv_fund': '价量+基本面混合，合格率显著提高，推荐使用',
        'mixed_analyst_fund': '分析师+基本面混合，平衡IC和覆盖范围，推荐使用'
    }
    
    return recommendations.get(dataset_name, '无特殊建议')