"""
数据库初始化脚本（开发环境）
- 清库重建：drop_all → create_all
- 灌注测试种子数据，覆盖新关系（Activity.publisher_id / Like / 唯一约束）
"""
from datetime import datetime, timedelta
from app.core.database import SessionLocal, engine, Base
from app.models import (
    User, UserRole,
    Product, ProductCategory, ProductStatus,
    ProductComment,
    Venue, VenueType, VenueTimeSlot,
    BusRoute, BusSchedule,
    Post, PostCategory, PostComment, Like,
    Activity, ActivityRegistration,
)
from app.core.security import get_password_hash

print("🧹 正在清空旧表 ...")
Base.metadata.drop_all(bind=engine)
print("🛠️  正在创建新表结构 ...")
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # ---------------- 用户 ----------------
    test_users = [
        User(
            student_id="320200001",
            username="zhangsan",
            hashed_password=get_password_hash("123456"),
            real_name="张三",
            phone="13800138001",
            email="zhangsan@lzu.edu.cn",
            avatar="",
            role=UserRole.STUDENT,
        ),
        User(
            student_id="320200002",
            username="lisi",
            hashed_password=get_password_hash("123456"),
            real_name="李四",
            phone="13800138002",
            email="lisi@lzu.edu.cn",
            avatar="",
            role=UserRole.STUDENT,
        ),
        User(
            student_id="320200003",
            username="wangwu",
            hashed_password=get_password_hash("123456"),
            real_name="王五",
            phone="13800138003",
            email="wangwu@lzu.edu.cn",
            avatar="",
            role=UserRole.STUDENT,
        ),
    ]
    db.add_all(test_users)
    db.commit()

    # ---------------- 二手商品 ----------------
    test_products = [
        Product(
            title="高等数学教材",
            description="九成新，无笔记，适合大一学生",
            price=25.0,
            category=ProductCategory.BOOKS,
            status=ProductStatus.AVAILABLE,
            images="[]",
            seller_id=1,
        ),
        Product(
            title="二手蓝牙耳机",
            description="音质好，续航 6h，原装配件齐全",
            price=120.0,
            category=ProductCategory.ELECTRONICS,
            status=ProductStatus.AVAILABLE,
            images="[]",
            seller_id=2,
        ),
        Product(
            title="宿舍小台灯",
            description="充电款，三档调光，可夹床头",
            price=35.0,
            category=ProductCategory.DAILY,
            status=ProductStatus.AVAILABLE,
            images="[]",
            seller_id=3,
        ),
    ]
    db.add_all(test_products)
    db.commit()

    # ---------------- 场馆 ----------------
    test_venues = [
        Venue(
            name="体育馆篮球场",
            venue_type=VenueType.BASKETBALL,
            location="城关校区体育馆",
            capacity=20,
            description="标准篮球场，设施完善",
        ),
        Venue(
            name="羽毛球馆",
            venue_type=VenueType.BADMINTON,
            location="榆中校区体育馆",
            capacity=10,
            description="专业羽毛球场地",
        ),
    ]
    db.add_all(test_venues)
    db.commit()

    # ---------------- 场馆时段（未来 3 天）----------------
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    time_slots = []
    for venue_id in [1, 2]:
        for day in range(3):
            date = today + timedelta(days=day)
            for hour in [9, 14, 16, 19]:
                time_slots.append(
                    VenueTimeSlot(
                        venue_id=venue_id,
                        date=date,
                        start_time=f"{hour:02d}:00",
                        end_time=f"{hour+2:02d}:00",
                        capacity=10,
                        booked_count=0,
                        is_available=True,
                    )
                )
    db.add_all(time_slots)
    db.commit()

    # ---------------- 校车 ----------------
    test_routes = [
        BusRoute(
            name="城关-榆中线",
            from_campus="城关校区",
            to_campus="榆中校区",
            description="连接城关和榆中校区",
        ),
        BusRoute(
            name="榆中-城关线",
            from_campus="榆中校区",
            to_campus="城关校区",
            description="连接榆中和城关校区",
        ),
    ]
    db.add_all(test_routes)
    db.commit()

    test_schedules = [
        BusSchedule(route_id=1, departure_time="07:30", seats=45, weekday_only=True),
        BusSchedule(route_id=1, departure_time="12:30", seats=45, weekday_only=False),
        BusSchedule(route_id=1, departure_time="17:30", seats=45, weekday_only=True),
        BusSchedule(route_id=2, departure_time="08:00", seats=45, weekday_only=True),
        BusSchedule(route_id=2, departure_time="13:00", seats=45, weekday_only=False),
        BusSchedule(route_id=2, departure_time="18:00", seats=45, weekday_only=True),
    ]
    db.add_all(test_schedules)
    db.commit()

    # ---------------- 生活圈动态 ----------------
    test_posts = [
        Post(
            author_id=1,
            title="失物招领：捡到一张校园卡",
            content="今天在图书馆捡到一张校园卡，失主请联系我",
            category=PostCategory.LOST_FOUND,
            tags="失物招领,校园卡",
            images="[]",
        ),
        Post(
            author_id=2,
            title=None,
            content="周末天气真好，组队去萃英山徒步～",
            category=PostCategory.SHARING,
            tags="徒步,萃英山",
            images="[]",
        ),
    ]
    db.add_all(test_posts)
    db.commit()

    # ---------------- 校园活动（任意用户可发布）----------------
    test_activities = [
        Activity(
            publisher_id=1,
            title="校园马拉松",
            description="一年一度的校园马拉松比赛，欢迎报名",
            organizer="体育部",
            location="榆中校区操场",
            start_time=datetime.now() + timedelta(days=7),
            end_time=datetime.now() + timedelta(days=7, hours=3),
            max_participants=100,
            cover_image="",
        ),
        Activity(
            publisher_id=2,
            title="第十届读书分享会",
            description="带上你最喜欢的一本书，与大家交换阅读体验",
            organizer="学生会文艺部",
            location="一分部图书馆 301",
            start_time=datetime.now() + timedelta(days=3),
            end_time=datetime.now() + timedelta(days=3, hours=2),
            max_participants=30,
            cover_image="",
        ),
    ]
    db.add_all(test_activities)
    db.commit()

    print("✅ 数据库初始化成功！")
    print("\n测试账号：")
    print("用户名: zhangsan / lisi / wangwu，密码: 123456")

except Exception as e:
    print(f"❌ 初始化失败: {e}")
    db.rollback()
    raise
finally:
    db.close()
