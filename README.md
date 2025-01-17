# WorldQuant Brain Alpha 生成工具

## 简介
这是一个用于自动生成和提交 WorldQuant Brain Alpha 表达式的工具。它可以帮助用户自动化测试和提交 Alpha 策略。

## 安装说明

### 方法一：直接使用
1. 下载 `dist` 目录中的所有文件：
   - Alpha_工具.exe
   - brain_credentials.txt
   - alpha_ids.txt

2. 修改 `brain_credentials.txt` 文件，填入您的 WorldQuant Brain 账号信息：
   ```json
   ["your_email@example.com", "your_password"]
   ```

### 方法二：从源码构建
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 运行构建脚本：
   ```bash
   python build.py
   ```

## 使用说明

### 运行模式
工具提供三种运行模式：
1. 自动模式：测试并自动提交2个合格Alpha
2. 仅测试模式：测试并保存合格Alpha ID
3. 仅提交模式：提交已保存的合格Alpha ID

### 数据集选择
目前支持以下数据集：
- fundamental6：基础财务数据 (TOP3000)
- analyst4：分析师预测数据 (TOP1000)
- pv1：股市成交量数据 (TOP1000)

### 策略模式
提供两种策略生成模式：
1. 基础策略模式：生成单因子策略
2. 多因子组合模式：生成多因子组合策略

## 注意事项
1. 确保 `brain_credentials.txt` 中的账号信息正确
2. `alpha_ids.txt` 用于存储合格的 Alpha ID
3. 每次提交后会自动更新 `alpha_ids.txt`
4. 建议定期备份重要的 Alpha ID

## 指标要求
合格的 Alpha 需要满足以下条件：
- Sharpe ratio > 1.5
- Fitness > 1.0
- Turnover: 0.1-0.9
- IC Mean > 0.02
- 子宇宙 Sharpe 需满足特定要求

## 常见问题
1. 如果认证失败，请检查账号信息是否正确
2. 如果无法获取数据字段，请确认数据集是否可用
3. 如果提交失败，可能是因为达到当日提交限制

## 更新日志
- v1.0.0: 初始版本发布
- v1.0.1: 添加 pv1 数据集支持
- v1.0.2: 优化策略生成逻辑

## 联系方式
如有问题或建议，请联系开发者666@woaiys.filegear-sg.me。

## 许可证
MIT License 