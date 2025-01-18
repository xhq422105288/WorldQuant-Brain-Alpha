"""数据集配置管理模块"""

DATASET_CONFIGS = {
    'fundamental6': {
        'id': 'fundamental6',
        'universe': 'TOP3000',
        'description': '基础财务数据',
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
        'description': '分析师预测数据',
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
        'description': '股市成交量数据',
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


def get_api_settings(dataset_name):
    """获取指定数据集的API设置"""

    config = DATASET_CONFIGS.get(dataset_name)
    if config and 'api_settings' in config:
        settings = config['api_settings'].copy()
        settings['universe'] = config['universe']
        return settings
    return None
