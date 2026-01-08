#!/usr/bin/env python3
"""
生成桌号二维码脚本
为每个桌号生成二维码图片，模拟顾客扫码点餐场景
"""

import os
import qrcode
from pathlib import Path

# 配置
QRCODE_DIR = "/workspace/projects/assets/qrcodes"
API_BASE = "http://9.128.251.82:8080"  # 使用实际IP

# 要生成二维码的桌号列表
TABLES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

def generate_table_qrcode(table_number):
    """
    为指定桌号生成二维码

    Args:
        table_number (int): 桌号

    Returns:
        str: 二维码文件路径
    """
    # 创建二维码内容（包含桌号信息）
    # 格式: ?table=8
    qr_content = f"{API_BASE}/assets/restaurant_full_test.html?table={table_number}"

    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    # 创建二维码图片
    img = qr.make_image(fill_color="black", back_color="white")

    # 保存图片
    os.makedirs(QRCODE_DIR, exist_ok=True)
    qr_path = os.path.join(QRCODE_DIR, f"table_{table_number}.png")
    img.save(qr_path)

    print(f"✅ 已生成 {table_number}号桌二维码: {qr_path}")
    print(f"   扫码后将跳转: {qr_content}")

    return qr_path

def generate_all_qrcodes():
    """生成所有桌号的二维码"""
    print("=" * 60)
    print("📱 生成桌号二维码")
    print("=" * 60)
    print()

    for table in TABLES:
        try:
            generate_table_qrcode(table)
        except Exception as e:
            print(f"❌ 生成{table}号桌二维码失败: {e}")

    print()
    print("=" * 60)
    print(f"✅ 二维码生成完成！共 {len(TABLES)} 个桌号")
    print(f"📁 保存位置: {QRCODE_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    generate_all_qrcodes()
