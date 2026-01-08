"""
二维码生成工具
为每个桌号生成唯一二维码并上传至S3
支持彩色二维码和中间添加公司logo
"""
import io
import os
from typing import Optional
from PIL import Image, ImageDraw
import qrcode
from qrcode.constants import ERROR_CORRECT_H

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

    def _add_logo_to_qrcode(self, qrcode_img: Image.Image, logo_data: bytes, logo_ratio: float = 0.2) -> Image.Image:
        """
        在二维码中间添加logo

        Args:
            qrcode_img: 二维码图片对象
            logo_data: logo图片的字节数据
            logo_ratio: logo占二维码大小的比例（默认20%）

        Returns:
            Image.Image: 添加logo后的二维码图片
        """
        try:
            # 加载logo图片
            logo_img = Image.open(io.BytesIO(logo_data))

            # 计算logo尺寸
            qr_width, qr_height = qrcode_img.size
            logo_size = int(min(qr_width, qr_height) * logo_ratio)

            # 调整logo大小（保持宽高比）
            logo_img.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

            # 计算logo位置（居中）
            logo_position = (
                (qr_width - logo_size) // 2,
                (qr_height - logo_size) // 2
            )

            # 创建带圆角的logo
            if logo_img.mode == 'RGBA':
                # logo已经是RGBA格式，直接使用
                pass
            else:
                logo_img = logo_img.convert('RGBA')

            # 创建白色背景的圆形遮罩
            mask = Image.new('RGBA', (logo_size, logo_size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(mask)
            draw.ellipse([(0, 0), (logo_size - 1, logo_size - 1)], fill=(255, 255, 255, 255))

            # 应用圆形遮罩
            logo_with_mask = Image.new('RGBA', (logo_size, logo_size))
            for y in range(logo_size):
                for x in range(logo_size):
                    pixel = logo_img.getpixel((x, y))
                    mask_pixel = mask.getpixel((x, y))
                    if mask_pixel[3] == 255:
                        logo_with_mask.putpixel((x, y), pixel)

            # 将logo粘贴到二维码上
            qrcode_img.paste(logo_with_mask, logo_position, logo_with_mask)

            return qrcode_img
        except Exception as e:
            # 如果添加logo失败，返回原始二维码
            print(f"添加logo失败: {str(e)}")
            return qrcode_img
    
    def generate_qrcode_for_table(
        self,
        table_id: int,
        base_url: str = "https://order.example.com",
        foreground_color: str = "black",
        background_color: str = "white",
        logo_data: Optional[bytes] = None,
        logo_ratio: float = 0.2
    ) -> dict:
        """
        为指定桌号生成二维码并上传至S3

        Args:
            table_id: 桌号ID
            base_url: 点餐页面的基础URL
            foreground_color: 二维码前景色（支持十六进制颜色或颜色名称）
            background_color: 二维码背景色（支持十六进制颜色或颜色名称）
            logo_data: logo图片的字节数据（可选）
            logo_ratio: logo占二维码大小的比例（默认20%）

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

            # 生成二维码图片（使用高错误纠正级别以支持logo）
            qr = qrcode.QRCode(
                version=1,
                error_correction=ERROR_CORRECT_H,  # 使用高错误纠正级别（30%）
                box_size=10,
                border=4,
            )
            qr.add_data(qrcode_content)
            qr.make(fit=True)

            # 将二维码转换为图片，使用自定义颜色
            img = qr.make_image(fill_color=foreground_color, back_color=background_color)

            # 如果有logo，添加到二维码中间
            if logo_data:
                img = self._add_logo_to_qrcode(img, logo_data, logo_ratio)

            # 将图片转换为字节流
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # 生成文件名（包含颜色信息以便区分）
            color_suffix = f"{foreground_color.replace('#', '')}_{background_color.replace('#', '')}"
            file_name = f"table_qrcode_store{table.store_id}_table{table.id}_{color_suffix}.png"

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
        base_url: str = "https://order.example.com",
        foreground_color: str = "black",
        background_color: str = "white",
        logo_data: Optional[bytes] = None,
        logo_ratio: float = 0.2
    ) -> list:
        """
        为指定店铺的所有桌号生成二维码

        Args:
            store_id: 店铺ID
            base_url: 点餐页面的基础URL
            foreground_color: 二维码前景色（支持十六进制颜色或颜色名称）
            background_color: 二维码背景色（支持十六进制颜色或颜色名称）
            logo_data: logo图片的字节数据（可选）
            logo_ratio: logo占二维码大小的比例（默认20%）

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
                result = self.generate_qrcode_for_table(
                    table.id,
                    base_url,
                    foreground_color,
                    background_color,
                    logo_data,
                    logo_ratio
                )
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
