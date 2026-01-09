"""
营收分析工具 - 支持每日营收统计、趋势分析等操作
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from langchain.tools import tool
from storage.database.db import get_session
from storage.database.shared.model import Orders, Payments, DailyRevenue
from datetime import datetime, timedelta, date
import json
from sqlalchemy import func, and_


@tool
def calculate_daily_revenue(store_id: int, target_date: Optional[str] = None, runtime=None) -> str:
    """
    计算指定日期的营收数据，并更新或创建每日营收记录
    
    Args:
        store_id: 店铺ID
        target_date: 目标日期，格式为YYYY-MM-DD，默认为今天
    
    Returns:
        返回营收数据的JSON字符串
    """
    try:
        # 解析日期
        if target_date:
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        else:
            target_date = date.today()
        
        # 计算日期范围
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        db = get_session()
        try:
            # 查询当日订单
            orders = db.query(Orders).filter(
                Orders.store_id == store_id,
                Orders.created_at >= start_datetime,
                Orders.created_at <= end_datetime
            ).all()
            
            # 计算基础数据
            total_orders = len(orders)
            total_amount = sum(o.total_amount for o in orders)
            total_discount = sum(o.discount_amount for o in orders)
            
            # 查询当日退款
            refunded_orders = db.query(Orders).filter(
                Orders.store_id == store_id,
                Orders.created_at >= start_datetime,
                Orders.created_at <= end_datetime,
                Orders.order_status == "cancelled"
            ).all()
            total_refund = sum(o.final_amount for o in refunded_orders)
            
            # 计算净营收
            net_revenue = total_amount - total_discount - total_refund
            
            # 统计支付方式
            payment_methods = {}
            for order in orders:
                if order.payment_method:
                    payment_methods[order.payment_method] = payment_methods.get(order.payment_method, 0) + order.final_amount
            
            # 统计高峰时段（按小时）
            peak_hours = {}
            for order in orders:
                hour = order.created_at.hour
                peak_hours[hour] = peak_hours.get(hour, 0) + 1
            
            # 查找或创建每日营收记录
            revenue_record = db.query(DailyRevenue).filter(
                DailyRevenue.store_id == store_id,
                func.date(DailyRevenue.date) == target_date
            ).first()
            
            if revenue_record:
                # 更新记录
                revenue_record.total_orders = total_orders
                revenue_record.total_amount = total_amount
                revenue_record.total_discount = total_discount
                revenue_record.total_refund = total_refund
                revenue_record.net_revenue = net_revenue
                revenue_record.payment_methods = payment_methods
                revenue_record.peak_hours = peak_hours
                revenue_record.updated_at = datetime.now()
            else:
                # 创建新记录
                revenue_record = DailyRevenue(
                    store_id=store_id,
                    date=start_datetime,
                    total_orders=total_orders,
                    total_amount=total_amount,
                    total_discount=total_discount,
                    total_refund=total_refund,
                    net_revenue=net_revenue,
                    payment_methods=payment_methods,
                    peak_hours=peak_hours
                )
                db.add(revenue_record)
            
            db.commit()
            db.refresh(revenue_record)
            
            return json.dumps({
                "success": True,
                "message": f"成功计算并更新店铺 {store_id} 在 {target_date} 的营收数据",
                "store_id": store_id,
                "date": target_date.isoformat() if isinstance(target_date, datetime) else target_date.strftime("%Y-%m-%d") if isinstance(target_date, date) else str(target_date),
                "total_orders": total_orders,
                "total_amount": total_amount,
                "total_discount": total_discount,
                "total_refund": total_refund,
                "net_revenue": net_revenue,
                "payment_methods": payment_methods,
                "peak_hours": peak_hours
            }, ensure_ascii=False, indent=2)
            
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        return json.dumps({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, ensure_ascii=False, indent=2)


@tool
def get_revenue_trend(store_id: int, days: int = 7, runtime=None) -> str:
    """
    获取指定天数内的营收趋势数据
    
    Args:
        store_id: 店铺ID
        days: 查询天数，默认7天
    
    Returns:
        返回营收趋势的JSON字符串
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        db = get_session()
        try:
            # 查询每日营收记录
            revenues = db.query(DailyRevenue).filter(
                DailyRevenue.store_id == store_id,
                func.date(DailyRevenue.date) >= start_date,
                func.date(DailyRevenue.date) <= end_date
            ).order_by(DailyRevenue.date).all()
            
            # 构建返回数据
            trend_data = []
            for revenue in revenues:
                trend_data.append({
                    "date": revenue.date.strftime("%Y-%m-%d"),
                    "total_orders": revenue.total_orders,
                    "total_amount": revenue.total_amount,
                    "total_discount": revenue.total_discount,
                    "total_refund": revenue.total_refund,
                    "net_revenue": revenue.net_revenue,
                    "payment_methods": revenue.payment_methods,
                    "peak_hours": revenue.peak_hours
                })
            
            # 计算统计数据
            if trend_data:
                avg_orders = sum(d["total_orders"] for d in trend_data) / len(trend_data)
                avg_revenue = sum(d["net_revenue"] for d in trend_data) / len(trend_data)
                max_revenue = max(d["net_revenue"] for d in trend_data)
                min_revenue = min(d["net_revenue"] for d in trend_data)
            else:
                avg_orders = 0
                avg_revenue = 0
                max_revenue = 0
                min_revenue = 0
            
            return json.dumps({
                "success": True,
                "store_id": store_id,
                "period": f"{start_date} ~ {end_date}",
                "days": len(trend_data),
                "statistics": {
                    "avg_orders_per_day": round(avg_orders, 2),
                    "avg_revenue_per_day": round(avg_revenue, 2),
                    "max_revenue": max_revenue,
                    "min_revenue": min_revenue
                },
                "trend": trend_data
            }, ensure_ascii=False, indent=2)
            
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        return json.dumps({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, ensure_ascii=False, indent=2)


@tool
def compare_revenue(store_id: int, period1_start: str, period1_end: str, period2_start: str, period2_end: str, runtime=None) -> str:
    """
    对比两个时期的营收数据
    
    Args:
        store_id: 店铺ID
        period1_start: 时期1开始日期（YYYY-MM-DD）
        period1_end: 时期1结束日期（YYYY-MM-DD）
        period2_start: 时期2开始日期（YYYY-MM-DD）
        period2_end: 时期2结束日期（YYYY-MM-DD）
    
    Returns:
        返回对比数据的JSON字符串
    """
    try:
        # 解析日期
        p1_start = datetime.strptime(period1_start, "%Y-%m-%d").date()
        p1_end = datetime.strptime(period1_end, "%Y-%m-%d").date()
        p2_start = datetime.strptime(period2_start, "%Y-%m-%d").date()
        p2_end = datetime.strptime(period2_end, "%Y-%m-%d").date()
        
        db = get_session()
        try:
            # 查询时期1的营收
            revenues1 = db.query(DailyRevenue).filter(
                DailyRevenue.store_id == store_id,
                func.date(DailyRevenue.date) >= p1_start,
                func.date(DailyRevenue.date) <= p1_end
            ).all()
            
            # 查询时期2的营收
            revenues2 = db.query(DailyRevenue).filter(
                DailyRevenue.store_id == store_id,
                func.date(DailyRevenue.date) >= p2_start,
                func.date(DailyRevenue.date) <= p2_end
            ).all()
            
            # 计算时期1的统计数据
            period1 = {
                "period": f"{period1_start} ~ {period1_end}",
                "days": len(revenues1),
                "total_orders": sum(r.total_orders for r in revenues1),
                "total_amount": sum(r.total_amount for r in revenues1),
                "net_revenue": sum(r.net_revenue for r in revenues1)
            }
            
            # 计算时期2的统计数据
            period2 = {
                "period": f"{period2_start} ~ {period2_end}",
                "days": len(revenues2),
                "total_orders": sum(r.total_orders for r in revenues2),
                "total_amount": sum(r.total_amount for r in revenues2),
                "net_revenue": sum(r.net_revenue for r in revenues2)
            }
            
            # 计算对比数据
            comparison = {
                "order_change": period2["total_orders"] - period1["total_orders"],
                "order_change_rate": ((period2["total_orders"] - period1["total_orders"]) / period1["total_orders"] * 100) if period1["total_orders"] > 0 else 0,
                "revenue_change": period2["net_revenue"] - period1["net_revenue"],
                "revenue_change_rate": ((period2["net_revenue"] - period1["net_revenue"]) / period1["net_revenue"] * 100) if period1["net_revenue"] > 0 else 0
            }
            
            return json.dumps({
                "success": True,
                "store_id": store_id,
                "period1": period1,
                "period2": period2,
                "comparison": comparison,
                "insight": f"相比时期1，时期2的订单数{'增加' if comparison['order_change'] > 0 else '减少'}了{abs(comparison['order_change_rate']):.2f}%，营收{'增长' if comparison['revenue_change'] > 0 else '下降'}了{abs(comparison['revenue_change_rate']):.2f}%"
            }, ensure_ascii=False, indent=2)
            
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        return json.dumps({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, ensure_ascii=False, indent=2)


@tool
def get_peak_hours_analysis(store_id: int, days: int = 30, runtime=None) -> str:
    """
    分析高峰时段，找出最繁忙的时间段
    
    Args:
        store_id: 店铺ID
        days: 分析天数，默认30天
    
    Returns:
        返回高峰时段分析的JSON字符串
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        db = get_session()
        try:
            # 查询每日营收记录
            revenues = db.query(DailyRevenue).filter(
                DailyRevenue.store_id == store_id,
                func.date(DailyRevenue.date) >= start_date,
                func.date(DailyRevenue.date) <= end_date
            ).all()
            
            # 统计各时段的订单数
            hour_stats = {}
            for revenue in revenues:
                if revenue.peak_hours:
                    for hour, count in revenue.peak_hours.items():
                        hour_stats[hour] = hour_stats.get(hour, 0) + count
            
            # 排序找出高峰时段
            sorted_hours = sorted(hour_stats.items(), key=lambda x: x[1], reverse=True)
            
            # 构建返回数据
            peak_analysis = {
                "total_days": len(revenues),
                "hourly_stats": sorted_hours,
                "top_5_peak_hours": sorted_hours[:5],
                "average_orders_per_hour": {str(k): round(v / len(revenues), 2) for k, v in hour_stats.items()},
                "insights": []
            }
            
            # 生成洞察
            if sorted_hours:
                peak_hour = sorted_hours[0][0]
                peak_analysis["insights"].append(f"最高峰时段是 {peak_hour}:00-{int(peak_hour)+1}:00，平均每天有 {sorted_hours[0][1] / len(revenues):.1f} 单")
                
                # 分析上午、下午、晚上的分布
                morning = sum(v for k, v in hour_stats.items() if 6 <= k < 12)
                afternoon = sum(v for k, v in hour_stats.items() if 12 <= k < 18)
                evening = sum(v for k, v in hour_stats.items() if 18 <= k < 24)
                night = sum(v for k, v in hour_stats.items() if 0 <= k < 6)
                
                total = morning + afternoon + evening + night
                if total > 0:
                    peak_analysis["insights"].append(f"上午（6-12点）占比 {morning/total*100:.1f}%，下午（12-18点）占比 {afternoon/total*100:.1f}%，晚上（18-24点）占比 {evening/total*100:.1f}%")
            
            return json.dumps({
                "success": True,
                "store_id": store_id,
                "analysis_period": f"{start_date} ~ {end_date}",
                "peak_analysis": peak_analysis
            }, ensure_ascii=False, indent=2)
            
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        return json.dumps({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, ensure_ascii=False, indent=2)
