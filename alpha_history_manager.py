"""Alpha 历史记录管理模块"""

import json
import os
from datetime import datetime


class AlphaHistoryManager:
    def __init__(self, history_file="alpha_history.json"):
        """初始化历史记录管理器"""
        self.history_file = history_file
        self.history_data = self.load_history()
        
    def load_history(self):
        """加载历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            print(f"⚠️ 加载历史记录时出错: {str(e)}")
            return []
            
    def save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
            print("✅ Alpha 历史记录保存成功")
        except Exception as e:
            print(f"❌ 保存历史记录时出错: {str(e)}")
            
    def add_alpha_result(self, alpha_result):
        """添加 Alpha 测试结果到历史记录"""
        # 添加时间戳
        alpha_result['saved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 添加到历史记录
        self.history_data.append(alpha_result)
        
        # 保存到文件
        self.save_history()
        
    def get_history(self, limit=None):
        """获取历史记录"""
        if limit:
            return self.history_data[-limit:]  # 返回最近的limit条记录
        return self.history_data
        
    def get_successful_alphas(self, limit=None):
        """获取成功的 Alpha 记录"""
        successful = [record for record in self.history_data if record.get('passed_all_checks', False)]
        if limit:
            return successful[-limit:]
        return successful
        
    def get_failed_alphas(self, limit=None):
        """获取失败的 Alpha 记录"""
        failed = [record for record in self.history_data if not record.get('passed_all_checks', True)]
        if limit:
            return failed[-limit:]
        return failed
        
    def clear_history(self):
        """清空历史记录"""
        self.history_data = []
        self.save_history()
        print("✅ 历史记录已清空")