# Context 类的模拟实现（用于生产环境）

from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class Context:
    """模拟 Context 类，用于生产环境"""
    project_id: str = ""
    logid: str = ""
    run_id: str = ""
    method: str = ""
    headers: Optional[Dict[str, str]] = None

    @classmethod
    def run_id(cls) -> str:
        """返回空字符串"""
        return ""

def new_context(**kwargs) -> Context:
    """
    创建新的 Context 实例
    :param kwargs: 上下文参数
    :return: Context 实例
    """
    return Context(**kwargs)

def default_headers(ctx: Optional[Any] = None) -> Dict[str, str]:
    """
    返回默认的请求头
    :param ctx: 上下文（生产环境忽略）
    :return: 空字典
    """
    return {}
