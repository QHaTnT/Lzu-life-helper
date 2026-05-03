"""
数据库模型定义 - 全关联建模
所有业务表均持有 user_id 外键，关键多对多/报名场景配唯一约束。
"""
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Boolean,
    ForeignKey,
    Enum,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


# ============================================================
# 用户
# ============================================================
class UserRole(str, enum.Enum):
    """用户角色"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20), unique=True, index=True, nullable=False, comment="学号/工号")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), comment="真实姓名")
    phone = Column(String(11), comment="手机号")
    email = Column(String(100), comment="邮箱")
    avatar = Column(String(255), comment="头像URL")
    role = Column(Enum(UserRole), default=UserRole.STUDENT, comment="用户角色")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 反向关系
    products = relationship("Product", back_populates="seller", cascade="all,delete-orphan")
    product_comments = relationship("ProductComment", back_populates="user", cascade="all,delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all,delete-orphan")
    posts = relationship("Post", back_populates="author", cascade="all,delete-orphan")
    post_comments = relationship("PostComment", back_populates="user", cascade="all,delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all,delete-orphan")
    activities_published = relationship(
        "Activity", back_populates="publisher", cascade="all,delete-orphan"
    )
    activity_registrations = relationship(
        "ActivityRegistration", back_populates="user", cascade="all,delete-orphan"
    )


# ============================================================
# 二手市场
# ============================================================
class ProductCategory(str, enum.Enum):
    """商品分类"""
    ELECTRONICS = "electronics"
    BOOKS = "books"
    DAILY = "daily"
    SPORTS = "sports"
    CLOTHING = "clothing"
    OTHER = "other"


class ProductStatus(str, enum.Enum):
    """商品状态"""
    AVAILABLE = "available"
    SOLD = "sold"
    REMOVED = "removed"


class Product(Base):
    """二手商品模型"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, comment="商品标题")
    description = Column(Text, comment="商品描述")
    price = Column(Float, nullable=False, comment="价格")
    category = Column(Enum(ProductCategory), nullable=False, index=True, comment="分类")
    status = Column(Enum(ProductStatus), default=ProductStatus.AVAILABLE, comment="状态")
    images = Column(Text, comment="图片URL列表，JSON格式")
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="卖家ID")
    views = Column(Integer, default=0, comment="浏览次数")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    seller = relationship("User", back_populates="products")
    comments = relationship(
        "ProductComment", back_populates="product", cascade="all,delete-orphan"
    )


class ProductComment(Base):
    """商品留言模型"""
    __tablename__ = "product_comments"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True, comment="商品ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    content = Column(Text, nullable=False, comment="留言内容")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    product = relationship("Product", back_populates="comments")
    user = relationship("User", back_populates="product_comments")


# ============================================================
# 场馆预约
# ============================================================
class VenueType(str, enum.Enum):
    """场馆类型"""
    BASKETBALL = "basketball"
    BADMINTON = "badminton"
    TABLE_TENNIS = "table_tennis"
    SWIMMING = "swimming"
    GYM = "gym"
    CLASSROOM = "classroom"


class Venue(Base):
    """场馆模型"""
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="场馆名称")
    venue_type = Column(Enum(VenueType), nullable=False, comment="场馆类型")
    location = Column(String(200), comment="位置")
    capacity = Column(Integer, comment="容量")
    description = Column(Text, comment="描述")
    is_active = Column(Boolean, default=True, comment="是否开放")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    time_slots = relationship(
        "VenueTimeSlot", back_populates="venue", cascade="all,delete-orphan"
    )


class VenueTimeSlot(Base):
    """场馆时段模型"""
    __tablename__ = "venue_time_slots"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False, index=True, comment="场馆ID")
    date = Column(DateTime, nullable=False, index=True, comment="日期")
    start_time = Column(String(5), nullable=False, comment="开始时间 HH:MM")
    end_time = Column(String(5), nullable=False, comment="结束时间 HH:MM")
    capacity = Column(Integer, nullable=False, comment="容量")
    booked_count = Column(Integer, default=0, comment="已预约数量")
    is_available = Column(Boolean, default=True, comment="是否可预约")

    venue = relationship("Venue", back_populates="time_slots")
    bookings = relationship("Booking", back_populates="time_slot")


class BookingStatus(str, enum.Enum):
    """预约状态"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Booking(Base):
    """预约记录模型"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    time_slot_id = Column(Integer, ForeignKey("venue_time_slots.id"), nullable=False, index=True, comment="时段ID")
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, comment="状态")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    user = relationship("User", back_populates="bookings")
    time_slot = relationship("VenueTimeSlot", back_populates="bookings")


# ============================================================
# 校车
# ============================================================
class BusRoute(Base):
    """校车路线模型"""
    __tablename__ = "bus_routes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="路线名称")
    from_campus = Column(String(50), nullable=False, comment="起点校区")
    to_campus = Column(String(50), nullable=False, comment="终点校区")
    description = Column(Text, comment="路线描述")
    is_active = Column(Boolean, default=True, comment="是否运营")

    schedules = relationship(
        "BusSchedule", back_populates="route", cascade="all,delete-orphan"
    )


class BusSchedule(Base):
    """校车时刻表模型"""
    __tablename__ = "bus_schedules"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("bus_routes.id"), nullable=False, index=True, comment="路线ID")
    departure_time = Column(String(5), nullable=False, comment="发车时间 HH:MM")
    seats = Column(Integer, nullable=False, comment="座位数")
    booked_seats = Column(Integer, default=0, comment="已预订座位数")
    weekday_only = Column(Boolean, default=False, comment="仅工作日")

    route = relationship("BusRoute", back_populates="schedules")


# ============================================================
# 生活圈（朋友圈式动态 + 评论 + 点赞）
# ============================================================
class PostCategory(str, enum.Enum):
    """动态分类"""
    LOST_FOUND = "lost_found"
    COMPLAINT = "complaint"
    ACTIVITY = "activity"
    SHARING = "sharing"
    QA = "qa"
    OTHER = "other"


class Post(Base):
    """生活圈动态模型"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="作者ID")
    title = Column(String(100), comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    category = Column(Enum(PostCategory), nullable=False, index=True, comment="分类")
    images = Column(Text, comment="图片URL列表，JSON格式（最多9张）")
    tags = Column(String(200), comment="标签，逗号分隔")
    views = Column(Integer, default=0, comment="浏览数")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    author = relationship("User", back_populates="posts")
    comments = relationship(
        "PostComment",
        back_populates="post",
        cascade="all,delete-orphan",
        order_by="PostComment.created_at",
    )
    like_records = relationship(
        "Like", back_populates="post", cascade="all,delete-orphan"
    )


class PostComment(Base):
    """动态评论模型"""
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True, comment="动态ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    content = Column(Text, nullable=False, comment="评论内容")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="post_comments")


class Like(Base):
    """点赞记录（User ↔ Post 多对多）"""
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_like_user_post"),
        Index("ix_like_post", "post_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="点赞用户ID")
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, comment="动态ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="点赞时间")

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="like_records")


# ============================================================
# 校园活动
# ============================================================
class Activity(Base):
    """活动模型 - 任意登录用户可发布"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    publisher_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True, comment="发布者ID"
    )
    title = Column(String(100), nullable=False, comment="活动标题")
    description = Column(Text, comment="活动描述")
    organizer = Column(String(100), comment="主办方/社团（可选展示名）")
    location = Column(String(200), comment="活动地点")
    start_time = Column(DateTime, nullable=False, index=True, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    max_participants = Column(Integer, comment="最大参与人数")
    current_participants = Column(Integer, default=0, comment="当前参与人数")
    cover_image = Column(String(255), comment="封面图片")
    is_active = Column(Boolean, default=True, comment="是否有效")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    publisher = relationship("User", back_populates="activities_published")
    registrations = relationship(
        "ActivityRegistration",
        back_populates="activity",
        cascade="all,delete-orphan",
    )


class ActivityRegistration(Base):
    """活动报名模型 - (activity_id, user_id) 唯一防重复报名"""
    __tablename__ = "activity_registrations"
    __table_args__ = (
        UniqueConstraint(
            "activity_id", "user_id", name="uq_activity_user_registration"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(
        Integer, ForeignKey("activities.id"), nullable=False, index=True, comment="活动ID"
    )
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID"
    )
    status = Column(String(20), default="registered", comment="状态")
    created_at = Column(DateTime, default=datetime.utcnow, comment="报名时间")

    activity = relationship("Activity", back_populates="registrations")
    user = relationship("User", back_populates="activity_registrations")
