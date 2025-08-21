"""Alpha 历史记录管理模块 (SQLite版本)"""

import sqlite3
import json
import os
from datetime import datetime


class AlphaHistoryManagerSQLite:
    def __init__(self, db_file="alpha_history.db"):
        """初始化历史记录管理器"""
        self.db_file = db_file
        self.init_database()
        
    def init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                # 创建表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alpha_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alpha_id TEXT UNIQUE,
                        expression TEXT,
                        passed_all_checks BOOLEAN,
                        metrics TEXT,  -- JSON格式存储指标
                        timestamp TEXT,
                        saved_at TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"❌ 初始化数据库时出错: {str(e)}")
            
    def add_alpha_result(self, alpha_result):
        """添加 Alpha 测试结果到历史记录"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # 添加时间戳
                alpha_result['saved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 将指标转换为JSON字符串
                metrics_json = json.dumps(alpha_result.get('metrics', {}))
                
                # 插入数据
                cursor.execute('''
                    INSERT OR REPLACE INTO alpha_history 
                    (alpha_id, expression, passed_all_checks, metrics, timestamp, saved_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    alpha_result.get('alpha_id'),
                    alpha_result.get('expression'),
                    alpha_result.get('passed_all_checks', False),
                    metrics_json,
                    alpha_result.get('timestamp'),
                    alpha_result['saved_at']
                ))
                
                conn.commit()
                print("✅ Alpha 历史记录保存成功")
                
        except Exception as e:
            print(f"❌ 保存历史记录时出错: {str(e)}")
            
    def get_history(self, limit=None):
        """获取历史记录"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                if limit:
                    cursor.execute('''
                        SELECT alpha_id, expression, passed_all_checks, metrics, timestamp, saved_at
                        FROM alpha_history
                        ORDER BY saved_at DESC
                        LIMIT ?
                    ''', (limit,))
                else:
                    cursor.execute('''
                        SELECT alpha_id, expression, passed_all_checks, metrics, timestamp, saved_at
                        FROM alpha_history
                        ORDER BY saved_at DESC
                    ''')
                
                rows = cursor.fetchall()
                history = []
                for row in rows:
                    record = {
                        'alpha_id': row[0],
                        'expression': row[1],
                        'passed_all_checks': row[2],
                        'metrics': json.loads(row[3]) if row[3] else {},
                        'timestamp': row[4],
                        'saved_at': row[5]
                    }
                    history.append(record)
                    
                return history
                
        except Exception as e:
            print(f"❌ 获取历史记录时出错: {str(e)}")
            return []
            
    def get_successful_alphas(self, limit=None):
        """获取成功的 Alpha 记录"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                if limit:
                    cursor.execute('''
                        SELECT alpha_id, expression, passed_all_checks, metrics, timestamp, saved_at
                        FROM alpha_history
                        WHERE passed_all_checks = 1
                        ORDER BY saved_at DESC
                        LIMIT ?
                    ''', (limit,))
                else:
                    cursor.execute('''
                        SELECT alpha_id, expression, passed_all_checks, metrics, timestamp, saved_at
                        FROM alpha_history
                        WHERE passed_all_checks = 1
                        ORDER BY saved_at DESC
                    ''')
                
                rows = cursor.fetchall()
                history = []
                for row in rows:
                    record = {
                        'alpha_id': row[0],
                        'expression': row[1],
                        'passed_all_checks': row[2],
                        'metrics': json.loads(row[3]) if row[3] else {},
                        'timestamp': row[4],
                        'saved_at': row[5]
                    }
                    history.append(record)
                    
                return history
                
        except Exception as e:
            print(f"❌ 获取成功Alpha记录时出错: {str(e)}")
            return []
            
    def get_failed_alphas(self, limit=None):
        """获取失败的 Alpha 记录"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                if limit:
                    cursor.execute('''
                        SELECT alpha_id, expression, passed_all_checks, metrics, timestamp, saved_at
                        FROM alpha_history
                        WHERE passed_all_checks = 0
                        ORDER BY saved_at DESC
                        LIMIT ?
                    ''', (limit,))
                else:
                    cursor.execute('''
                        SELECT alpha_id, expression, passed_all_checks, metrics, timestamp, saved_at
                        FROM alpha_history
                        WHERE passed_all_checks = 0
                        ORDER BY saved_at DESC
                    ''')
                
                rows = cursor.fetchall()
                history = []
                for row in rows:
                    record = {
                        'alpha_id': row[0],
                        'expression': row[1],
                        'passed_all_checks': row[2],
                        'metrics': json.loads(row[3]) if row[3] else {},
                        'timestamp': row[4],
                        'saved_at': row[5]
                    }
                    history.append(record)
                    
                return history
                
        except Exception as e:
            print(f"❌ 获取失败Alpha记录时出错: {str(e)}")
            return []
            
    def clear_history(self):
        """清空历史记录"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM alpha_history')
                conn.commit()
                print("✅ 历史记录已清空")
        except Exception as e:
            print(f"❌ 清空历史记录时出错: {str(e)}")
            
    def get_statistics(self):
        """获取统计信息"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # 总数
                cursor.execute('SELECT COUNT(*) FROM alpha_history')
                total_count = cursor.fetchone()[0]
                
                # 成功数
                cursor.execute('SELECT COUNT(*) FROM alpha_history WHERE passed_all_checks = 1')
                success_count = cursor.fetchone()[0]
                
                return {
                    'total_count': total_count,
                    'success_count': success_count,
                    'success_rate': success_count / total_count if total_count > 0 else 0
                }
                
        except Exception as e:
            print(f"❌ 获取统计信息时出错: {str(e)}")
            return {
                'total_count': 0,
                'success_count': 0,
                'success_rate': 0
            }