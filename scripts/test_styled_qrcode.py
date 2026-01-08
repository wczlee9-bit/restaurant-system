"""
测试带样式的二维码生成功能
"""
import requests
import os
from pathlib import Path

# API地址
API_URL = "http://localhost:8000/api/generate-styled-qrcode"

def test_black_white():
    """测试黑白二维码"""
    print("测试1: 生成黑白二维码...")

    files = {}
    data = {
        'table_id': '11',  # 使用存在的桌号ID
        'base_url': 'https://tiny-sprite-65833c.netlify.app/restaurant_full_test.html',
        'foreground_color': 'black',
        'background_color': 'white',
        'logo_ratio': '0.2'
    }

    try:
        response = requests.post(API_URL, data=data, files=files)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"成功生成二维码!")
            print(f"二维码URL: {result.get('qrcode_url')}")
            print(f"二维码内容: {result.get('qrcode_content')}")
            return True
        else:
            print(f"失败: {response.text}")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

def test_color_qrcode():
    """测试彩色二维码"""
    print("\n测试2: 生成彩色二维码...")

    files = {}
    data = {
        'table_id': '11',  # 使用存在的桌号ID
        'base_url': 'https://tiny-sprite-65833c.netlify.app/restaurant_full_test.html',
        'foreground_color': '#667eea',
        'background_color': '#ffffff',
        'logo_ratio': '0.2'
    }

    try:
        response = requests.post(API_URL, data=data, files=files)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"成功生成彩色二维码!")
            print(f"二维码URL: {result.get('qrcode_url')}")
            return True
        else:
            print(f"失败: {response.text}")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

def test_qrcode_with_logo():
    """测试带logo的二维码"""
    print("\n测试3: 生成带logo的二维码...")

    # 创建一个简单的logo图片（用于测试）
    from PIL import Image, ImageDraw, ImageFont
    import io

    # 创建一个简单的logo
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([(20, 20), (180, 180)], fill='#667eea', outline='black')
    draw.text((60, 80), 'LOGO', fill='white')

    # 保存到内存
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {
        'logo': ('logo.png', img_bytes, 'image/png')
    }
    data = {
        'table_id': '11',  # 使用存在的桌号ID
        'base_url': 'https://tiny-sprite-65833c.netlify.app/restaurant_full_test.html',
        'foreground_color': 'black',
        'background_color': 'white',
        'logo_ratio': '0.2'
    }

    try:
        response = requests.post(API_URL, data=data, files=files)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"成功生成带logo的二维码!")
            print(f"二维码URL: {result.get('qrcode_url')}")
            return True
        else:
            print(f"失败: {response.text}")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

def test_styled_qrcode_with_logo():
    """测试彩色带logo的二维码"""
    print("\n测试4: 生成彩色带logo的二维码...")

    # 创建一个简单的logo图片（用于测试）
    from PIL import Image, ImageDraw
    import io

    # 创建一个简单的logo
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.ellipse([(20, 20), (180, 180)], fill='#764ba2', outline='black')
    draw.text((60, 90), 'R', fill='white')

    # 保存到内存
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {
        'logo': ('logo.png', img_bytes, 'image/png')
    }
    data = {
        'table_id': '11',  # 使用存在的桌号ID
        'base_url': 'https://tiny-sprite-65833c.netlify.app/restaurant_full_test.html',
        'foreground_color': '#667eea',
        'background_color': '#ffffff',
        'logo_ratio': '0.25'
    }

    try:
        response = requests.post(API_URL, data=data, files=files)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"成功生成彩色带logo的二维码!")
            print(f"二维码URL: {result.get('qrcode_url')}")
            return True
        else:
            print(f"失败: {response.text}")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("开始测试带样式的二维码生成功能")
    print("=" * 60)

    # 检查API服务是否运行
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"API服务状态: {response.json()}")
    except Exception as e:
        print(f"错误: 无法连接到API服务，请先启动API服务")
        print(f"启动命令: python -m src.main")
        exit(1)

    # 运行所有测试
    results = []
    results.append(("黑白二维码", test_black_white()))
    results.append(("彩色二维码", test_color_qrcode()))
    results.append(("带logo二维码", test_qrcode_with_logo()))
    results.append(("彩色带logo二维码", test_styled_qrcode_with_logo()))

    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")

    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 所有测试通过!")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息")
