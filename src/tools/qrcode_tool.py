"""
二维码生成工具
"""
import qrcode
from io import BytesIO
import os
from typing import Optional
from sqlalchemy.orm import Session
from storage.database.db import get_session
from storage.database.shared.model import Table, Store
from storage.s3.s3_storage import S3SyncStorage
import json


def generate_qrcode_url(store_id: int, table_id: int, base_url: str = "https://your-domain.com/order") -> str:
    """
    生成扫码后的跳转URL
    
    Args:
        store_id: 店铺ID
        table_id: 桌号ID
        base_url: 基础URL
    
    Returns:
        完整的跳转URL
    """
    return f"{base_url}?store_id={store_id}&table_id={table_id}"


def generate_qrcode_image(url: str) -> BytesIO:
    """
    生成二维码图片
    
    Args:
        url: 二维码内容（跳转URL）
    
    Returns:
        二维码图片的 BytesIO 对象
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return img_io


def generate_table_qrcode(table_id: int, base_url: str = "https://your-domain.com/order") -> dict:
    """
    为指定桌号生成二维码并上传到S3
    
    Args:
        table_id: 桌号ID
        base_url: 基础URL
    
    Returns:
        包含二维码URL的字典
    """
    db = get_session()
    try:
        # 查询桌号信息
        table = db.query(Table).filter(Table.id == table_id).first()
        if not table:
            return {
                "success": False,
                "error": f"桌号ID {table_id} 不存在"
            }
        
        # 生成跳转URL
        url = generate_qrcode_url(table.store_id, table_id, base_url)
        
        # 生成二维码图片
        img_io = generate_qrcode_image(url)
        
        # 上传到S3
        storage = S3SyncStorage(
            endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
            access_key="",
            secret_key="",
            bucket_name=os.getenv("COZE_BUCKET_NAME"),
            region="cn-beijing",
        )
        
        # 生成文件名：qrcode_table_{table_id}.png
        file_name = f"qrcode_table_{table_id}.png"
        key = storage.upload_file(
            file_content=img_io.getvalue(),
            file_name=file_name,
            content_type="image/png"
        )
        
        # 更新桌号表
        table.qrcode_url = storage.generate_presigned_url(key=key, expire_time=86400 * 365)  # 一年有效期
        table.qrcode_content = url
        db.commit()
        db.refresh(table)
        
        return {
            "success": True,
            "table_id": table_id,
            "table_number": table.table_number,
            "qrcode_url": table.qrcode_url,
            "qrcode_content": table.qrcode_content,
            "message": f"桌号 {table.table_number} 的二维码生成成功"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


def generate_store_qrcodes(store_id: int, base_url: str = "https://your-domain.com/order") -> dict:
    """
    为店铺的所有桌号生成二维码
    
    Args:
        store_id: 店铺ID
        base_url: 基础URL
    
    Returns:
        生成结果的汇总
    """
    db = get_session()
    try:
        # 查询店铺的所有桌号
        tables = db.query(Table).filter(
            Table.store_id == store_id,
            Table.is_active == True
        ).all()
        
        if not tables:
            return {
                "success": False,
                "error": f"店铺ID {store_id} 没有激活的桌号"
            }
        
        results = []
        success_count = 0
        fail_count = 0
        
        for table in tables:
            result = generate_table_qrcode(table.id, base_url)
            if result["success"]:
                success_count += 1
                results.append({
                    "table_id": table.id,
                    "table_number": table.table_number,
                    "qrcode_url": result["qrcode_url"],
                    "status": "success"
                })
            else:
                fail_count += 1
                results.append({
                    "table_id": table.id,
                    "table_number": table.table_number,
                    "error": result["error"],
                    "status": "failed"
                })
        
        return {
            "success": True,
            "store_id": store_id,
            "total": len(tables),
            "success_count": success_count,
            "fail_count": fail_count,
            "results": results
        }
        
    finally:
        db.close()


if __name__ == "__main__":
    # 测试生成二维码
    print("测试为店铺2的所有桌号生成二维码...")
    result = generate_store_qrcodes(2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
