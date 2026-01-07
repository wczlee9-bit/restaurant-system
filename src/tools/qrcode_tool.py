"""
二维码生成工具
为每个桌号生成唯一二维码并上传至S3
"""
import io
import os
from typing import Optional
import qrcode
from qrcode.constants import ERROR_CORRECT_L

from storage.s3.s3_storage import S3SyncStorage
from storage.database.db import get_session
from storage.database.shared.model import Tables


class QRCodeGenerator:
    """二维码生成器"""
    
    def __init__(self):
        """初始化S3存储客户端"""
        self.storage = S3SyncStorage(
            endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
            access_key="",
            secret_key="",
            bucket_name=os.getenv("COZE_BUCKET_NAME"),
            region="cn-beijing",
        )
    
    def generate_qrcode_for_table(
        self, 
        table_id: int, 
        base_url: str = "https://order.example.com"
    ) -> dict:
        """
        为指定桌号生成二维码并上传至S3
        
        Args:
            table_id: 桌号ID
            base_url: 点餐页面的基础URL
            
        Returns:
            dict: 包含二维码URL和二维码内容
            {
                "qrcode_url": "https://...",
                "qrcode_content": "https://order.example.com?table=xxx&store=xxx"
            }
        """
        db = get_session()
        try:
            # 获取桌号信息
            table = db.query(Tables).filter(Tables.id == table_id).first()
            if not table:
                raise ValueError(f"桌号ID {table_id} 不存在")
            
            # 生成二维码内容（包含店铺ID和桌号）
            qrcode_content = f"{base_url}?store_id={table.store_id}&table_id={table_id}"
            
            # 生成二维码图片
            qr = qrcode.QRCode(
                version=1,
                error_correction=ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qrcode_content)
            qr.make(fit=True)
            
            # 将二维码转换为图片
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 将图片转换为字节流
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # 生成文件名
            file_name = f"table_qrcode_store{table.store_id}_table{table.id}.png"
            
            # 上传到S3
            qrcode_key = self.storage.upload_file(
                file_content=img_byte_arr,
                file_name=file_name,
                content_type="image/png"
            )
            
            # 生成签名URL（有效期1小时）
            qrcode_url = self.storage.generate_presigned_url(
                key=qrcode_key,
                expire_time=3600
            )
            
            # 更新数据库
            table.qrcode_url = qrcode_url
            table.qrcode_content = qrcode_content
            db.commit()
            db.refresh(table)
            
            return {
                "qrcode_url": qrcode_url,
                "qrcode_content": qrcode_content,
                "table_id": table_id,
                "store_id": table.store_id,
                "table_number": table.table_number
            }
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def generate_qrcodes_for_store(
        self, 
        store_id: int, 
        base_url: str = "https://order.example.com"
    ) -> list:
        """
        为指定店铺的所有桌号生成二维码
        
        Args:
            store_id: 店铺ID
            base_url: 点餐页面的基础URL
            
        Returns:
            list: 所有桌号的二维码信息列表
        """
        db = get_session()
        try:
            # 获取店铺所有活跃的桌号
            tables = db.query(Tables).filter(
                Tables.store_id == store_id,
                Tables.is_active == True
            ).all()
            
            results = []
            for table in tables:
                result = self.generate_qrcode_for_table(table.id, base_url)
                results.append(result)
            
            return results
            
        finally:
            db.close()
    
    def get_qrcode_url_by_table(self, table_id: int) -> Optional[str]:
        """
        获取桌号的二维码URL
        
        Args:
            table_id: 桌号ID
            
        Returns:
            str: 二维码URL，如果不存在则返回None
        """
        db = get_session()
        try:
            table = db.query(Tables).filter(Tables.id == table_id).first()
            if table and table.qrcode_url:
                return table.qrcode_url
            return None
        finally:
            db.close()
