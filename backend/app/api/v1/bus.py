"""
校车服务 API

本模块处理校车路线和时刻表查询相关的接口，包括：
- 获取校车路线列表
- 获取指定路线的时刻表

功能说明：
- 校车路线信息包括起点、终点、途经站点等
- 时刻表包括发车时间、到达时间等
- 只返回启用状态的路线
"""

# 导入 FastAPI 核心组件
from fastapi import APIRouter, Depends, HTTPException, status

# 导入 SQLAlchemy ORM 的 Session 类
from sqlalchemy.orm import Session

# 导入数据库连接依赖
from app.core.database import get_db

# 导入统一响应格式函数
from app.core.response import ok

# 导入校车相关的模型类
# BusRoute：校车路线模型，对应数据库中的 bus_routes 表
# BusSchedule：校车时刻表模型，对应数据库中的 bus_schedules 表
from app.models import BusRoute, BusSchedule

# 导入序列化函数
from app.utils.serializers import serialize_bus_route, serialize_bus_schedule

# 创建路由实例
router = APIRouter()


# ============================================================
# 获取校车路线列表接口
# ============================================================

# @router.get("/routes")：定义 GET 方法的接口，路径为 /bus/routes
# 用于获取所有启用的校车路线
@router.get("/routes")
def get_bus_routes(db: Session = Depends(get_db)):
    """
    获取校车路线列表

    参数说明：
    - db: 数据库会话
    """
    # 查询所有启用的校车路线
    # BusRoute.is_active == True：只查询状态为启用的路线
    # 对应 SQL：SELECT * FROM bus_routes WHERE is_active = TRUE
    # 这样设计可以隐藏已停运或维护中的路线
    routes = db.query(BusRoute).filter(BusRoute.is_active == True).all()

    # 将所有路线对象序列化为字典列表返回
    return ok([serialize_bus_route(r) for r in routes])


# ============================================================
# 获取路线时刻表接口
# ============================================================

# @router.get("/routes/{route_id}/schedules")：获取指定路线的时刻表
# 这是嵌套资源的设计模式：时刻表是路线的子资源
@router.get("/routes/{route_id}/schedules")
def get_bus_schedules(route_id: int, db: Session = Depends(get_db)):
    """
    获取路线时刻表

    参数说明：
    - route_id: 路线 ID
    - db: 数据库会话
    """
    # 首先验证路线是否存在
    # 对应 SQL：SELECT * FROM bus_routes WHERE id = ?
    route = db.query(BusRoute).filter(BusRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="路线不存在")

    # 查询该路线的所有时刻表
    # .filter(BusSchedule.route_id == route_id)：过滤出指定路线的时刻表
    # .order_by(BusSchedule.departure_time)：按发车时间升序排列
    # 对应 SQL：
    # SELECT * FROM bus_schedules
    # WHERE route_id = ?
    # ORDER BY departure_time ASC
    schedules = (
        db.query(BusSchedule)
        .filter(BusSchedule.route_id == route_id)
        .order_by(BusSchedule.departure_time)
        .all()
    )

    return ok([serialize_bus_schedule(s) for s in schedules])
