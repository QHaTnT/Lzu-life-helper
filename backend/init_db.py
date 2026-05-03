"""
数据库初始化脚本（开发环境）
- 清库重建：drop_all → create_all
- 灌注测试种子数据，覆盖所有模块
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
    # ── 用户 ──────────────────────────────────────────────────
    users = [
        User(student_id="320200001", username="zhangsan", hashed_password=get_password_hash("123456"),
             real_name="张三", phone="13800138001", email="zhangsan@lzu.edu.cn", role=UserRole.STUDENT),
        User(student_id="320200002", username="lisi", hashed_password=get_password_hash("123456"),
             real_name="李四", phone="13800138002", email="lisi@lzu.edu.cn", role=UserRole.STUDENT),
        User(student_id="320200003", username="wangwu", hashed_password=get_password_hash("123456"),
             real_name="王五", phone="13800138003", email="wangwu@lzu.edu.cn", role=UserRole.STUDENT),
        User(student_id="320200004", username="zhaoliu", hashed_password=get_password_hash("123456"),
             real_name="赵六", phone="13800138004", email="zhaoliu@lzu.edu.cn", role=UserRole.STUDENT),
        User(student_id="320200005", username="sunqi", hashed_password=get_password_hash("123456"),
             real_name="孙七", phone="13800138005", email="sunqi@lzu.edu.cn", role=UserRole.STUDENT),
    ]
    db.add_all(users)
    db.commit()

    # ── 二手商品 ──────────────────────────────────────────────
    products = [
        Product(title="高等数学（上下册）", description="同济第七版，九成新，无笔记划线，适合大一新生备用。",
                price=25.0, category=ProductCategory.BOOKS, status=ProductStatus.AVAILABLE, images="[]", seller_id=1),
        Product(title="大学英语四级词汇书", description="朱伟恋练有词，刷了一遍，有少量笔记，不影响使用。",
                price=15.0, category=ProductCategory.BOOKS, status=ProductStatus.AVAILABLE, images="[]", seller_id=2),
        Product(title="二手蓝牙耳机 Sony WH-1000XM4", description="降噪效果极好，续航约 30h，原装充电线和收纳包齐全，成色 9 成新。",
                price=800.0, category=ProductCategory.ELECTRONICS, status=ProductStatus.AVAILABLE, images="[]", seller_id=1),
        Product(title="小米手环 7", description="表盘完好，表带有轻微磨损，电池续航正常，附原装充电器。",
                price=120.0, category=ProductCategory.ELECTRONICS, status=ProductStatus.AVAILABLE, images="[]", seller_id=3),
        Product(title="宿舍小台灯", description="充电款，三档调光，可夹床头，用了一学期，功能完好。",
                price=35.0, category=ProductCategory.DAILY, status=ProductStatus.AVAILABLE, images="[]", seller_id=2),
        Product(title="电热水壶 1.5L", description="宿舍用，烧水快，内胆无水垢，毕业出售。",
                price=30.0, category=ProductCategory.DAILY, status=ProductStatus.AVAILABLE, images="[]", seller_id=4),
        Product(title="羽毛球拍（两支）", description="尤尼克斯入门款，附球包和 3 筒球，适合初学者。",
                price=80.0, category=ProductCategory.SPORTS, status=ProductStatus.AVAILABLE, images="[]", seller_id=3),
        Product(title="自行车（折叠款）", description="大行 P8，骑了两年，刹车和变速正常，适合校内代步。",
                price=350.0, category=ProductCategory.OTHER, status=ProductStatus.AVAILABLE, images="[]", seller_id=5),
    ]
    db.add_all(products)
    db.commit()

    # 商品留言示例
    comments = [
        ProductComment(product_id=1, user_id=2, content="请问还在吗？可以便宜一点吗"),
        ProductComment(product_id=1, user_id=1, content="在的，价格可以商量"),
        ProductComment(product_id=3, user_id=4, content="耳机成色怎么样？有没有划痕"),
        ProductComment(product_id=3, user_id=1, content="外壳完好，头梁有一点点使用痕迹，不明显"),
    ]
    db.add_all(comments)
    db.commit()

    # ── 场馆 ──────────────────────────────────────────────────
    venues = [
        Venue(name="羽毛球馆 A 区", venue_type=VenueType.BADMINTON,
              location="城关校区体育馆一楼", capacity=4, description="共 4 片标准羽毛球场，木地板，灯光良好"),
        Venue(name="乒乓球室", venue_type=VenueType.TABLE_TENNIS,
              location="城关校区体育馆二楼", capacity=8, description="共 8 张乒乓球台，免费借拍"),
        Venue(name="篮球场（室内）", venue_type=VenueType.BASKETBALL,
              location="榆中校区体育馆", capacity=20, description="标准室内篮球场，可容纳 5v5 比赛"),
        Venue(name="公共自习室 301", venue_type=VenueType.CLASSROOM,
              location="城关校区图书馆三楼", capacity=60, description="安静自习区，提供插座和 WiFi"),
    ]
    db.add_all(venues)
    db.commit()

    # 场馆时段（未来 3 天，每天 4 个时段）
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    slots = []
    for vid in range(1, 5):
        for day in range(3):
            date = today + timedelta(days=day)
            for start_h, end_h in [(8, 10), (10, 12), (14, 16), (19, 21)]:
                slots.append(VenueTimeSlot(
                    venue_id=vid, date=date,
                    start_time=f"{start_h:02d}:00", end_time=f"{end_h:02d}:00",
                    capacity=venues[vid-1].capacity, booked_count=0, is_available=True,
                ))
    db.add_all(slots)
    db.commit()

    # ── 校车 ──────────────────────────────────────────────────
    routes = [
        BusRoute(name="城关→榆中", from_campus="城关校区", to_campus="榆中校区", description="途经盘旋路，约 50 分钟"),
        BusRoute(name="榆中→城关", from_campus="榆中校区", to_campus="城关校区", description="途经盘旋路，约 50 分钟"),
    ]
    db.add_all(routes)
    db.commit()

    schedules = [
        BusSchedule(route_id=1, departure_time="07:00", seats=45, weekday_only=True),
        BusSchedule(route_id=1, departure_time="07:30", seats=45, weekday_only=True),
        BusSchedule(route_id=1, departure_time="12:00", seats=45, weekday_only=False),
        BusSchedule(route_id=1, departure_time="12:30", seats=45, weekday_only=False),
        BusSchedule(route_id=1, departure_time="17:30", seats=45, weekday_only=True),
        BusSchedule(route_id=1, departure_time="18:00", seats=45, weekday_only=True),
        BusSchedule(route_id=2, departure_time="07:30", seats=45, weekday_only=True),
        BusSchedule(route_id=2, departure_time="08:00", seats=45, weekday_only=True),
        BusSchedule(route_id=2, departure_time="12:30", seats=45, weekday_only=False),
        BusSchedule(route_id=2, departure_time="13:00", seats=45, weekday_only=False),
        BusSchedule(route_id=2, departure_time="18:00", seats=45, weekday_only=True),
        BusSchedule(route_id=2, departure_time="18:30", seats=45, weekday_only=True),
    ]
    db.add_all(schedules)
    db.commit()

    # ── 生活圈动态 ────────────────────────────────────────────
    posts = [
        Post(author_id=1, title="失物招领：图书馆捡到校园卡",
             content="今天下午在图书馆三楼捡到一张校园卡，卡主请联系我（微信同手机号 13800138001）或到图书馆前台认领。",
             category=PostCategory.LOST_FOUND, tags="失物招领,校园卡", images="[]"),
        Post(author_id=2, title=None,
             content="周末天气真好，组队去萃英山徒步～有没有人一起？下午两点从南门出发 🏔️",
             category=PostCategory.SHARING, tags="徒步,萃英山,周末", images="[]"),
        Post(author_id=3, title="吐槽一下食堂",
             content="榆中校区二食堂的麻辣烫最近越来越贵了，一碗要 18 块，关键还不好吃……大家有没有推荐的平价食堂？",
             category=PostCategory.COMPLAINT, tags="食堂,吐槽", images="[]"),
        Post(author_id=4, title="求助：线性代数期末复习",
             content="线代期末快到了，有没有学长学姐分享一下复习重点？特别是特征值和二次型那块，感觉完全没懂 😭",
             category=PostCategory.QA, tags="线性代数,期末,求助", images="[]"),
        Post(author_id=5, title=None,
             content="社团招新啦！兰大摄影协会正在招募新成员，不需要任何基础，只需要热爱摄影 📷 感兴趣的同学扫码加群！",
             category=PostCategory.SHARING, tags="社团招新,摄影", images="[]"),
        Post(author_id=1, title="失物招领：黑色雨伞",
             content="在第二教学楼 204 教室捡到一把黑色折叠雨伞，失主请联系 13800138001。",
             category=PostCategory.LOST_FOUND, tags="失物招领,雨伞", images="[]"),
    ]
    db.add_all(posts)
    db.commit()

    # 动态评论和点赞
    post_comments = [
        PostComment(post_id=1, user_id=3, content="我上周也丢了校园卡，不知道是不是我的，能描述一下卡号后四位吗"),
        PostComment(post_id=2, user_id=4, content="我去！等我等我，下午两点南门见"),
        PostComment(post_id=3, user_id=1, content="同感，感觉每学期都在涨价……"),
        PostComment(post_id=4, user_id=2, content="特征值重点看相似对角化，二次型重点看正定判断，这两块必考"),
    ]
    db.add_all(post_comments)
    db.commit()

    likes = [
        Like(post_id=2, user_id=1),
        Like(post_id=2, user_id=3),
        Like(post_id=3, user_id=2),
        Like(post_id=3, user_id=4),
        Like(post_id=5, user_id=1),
        Like(post_id=5, user_id=2),
        Like(post_id=5, user_id=3),
    ]
    db.add_all(likes)
    db.commit()

    # ── 校园活动 ──────────────────────────────────────────────
    activities = [
        Activity(publisher_id=5, title="兰大摄影协会 | 春季外拍活动",
                 description="本次外拍地点为兰州黄河风情线，带上你的相机或手机，记录春天的兰州。活动结束后将评选优秀作品展出。",
                 organizer="兰大摄影协会", location="黄河风情线（小西湖广场集合）",
                 start_time=datetime.now() + timedelta(days=5),
                 end_time=datetime.now() + timedelta(days=5, hours=4),
                 max_participants=30, cover_image="", current_participants=8),
        Activity(publisher_id=1, title="第十届读书分享会",
                 description="带上你最喜欢的一本书，与大家交换阅读体验。本次主题：「改变我的一本书」。",
                 organizer="学生会文艺部", location="城关校区图书馆 301 报告厅",
                 start_time=datetime.now() + timedelta(days=3),
                 end_time=datetime.now() + timedelta(days=3, hours=2),
                 max_participants=50, cover_image="", current_participants=15),
        Activity(publisher_id=2, title="校园马拉松报名开始",
                 description="一年一度的校园马拉松，设 5km 和 10km 两个组别，完赛均有纪念品。",
                 organizer="体育部", location="榆中校区操场（起终点）",
                 start_time=datetime.now() + timedelta(days=14),
                 end_time=datetime.now() + timedelta(days=14, hours=3),
                 max_participants=200, cover_image="", current_participants=56),
        Activity(publisher_id=3, title="Python 编程入门工作坊",
                 description="零基础也能学！两小时带你写出第一个 Python 程序，内容包括：变量、循环、函数基础。",
                 organizer="计算机协会", location="城关校区信息科学楼 B201",
                 start_time=datetime.now() + timedelta(days=2),
                 end_time=datetime.now() + timedelta(days=2, hours=2),
                 max_participants=40, cover_image="", current_participants=22),
    ]
    db.add_all(activities)
    db.commit()

    print("✅ 数据库初始化成功！")
    print("\n测试账号（密码均为 123456）：")
    print("  zhangsan / lisi / wangwu / zhaoliu / sunqi")
    print("\n已创建示例数据：")
    print("  二手商品 8 件 | 场馆 4 个 | 校车班次 12 条")
    print("  生活圈动态 6 条 | 活动 4 个")

except Exception as e:
    print(f"❌ 初始化失败: {e}")
    db.rollback()
    raise
finally:
    db.close()
