import PyInstaller.__main__
import os
import sys
import shutil

# 获取项目根目录的绝对路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 创建 mac 目录
mac_dir = os.path.dirname(os.path.abspath(__file__))
mac_dist_dir = os.path.join(mac_dir, 'dist')
if not os.path.exists(mac_dir):
    os.makedirs(mac_dir)
if not os.path.exists(mac_dist_dir):
    os.makedirs(mac_dist_dir)

# 设置命令行参数
args = [
    os.path.join(ROOT_DIR, 'main.py'),  # 主程序入口
    '--name=Alpha_Tool',  # Mac版本名称
    '--onefile',  # 打包成单个文件
    '--console',  # 使用控制台窗口
    f'--add-data={os.path.join(ROOT_DIR, "dataset_config.py")}{os.pathsep}.',
    f'--add-data={os.path.join(ROOT_DIR, "alpha_strategy.py")}{os.pathsep}.',
    f'--add-data={os.path.join(ROOT_DIR, "brain_batch_alpha.py")}{os.pathsep}.',
    '--clean',
    '--noconfirm',
    '--target-architecture=universal2',  # 支持 Intel 和 M1 芯片
    '--codesign-identity=-',
    f'--distpath={mac_dist_dir}',
    f'--workpath={os.path.join(mac_dir, "build")}',
    f'--specpath={mac_dir}'
]

# 如果有Mac图标文件，添加图标
if os.path.exists(os.path.join(mac_dir, 'icon.icns')):
    args.append(f'--icon={os.path.join(mac_dir, "icon.icns")}')

# 运行打包命令
PyInstaller.__main__.run(args)

# 打包完成后，复制或创建配置文件到dist目录
print("\n正在处理配置文件...")
try:
    # 处理认证文件
    credentials_src = os.path.join(ROOT_DIR, 'brain_credentials.txt')
    if os.path.exists(credentials_src):
        shutil.copy2(credentials_src, mac_dist_dir)
        print("✅ brain_credentials.txt 复制成功")
    else:
        with open(os.path.join(mac_dist_dir, 'brain_credentials.txt'), 'w') as f:
            f.write('["your_email@example.com","your_password"]')
        print("✅ 创建了示例 brain_credentials.txt")
        
    # 处理Alpha ID文件
    alpha_ids_src = os.path.join(ROOT_DIR, 'alpha_ids.txt')
    if os.path.exists(alpha_ids_src):
        shutil.copy2(alpha_ids_src, mac_dist_dir)
        print("✅ alpha_ids.txt 复制成功")
    else:
        with open(os.path.join(mac_dist_dir, 'alpha_ids.txt'), 'w') as f:
            pass
        print("✅ 创建了空的 alpha_ids.txt")
        
    # 创建运行说明文件
    with open(os.path.join(mac_dist_dir, 'README_MAC.txt'), 'w') as f:
        f.write('''Mac版本使用说明：
1. 打开终端 (Terminal)
2. 进入程序所在目录：cd 程序所在路径
3. 添加执行权限：chmod +x Alpha_Tool
4. 运行程序：./Alpha_Tool
        ''')
    print("✅ 创建了使用说明文件")
        
except Exception as e:
    print(f"❌ 处理配置文件时出错: {str(e)}")

print(f"\n✅ Mac版本打包完成! 文件位于 {mac_dist_dir}") 