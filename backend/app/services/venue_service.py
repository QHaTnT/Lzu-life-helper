"""
场馆预约服务 - 核心业务逻辑

【本文件的职责】
处理场馆预约相关的所有业务逻辑，包括：
1. 查询空闲时段
2. 创建预约（含并发控制）
3. 取消预约
4. 查询用户预约记录

【为什么业务逻辑要放在 Service 层而不是直接写在路由里】
1. 路由（Router）只负责接收 HTTP 请求和返回响应，不应该包含复杂业务逻辑。
2. Service 层可以被多个路由复用（如创建预约的逻辑可以被不同入口调用）。
3. Service 层更容易测试（不需要启动 HTTP 服务器）。
4. 分层架构让代码职责清晰：路由管"怎么通信"，Service 管"怎么做事"。

【并发控制的重要性】
场馆预约是典型的"竞争资源"场景：多个用户可能同时预约同一个时段。
如果不做并发控制，可能出现"超卖"：时段只剩 1 个名额，但两个人同时预约成功了。
本文件使用 Redis 分布式锁 + MySQL 行锁双重保障来解决这个问题。
"""
from datetime import datetime, timedelta
from typing import List, Optional          # 用于类型提示，让代码更易读
from sqlalchemy.orm import Session          # 数据库会话对象，代表一次数据库连接
from sqlalchemy import and_                 # 用于组合多个查询条件
from app.models import Venue, VenueTimeSlot, Booking, BookingStatus  # 数据模型
from app.core.config import settings        # 应用配置（如预约天数限制、锁超时时间等）


class VenueService:
    """场馆预约服务类，所有方法都是静态方法，不需要实例化。"""

    @staticmethod
    def get_available_time_slots(
        db: Session, venue_id: int, days: int = None
    ) -> List[VenueTimeSlot]:
        """
        获取场馆未来 N 天的空闲时段。

        【参数说明】
        - db: 数据库会话，由路由层传入，用于执行数据库查询。
        - venue_id: 场馆 ID，指定要查哪个场馆。
        - days: 查询未来几天，默认从配置文件读取。

        【为什么用 @staticmethod】
        静态方法不需要访问实例属性（self），这个方法只需要数据库和参数就能工作，
        所以用静态方法更简洁。如果需要访问类级别的配置，也可以用类方法。

        【返回值】
        返回一个 VenueTimeSlot 对象列表，前端可以直接使用这些对象的属性。
        """
        # 如果没有指定天数，从配置文件读取默认值。
        # 为什么不硬编码？因为不同环境（开发/测试/生产）可能需要不同的天数限制。
        if days is None:
            days = settings.VENUE_BOOKING_DAYS

        # 计算查询的起止日期。
        # replace(hour=0, minute=0, second=0, microsecond=0) 把时间归零到当天 00:00:00。
        # 为什么要归零？因为数据库中 date 字段存的是日期（时分秒为 00:00:00），
        # 如果当前时间是 14:30，start_date 不归零的话就无法匹配到今天的时段。
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # end_date 是 start_date 之后 N 天，用 < 而不是 <=，确保包含今天但不包含 N+1 天。
        end_date = start_date + timedelta(days=days)

        # 构建查询：从 venue_time_slots 表中筛选符合条件的时段。
        time_slots = (
            db.query(VenueTimeSlot)
            .filter(
                and_(
                    # 条件1：指定场馆的时段
                    VenueTimeSlot.venue_id == venue_id,
                    # 条件2：日期在今天（含）到 N 天之内
                    VenueTimeSlot.date >= start_date,
                    VenueTimeSlot.date < end_date,
                    # 条件3：时段标记为可预约
                    # 为什么用 == True 而不是直接用 is_available？
                    # 因为 SQLAlchemy 的 filter 需要用 == 比较，Python 的 is 语法不适用。
                    VenueTimeSlot.is_available == True,
                    # 条件4：已预约数量小于容量（还有空位）
                    # 这是双重保险：即使 is_available 没有及时更新，这个条件也能过滤掉满员时段。
                    VenueTimeSlot.booked_count < VenueTimeSlot.capacity,
                )
            )
            # 按日期和开始时间排序：先按日期升序，同一天内按时间升序。
            # 这样前端展示时就是按时间顺序排列的，用户体验更好。
            .order_by(VenueTimeSlot.date, VenueTimeSlot.start_time)
            .all()
        )

        return time_slots

    @staticmethod
    def create_booking_with_lock(
        db: Session, user_id: int, time_slot_id: int
    ) -> Optional[Booking]:
        """
        创建预约（Redis 分布式锁 + MySQL 行锁双重保障）。

        【并发问题分析】
        假设时段 A 只剩 1 个名额，用户 X 和用户 Y 同时点击预约：
        - 如果没有并发控制：两个请求都读到 booked_count=3, capacity=4，
          都执行 booked_count += 1，最终 booked_count=5，超过了 capacity=4，这就是"超卖"。
        - 解决方案：用锁确保同一时刻只有一个请求能操作这个时段。

        【双重锁的设计思路】
        - Redis 分布式锁：拦截大部分并发请求，只让一个请求进入。
          适用于多个服务器实例部署的场景（多进程/多机器）。
        - MySQL 行锁（SELECT ... FOR UPDATE）：在数据库层面二次保证，
          即使 Redis 锁失效（如 Redis 宕机），数据库锁也能防止数据不一致。

        【参数说明】
        - db: 数据库会话。
        - user_id: 当前用户的 ID。
        - time_slot_id: 要预约的时段 ID。

        【返回值】
        - 成功：返回 Booking 对象。
        - 失败（时段不存在/已满/已预约/锁未获取）：返回 None。
        """
        # 延迟导入 redis_client：不在文件顶部导入，而是在函数内部导入。
        # 为什么？因为如果 Redis 服务不可用，文件顶部导入会导致整个模块无法加载。
        # 在函数内部导入，只在需要时才加载，Redis 挂了也不影响其他功能。
        from app.core.redis import redis_client

        # ── 第一步：获取 Redis 分布式锁 ──
        # 锁的 key：标识"这个时段正在被操作"。
        # 格式 "booking_lock:{时段ID}"，不同时段用不同的锁，互不影响。
        lock_key = f"booking_lock:{time_slot_id}"
        # 锁的 value：记录是谁在操作、什么时间操作的。
        # 用于日志追踪和防止误删别人的锁（虽然下面的 delete 没用到，但保留是个好习惯）。
        lock_value = f"{user_id}:{datetime.now().timestamp()}"
        # 锁的超时时间：从配置文件读取。
        # 为什么需要超时？如果获取锁的进程崩溃了，没有释放锁，
        # 其他进程就会永远等待。设置超时后，锁会自动释放。
        lock_timeout = settings.VENUE_BOOKING_LOCK_TIMEOUT

        # set(nx=True) 是 Redis 的"原子性设置"操作：
        # 只有当 key 不存在时才设置，返回 True；key 已存在则返回 False。
        # 这保证了多个进程竞争时只有一个能成功设置。
        # ex=lock_timeout 设置过期时间（秒），到期自动删除 key。
        lock_acquired = redis_client.set(lock_key, lock_value, nx=True, ex=lock_timeout)
        # 如果没有获取到锁，说明有其他请求正在操作这个时段，直接返回 None。
        # 前端收到 None 后可以提示"请稍后重试"。
        if not lock_acquired:
            return None

        try:
            # ── 第二步：获取 MySQL 行锁 ──
            # .with_for_update() 是 SQL 的 SELECT ... FOR UPDATE 语法。
            # 它会锁定查询到的行，其他事务如果要修改同一行，必须等待当前事务完成。
            # 这是数据库层面的锁，比 Redis 锁更可靠（数据库事务有 ACID 保证）。
            # 为什么要先查再改？因为需要先确认时段是否存在、是否有空位。
            time_slot = (
                db.query(VenueTimeSlot)
                .filter(VenueTimeSlot.id == time_slot_id)
                .with_for_update()
                .first()
            )

            # 时段不存在（可能已被删除），返回 None。
            if not time_slot:
                return None

            # 时段已满（已预约数 >= 容量），无法预约，返回 None。
            if time_slot.booked_count >= time_slot.capacity:
                return None

            # ── 第三步：检查是否已经预约过 ──
            # 查询该用户是否已经对这个时段有"待确认"或"已确认"的预约。
            # 为什么要检查？防止同一个人重复预约同一个时段。
            # status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]) 表示
            # 只检查有效预约，已取消的不算。
            existing_booking = (
                db.query(Booking)
                .filter(
                    and_(
                        Booking.user_id == user_id,
                        Booking.time_slot_id == time_slot_id,
                        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                    )
                )
                .first()
            )

            # 如果已经预约过，返回 None。
            if existing_booking:
                return None

            # ── 第四步：创建预约记录 ──
            # 创建一个新的 Booking 对象，状态为 CONFIRMED（已确认）。
            # 为什么不是 PENDING？因为这里是直接确认（没有人工审核环节）。
            booking = Booking(
                user_id=user_id,
                time_slot_id=time_slot_id,
                status=BookingStatus.CONFIRMED,
            )
            # db.add() 把新记录加入会话，但还没有写入数据库。
            # 实际写入是在 db.commit() 时。
            db.add(booking)

            # ── 第五步：更新时段的已预约数量 ──
            # booked_count 加 1。
            time_slot.booked_count += 1
            # 如果已预约数量达到容量上限，把 is_available 设为 False。
            # 这样其他用户查询时就看不到这个时段了（在 get_available_time_slots 中被过滤）。
            if time_slot.booked_count >= time_slot.capacity:
                time_slot.is_available = False

            # ── 第六步：提交事务 ──
            # db.commit() 把上面所有操作（新增预约 + 更新时段）一次性写入数据库。
            # 事务保证了原子性：要么全部成功，要么全部回滚。
            db.commit()
            # db.refresh() 从数据库重新读取 booking 对象的数据（包括自增 id、默认时间等）。
            # 因为 commit 之后，数据库可能填充了一些默认值（如 id、created_at），
            # 这些值在 Python 对象上还是空的，refresh 可以同步回来。
            db.refresh(booking)
            return booking

        finally:
            # ── 第七步：释放 Redis 锁 ──
            # finally 块无论 try 中是否发生异常，都会执行。
            # 这确保了即使业务逻辑出错，锁也一定会被释放，
            # 不会导致其他请求永远获取不到锁。
            # delete(lock_key) 直接删除 key，释放锁。
            redis_client.delete(lock_key)

    @staticmethod
    def cancel_booking(db: Session, booking_id: int, user_id: int) -> bool:
        """
        取消预约。

        【参数说明】
        - db: 数据库会话。
        - booking_id: 要取消的预约记录 ID。
        - user_id: 当前用户的 ID（用于验证权限，只能取消自己的预约）。

        【返回值】
        - True: 取消成功。
        - False: 预约不存在或不属于当前用户。

        【为什么取消预约不需要加锁】
        取消预约是"减少"操作（booked_count - 1），不会导致超卖。
        而且取消操作通常是单用户的（只有自己能取消自己的预约），并发冲突概率低。
        如果未来需要高并发取消（如批量取消），可以考虑加锁。
        """
        # 查询预约记录：必须同时满足三个条件才查得到。
        booking = (
            db.query(Booking)
            .filter(
                and_(
                    # 条件1：预约 ID 匹配
                    Booking.id == booking_id,
                    # 条件2：必须是自己的预约（权限控制）
                    # 为什么不在查到之后再判断 user_id？因为在查询时就加上条件更安全，
                    # 防止通过其他途径（如 API 漏洞）取消别人的预约。
                    Booking.user_id == user_id,
                    # 条件3：只能取消"待确认"或"已确认"的预约
                    # 已完成或已取消的预约不能再取消。
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                )
            )
            .first()
        )

        # 预约不存在或无权取消，返回 False。
        if not booking:
            return False

        # 更新预约状态为"已取消"。
        booking.status = BookingStatus.CANCELLED

        # 查询对应的时段，释放名额。
        time_slot = db.query(VenueTimeSlot).filter(
            VenueTimeSlot.id == booking.time_slot_id
        ).first()

        if time_slot:
            # booked_count 减 1，但最小为 0（防止出现负数）。
            # max(0, ...) 是防御性编程：即使 booked_count 已经是 0（理论上不应该），
            # 也不会变成负数。
            time_slot.booked_count = max(0, time_slot.booked_count - 1)
            # 释放名额后，把 is_available 重新设为 True。
            # 之前如果因为满员被设为 False，现在有空位了，应该重新开放。
            time_slot.is_available = True

        # 提交事务：预约状态变更 + 时段名额更新，一起提交。
        db.commit()
        return True

    @staticmethod
    def get_user_bookings(
        db: Session, user_id: int, status: Optional[str] = None
    ) -> List[Booking]:
        """
        获取用户的预约记录。

        【参数说明】
        - db: 数据库会话。
        - user_id: 用户 ID。
        - status: 可选的状态筛选，如 "confirmed" 只查已确认的预约。
          如果为 None，则查询所有状态的预约。

        【为什么支持可选的状态筛选】
        前端可能需要不同页面展示不同状态的预约：
        - "我的预约"页面：显示所有状态
        - "即将到来"页面：只显示 confirmed 状态
        - "历史预约"页面：只显示 completed 或 cancelled 状态
        通过 status 参数可以一次接口满足多种需求。

        【返回值】
        返回按创建时间倒序排列的预约列表（最新的在前面）。
        """
        # 先构建基础查询：只查当前用户的预约。
        query = db.query(Booking).filter(Booking.user_id == user_id)

        # 如果指定了状态，追加状态过滤条件。
        # 这种"先构建查询，再按需添加条件"的模式叫"查询构建器模式"，
        # 比用一大堆 if-else 拼 SQL 更优雅。
        if status:
            query = query.filter(Booking.status == status)

        # 按创建时间倒序：最新的预约排在最前面，用户体验更好。
        # .all() 执行查询并返回所有结果。
        bookings = query.order_by(Booking.created_at.desc()).all()
        return bookings
