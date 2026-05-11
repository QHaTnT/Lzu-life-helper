"""
数据库初始化脚本（开发环境）
- 清库重建：drop_all → create_all
- 灌注测试种子数据，覆盖所有模块

【本文件的职责】
在开发阶段快速初始化数据库：删除所有旧表、创建新表、插入测试数据。
运行方式：在 backend 目录下执行 python init_db.py。

【为什么需要种子数据】
1. 新开发者加入项目时，不需要手动在界面上一条条添加数据来测试。
2. 前端开发者需要后端返回有意义的数据来调试页面。
3. 演示项目时需要有完整的数据来展示所有功能。
4. 自动化测试可以基于固定的种子数据编写断言。

【安全警告】
这个脚本会删除所有数据！只应在开发环境使用，绝对不能在生产环境运行。
生产环境应该用数据库迁移工具（如 Alembic）来管理表结构变更。
"""
from datetime import datetime, timedelta           # 日期时间操作
from app.core.database import SessionLocal, engine, Base  # 数据库连接相关
from app.models import (
    # 用户相关
    User, UserRole,
    # 二手市场相关
    Product, ProductCategory, ProductStatus,
    ProductComment,
    # 场馆预约相关
    Venue, VenueType, VenueTimeSlot,
    # 校车相关
    BusRoute, BusSchedule,
    # 生活圈相关
    Post, PostCategory, PostComment, Like,
    # 活动相关
    Activity, ActivityRegistration,
)
from app.core.security import get_password_hash  # 密码哈希函数

# ── 第一步：清空旧表并重建 ──
print("🧹 正在清空旧表 ...")
# drop_all(bind=engine) 删除数据库中所有由 Base 定义的表。
# 为什么用 drop_all 而不是只创建不存在的表？
# 因为如果表结构有变化（如新增列），旧表不会自动更新，
# drop_all + create_all 可以确保表结构和代码完全一致。
# 注意：这会删除所有数据！
Base.metadata.drop_all(bind=engine)

print("🛠️  正在创建新表结构 ...")
# create_all(bind=engine) 根据 Base 上定义的所有模型类创建表。
# 如果表已经存在，create_all 不会报错（也不会修改已有的表）。
# 所以上面必须先 drop_all 清空。
Base.metadata.create_all(bind=engine)

# 创建数据库会话：后续所有数据库操作都通过这个会话执行。
# SessionLocal 是一个会话工厂，每次调用都会创建一个新的会话。
db = SessionLocal()

try:
    # ── 用户 ──────────────────────────────────────────────────
    # 创建 5 个测试用户，覆盖"学生"角色。
    # 为什么是 5 个？因为需要足够的用户来模拟社交互动：
    # - 有人发布商品，有人评论
    # - 有人发帖，有人点赞
    # - 有人报名活动
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
    # 为什么所有用户的密码都是 "123456"？
    # 这是测试数据，密码统一方便记忆和登录测试。
    # 绝不能在生产环境使用简单密码。

    # add_all() 一次性把所有用户对象加入会话（还没写入数据库）。
    db.add_all(users)
    # commit() 把会话中的所有操作一次性提交到数据库。
    # 为什么分批 commit 而不是最后一起提交？
    # 因为后续的数据（如商品）需要引用用户的 id（外键），
    # 必须先 commit 用户数据，数据库才会生成自增 id。
    db.commit()

    # ── 二手商品 ──────────────────────────────────────────────
    # 创建 8 个二手商品，覆盖所有分类（电子、书籍、日用、运动、其他）。
    # 为什么是 8 个？因为需要足够多的商品来测试列表分页、分类筛选等功能。
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
    # images="[]" 表示没有图片（空 JSON 数组字符串）。
    # 因为测试数据不需要真实图片，用空数组即可。
    # seller_id 引用的是 users 表的 id（1-5 对应上面创建的 5 个用户）。
    db.add_all(products)
    db.commit()

    # ── 商品留言示例 ──
    # 创建 4 条商品留言，模拟买家咨询场景。
    # 为什么只有 4 条？因为种子数据够用就行，太多反而影响维护。
    # 注意 user_id=1 的用户同时发布了商品（seller_id=1）又回复了留言，
    # 这模拟了"卖家回复买家咨询"的场景。
    comments = [
        ProductComment(product_id=1, user_id=2, content="请问还在吗？可以便宜一点吗"),
        ProductComment(product_id=1, user_id=1, content="在的，价格可以商量"),
        ProductComment(product_id=3, user_id=4, content="耳机成色怎么样？有没有划痕"),
        ProductComment(product_id=3, user_id=1, content="外壳完好，头梁有一点点使用痕迹，不明显"),
    ]
    db.add_all(comments)
    db.commit()

    # ── 场馆 ──────────────────────────────────────────────────
    # 创建 4 个场馆，覆盖所有类型（羽毛球、乒乓球、篮球、教室）。
    # capacity 是场馆同时可容纳的场次数/人数。
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

    # ── 场馆时段（未来 3 天，每天 4 个时段） ──
    # 为每个场馆生成未来 3 天的可预约时段。
    # 为什么是 3 天？因为用户通常只预约近期的场馆，太远的时段没有意义。
    # 为什么每天 4 个时段？这是产品设计决定的，模拟学校场馆的实际开放时间。
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # 归零到当天 00:00:00，确保日期部分准确。
    slots = []
    # vid 从 1 到 4，对应上面创建的 4 个场馆的 id。
    for vid in range(1, 5):
        # day 从 0 到 2，表示今天、明天、后天。
        for day in range(3):
            date = today + timedelta(days=day)
            # 4 个时段：上午两段（8-10、10-12），下午一段（14-16），晚上一段（19-21）。
            # 为什么跳过 12-14？因为这是午休时间，场馆通常不开放。
            # 为什么跳过 21 点以后？因为学校有熄灯/闭馆时间。
            for start_h, end_h in [(8, 10), (10, 12), (14, 16), (19, 21)]:
                slots.append(VenueTimeSlot(
                    venue_id=vid, date=date,
                    # start_time 和 end_time 用字符串格式 "HH:MM"。
                    # f"{start_h:02d}:00" 把整数格式化为两位数，如 8 -> "08"。
                    start_time=f"{start_h:02d}:00", end_time=f"{end_h:02d}:00",
                    # capacity 从对应场馆复制过来。
                    # venues[vid-1] 是因为列表索引从 0 开始，而 vid 从 1 开始。
                    capacity=venues[vid-1].capacity,
                    booked_count=0,  # 新时段没有预约
                    is_available=True,  # 新时段可预约
                ))
    # 总共 4 个场馆 × 3 天 × 4 个时段 = 48 个时段记录。
    db.add_all(slots)
    db.commit()

    # ── 校车 ──────────────────────────────────────────────────
    # 创建 2 条校车路线：城关到榆中、榆中到城关。
    # 为什么是这两条？因为兰州大学有两个主要校区，学生经常需要往返。
    routes = [
        BusRoute(name="城关→榆中", from_campus="城关校区", to_campus="榆中校区", description="途经盘旋路，约 50 分钟"),
        BusRoute(name="榆中→城关", from_campus="榆中校区", to_campus="城关校区", description="途经盘旋路，约 50 分钟"),
    ]
    db.add_all(routes)
    db.commit()

    # 为每条路线创建 6 个班次，共 12 个班次。
    # 为什么是 6 个？模拟真实校车运营：早高峰 2 班、中午 2 班、晚高峰 2 班。
    # weekday_only 的设计：
    # - 早高峰（7:00-8:00）和晚高峰（17:30-18:30）只在工作日运行，
    #   因为周末学生通常不需要赶早课。
    # - 中午（12:00-13:00）每天都运行，因为周末也有学生在两个校区之间活动。
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
    # seats=45 模拟 45 座大巴。
    # booked_seats 默认为 0，新班次没有预订。
    db.add_all(schedules)
    db.commit()

    # ── 生活圈动态 ────────────────────────────────────────────
    # 创建 6 条动态，覆盖所有分类（失物招领、分享、吐槽、问答）。
    # 为什么是 6 条？需要足够多的帖子来测试列表分页、分类筛选、点赞等功能。
    posts = [
        Post(author_id=1, title="失物招领：图书馆捡到校园卡",
             content="今天下午在图书馆三楼捡到一张校园卡，卡主请联系我（微信同手机号 13800138001）或到图书馆前台认领。",
             category=PostCategory.LOST_FOUND, tags="失物招领,校园卡", images="[]"),
        # title=None 表示这条动态没有标题（纯文字分享，类似朋友圈）。
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
    # 注意 tags 字段用逗号分隔存储，如 "失物招领,校园卡"。
    # 这是简单的标签存储方式，不需要单独的标签表。
    db.add_all(posts)
    db.commit()

    # ── 动态评论和点赞 ──
    # 创建 4 条评论，模拟用户互动。
    # 注意评论内容和帖子内容是相关的（如评论"特征值重点看相似对角化"），
    # 这让测试数据更真实。
    post_comments = [
        PostComment(post_id=1, user_id=3, content="我上周也丢了校园卡，不知道是不是我的，能描述一下卡号后四位吗"),
        PostComment(post_id=2, user_id=4, content="我去！等我等我，下午两点南门见"),
        PostComment(post_id=3, user_id=1, content="同感，感觉每学期都在涨价……"),
        PostComment(post_id=4, user_id=2, content="特征值重点看相似对角化，二次型重点看正定判断，这两块必考"),
    ]
    db.add_all(post_comments)
    db.commit()

    # 创建 7 条点赞记录。
    # 设计思路：
    # - 帖子 2（徒步活动）有 2 个赞，帖子 3（吐槽食堂）有 2 个赞，
    #   帖子 5（社团招新）有 3 个赞。
    # - 用来测试"点赞数统计"和"是否已点赞"功能。
    # - 没有人给自己点赞（合理的行为模式）。
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
    # 创建 4 个活动，覆盖不同类型（外拍、读书会、马拉松、编程工作坊）。
    # 为什么需要活动数据？因为活动模块需要测试发布、列表、报名等功能。
    activities = [
        Activity(publisher_id=5, title="兰大摄影协会 | 春季外拍活动",
                 description="本次外拍地点为兰州黄河风情线，带上你的相机或手机，记录春天的兰州。活动结束后将评选优秀作品展出。",
                 organizer="兰大摄影协会", location="黄河风情线（小西湖广场集合）",
                 # 活动时间设为未来 5 天，确保在测试时活动是"未开始"状态。
                 # 如果设为过去的时间，活动就过期了，无法测试报名功能。
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
    # current_participants 是预设的已报名人数，模拟活动已经开始报名的场景。
    # cover_image="" 表示没有封面图（空字符串而不是 None，避免前端显示 broken image）。
    db.add_all(activities)
    db.commit()

    # 打印初始化成功的摘要信息。
    print("✅ 数据库初始化成功！")
    print("\n测试账号（密码均为 123456）：")
    print("  zhangsan / lisi / wangwu / zhaoliu / sunqi")
    print("\n已创建示例数据：")
    print("  二手商品 8 件 | 场馆 4 个 | 校车班次 12 条")
    print("  生活圈动态 6 条 | 活动 4 个")

except Exception as e:
    # 如果任何一步出错，回滚所有未提交的操作。
    # 为什么需要 rollback？因为上面分多次 commit，如果中间某次失败，
    # 之前 commit 的数据已经在数据库里了，但后续数据不完整。
    # rollback 可以保证要么全部成功，要么全部不提交（虽然已经 commit 的无法回滚，
    # 但至少不会在错误状态下继续操作）。
    print(f"❌ 初始化失败: {e}")
    db.rollback()
    # raise 把异常抛出，让调用者知道初始化失败了。
    raise
finally:
    # 无论成功还是失败，都关闭数据库会话。
    # 为什么在 finally 中关闭？因为数据库连接是有限资源，
    # 不关闭会导致连接池耗尽，后续操作无法连接数据库。
    db.close()
