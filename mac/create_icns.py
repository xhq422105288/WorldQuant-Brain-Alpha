import os
from PIL import Image
import struct

def create_icns(png_path):
    """创建.icns文件"""
    try:
        # 创建临时iconset目录
        iconset_name = "icon.iconset"
        if not os.path.exists(iconset_name):
            os.makedirs(iconset_name)
        
        # 需要的图标尺寸和对应的icns类型
        icon_types = {
            16: 'icp4',    # 16x16
            32: 'icp5',    # 32x32
            64: 'icp6',    # 64x64
            128: 'ic07',   # 128x128
            256: 'ic08',   # 256x256
            512: 'ic09',   # 512x512
            1024: 'ic10'   # 1024x1024
        }
        
        # 打开原始图片
        img = Image.open(png_path)
        
        # 创建icns文件
        icns_path = os.path.join(os.path.dirname(png_path), 'icon.icns')
        with open(icns_path, 'wb') as icns_file:
            # 写入icns文件头
            icns_file.write(b'icns')  # 魔数
            size_placeholder = icns_file.tell()
            icns_file.write(b'\x00\x00\x00\x00')  # 文件大小占位
            
            # 为每个尺寸生成图标数据
            for size, icon_type in icon_types.items():
                # 调整图片大小
                img_copy = img.copy()
                img_copy.thumbnail((size, size), Image.Resampling.LANCZOS)
                
                # 转换为PNG格式
                from io import BytesIO
                png_data = BytesIO()
                img_copy.save(png_data, format='PNG')
                png_bytes = png_data.getvalue()
                
                # 写入图标类型和数据
                icns_file.write(icon_type.encode('ascii'))
                data_size = len(png_bytes) + 8  # 8是类型和大小字段的长度
                icns_file.write(struct.pack('>I', data_size))
                icns_file.write(png_bytes)
            
            # 写入文件总大小
            total_size = icns_file.tell()
            icns_file.seek(size_placeholder)
            icns_file.write(struct.pack('>I', total_size))
        
        print(f"✅ 成功创建 icon.icns 文件: {icns_path}")
        
    except Exception as e:
        print(f"❌ 创建图标时出错: {str(e)}")
        raise

if __name__ == "__main__":
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录
    root_dir = os.path.dirname(script_dir)
    
    # 检查图标文件
    png_paths = [
        os.path.join(script_dir, 'icon.png'),  # mac目录下的icon.png
        os.path.join(root_dir, 'icon.png'),    # 项目根目录下的icon.png
    ]
    
    png_path = None
    for path in png_paths:
        if os.path.exists(path):
            png_path = path
            break
    
    if png_path is None:
        print("❌ 未找到 icon.png 文件")
        print("请将 icon.png 放在以下位置之一：")
        for path in png_paths:
            print(f"  - {path}")
    else:
        print(f"✅ 找到图标文件: {png_path}")
        create_icns(png_path) 