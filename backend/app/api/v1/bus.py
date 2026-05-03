"""
校车服务 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.response import ok
from app.models import BusRoute, BusSchedule
from app.utils.serializers import serialize_bus_route, serialize_bus_schedule

router = APIRouter()


@router.get("/routes")
def get_bus_routes(db: Session = Depends(get_db)):
    """获取校车路线列表"""
    routes = db.query(BusRoute).filter(BusRoute.is_active == True).all()
    return ok([serialize_bus_route(r) for r in routes])


@router.get("/routes/{route_id}/schedules")
def get_bus_schedules(route_id: int, db: Session = Depends(get_db)):
    """获取路线时刻表"""
    route = db.query(BusRoute).filter(BusRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="路线不存在")

    schedules = (
        db.query(BusSchedule)
        .filter(BusSchedule.route_id == route_id)
        .order_by(BusSchedule.departure_time)
        .all()
    )
    return ok([serialize_bus_schedule(s) for s in schedules])
