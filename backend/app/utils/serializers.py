"""
ORM 实例 → 标准 dict 的序列化工具，便于统一响应中嵌入嵌套对象。
所有 datetime 自动 isoformat()，避免 JSONResponse 序列化报错。

【本文件的职责】
把 SQLAlchemy 的 ORM 对象（如 User、Product 等）转换为 Python 字典（dict）。
这个字典可以直接传给 JSONResponse 返回给前端。

【为什么需要单独的序列化函数，而不是直接返回 ORM 对象】
1. ORM 对象包含数据库连接、会话状态等内部信息，直接序列化会报错或泄露敏感数据。
2. ORM 对象的 datetime 类型不能直接被 JSON 序列化（JSON 不认识 Python 的 datetime 对象）。
3. ORM 对象可能包含不需要返回给前端的字段（如 hashed_password 密码哈希）。
4. 前端需要的数据结构和 ORM 对象的结构不一定完全一致（如前端需要嵌套的用户信息）。
5. 序列化函数可以统一处理 None 值、默认值、枚举值转换等细节。

【为什么不使用 Pydantic 模型做序列化】
Pydantic 模型更适合做请求参数校验和响应模型定义，而这里的序列化函数更灵活：
可以处理嵌套关联（如帖子的作者信息）、可选参数（如 is_liked）等场景。
两种方式各有优劣，本项目选择了手动序列化的方式。

【日期时间处理】
所有 datetime 字段都通过 _dt() 函数转换为 ISO 8601 格式的字符串。
ISO 8601 格式如 "2024-01-15T14:30:00"，前端可以直接用 Date 对象解析。
如果不转换，JSONResponse 会报错："Object of type datetime is not JSON serializable"。
"""
from datetime import datetime        # 用于 datetime 类型判断和转换
from typing import Optional, List    # 类型提示：Optional 表示可能为 None，List 表示列表
import json                          # 用于解析 JSON 格式的字符串（如图片列表）

from app.models import (
    User, Product, ProductComment,
    Venue, VenueTimeSlot, Booking,
    BusRoute, BusSchedule,
    Post, PostComment,
    Activity, ActivityRegistration,
)


def _dt(value: Optional[datetime]) -> Optional[str]:
    """
    将 datetime 对象转换为 ISO 8601 格式的字符串。

    【为什么需要这个函数】
    Python 的 datetime 对象不能直接被 JSON 序列化。
    这个函数统一处理所有日期时间字段的转换，避免每个序列化函数都写一遍 try-except。

    【参数】
    value: 可能是 datetime 对象，也可能是 None。

    【返回值】
    - 如果 value 不为 None：返回 "2024-01-15T14:30:00" 格式的字符串。
    - 如果 value 为 None：返回 None（前端收到 null）。

    【为什么用 isoformat() 而不是 strftime("%Y-%m-%d %H:%M:%S")】
    isoformat() 是 Python 内置方法，输出格式是国际标准（ISO 8601），
    前端的 new Date() 可以直接解析。strftime 需要手动指定格式，容易出错。
    """
    return value.isoformat() if value else None


def _images(raw: Optional[str]) -> List[str]:
    """
    将 JSON 格式的图片字符串解析为 Python 列表。

    【为什么图片要单独处理】
    数据库中图片列表存储为 JSON 字符串，如 '["url1.jpg", "url2.jpg"]'。
    前端需要的是 Python 列表（JSON 数组），所以需要解析。

    【参数】
    raw: 数据库中的原始字符串，可能是 JSON 数组字符串，也可能是 None 或空字符串。

    【返回值】
    - 成功解析：返回字符串列表，如 ["url1.jpg", "url2.jpg"]。
    - 解析失败或为空：返回空列表 []。

    【为什么用 try-except 包裹】
    防御性编程：如果数据库中的数据格式不合法（比如不是有效的 JSON），
    直接返回空列表而不是报错，保证程序不会崩溃。
    这在生产环境中很重要——一条脏数据不应该导致整个接口挂掉。
    """
    # 如果 raw 为 None 或空字符串，直接返回空列表。
    if not raw:
        return []
    try:
        # json.loads() 把 JSON 字符串解析为 Python 对象。
        v = json.loads(raw)
        # 额外检查：确保解析结果是列表而不是其他类型（如字符串、数字）。
        # 如果有人在数据库里存了 "hello"（不是 JSON 数组），json.loads 不会报错，
        # 但解析结果是字符串而不是列表，这里做个类型检查。
        return v if isinstance(v, list) else []
    except Exception:
        # 任何异常（包括 JSON 解析错误、类型错误等）都返回空列表。
        # 用 Exception 而不是 JSONDecodeError 是为了兜底所有可能的错误。
        return []


# ---------------- User ----------------
def serialize_user_brief(user: User) -> dict:
    """
    用户精简卡片：嵌入到帖子、评论等场景中的用户基本信息。

    【为什么需要"精简版"和"完整版"两个序列化函数】
    - 精简版（brief）：只包含少量字段（id、用户名、头像），用于嵌套展示。
      例如帖子列表中显示"谁发的"，只需要用户名和头像，不需要手机号、邮箱等隐私信息。
    - 完整版（serialize_user）：包含所有字段，用于用户个人主页等场景。

    【为什么不能直接用 serialize_user 嵌套】
    1. 完整版包含密码哈希等敏感字段，嵌套到帖子中会泄露。
    2. 完整版数据量大，嵌套到列表中会增加响应体积，影响性能。

    【参数】
    user: User ORM 对象。

    【返回值】
    包含 5 个字段的字典，或 None（如果 user 为 None）。
    """
    # 如果 user 为 None（如匿名用户发布的帖子），返回 None。
    # 这种情况在数据库关联查询中可能出现（如 LEFT JOIN 时右表无数据）。
    if not user:
        return None
    return {
        "id": user.id,                        # 用户 ID：前端用于生成链接、头像地址等
        "username": user.username,             # 用户名：展示用
        "real_name": user.real_name,           # 真实姓名：展示用
        "avatar": user.avatar or "",           # 头像 URL：如果为 None 则返回空字符串
        # 为什么 avatar 用 "or ''" 而不是直接用 user.avatar？
        # 因为前端通常用 <img src="avatar"> 渲染头像，如果 src 为 null 会显示 broken image。
        # 空字符串 "" 虽然也不会显示图片，但至少不会报错，前端可以显示默认头像。
        "phone": user.phone or "",             # 手机号：同理，为 None 时返回空字符串。
    }


def serialize_user(user: User) -> dict:
    """
    用户完整信息：用于个人主页、设置页面等需要展示所有信息的场景。

    【和 serialize_user_brief 的区别】
    多了 student_id、email、role、is_active、created_at 等字段。
    注意：这个函数不返回 hashed_password，因为密码哈希绝对不能返回给前端。
    """
    return {
        "id": user.id,
        "student_id": user.student_id,        # 学号：完整版才展示
        "username": user.username,
        "real_name": user.real_name,
        "phone": user.phone,
        "email": user.email,                   # 邮箱：完整版才展示
        "avatar": user.avatar or "",
        # role 字段的处理：
        # user.role 是一个 Enum 对象（如 UserRole.STUDENT），不是字符串。
        # 如果直接返回 Enum 对象，JSON 序列化会报错。
        # hasattr(user.role, "value") 检查是否有 value 属性（Enum 对象有），
        # 如果有就取 .value（如 "student"），否则直接返回原值。
        # 这样做是为了兼容可能的非 Enum 值（防御性编程）。
        "role": user.role.value if hasattr(user.role, "value") else user.role,
        "is_active": user.is_active,           # 账号是否激活
        "created_at": _dt(user.created_at),    # 注册时间：用 _dt() 转换格式
    }


# ---------------- Product ----------------
def serialize_product(product: Product) -> dict:
    """
    商品信息序列化。

    【特殊处理】
    - images 字段：从 JSON 字符串解析为列表（通过 _images 函数）。
    - seller 字段：嵌套序列化卖家信息（通过 serialize_user_brief）。
    - category 和 status 字段：从 Enum 对象提取 .value 字符串。
    """
    return {
        "id": product.id,
        "title": product.title,
        "description": product.description,
        "price": product.price,
        # category 和 status 都是 Enum 类型，需要转换为字符串。
        # hasattr 检查是为了防御性编程，防止传入非 Enum 类型时出错。
        "category": product.category.value if hasattr(product.category, "value") else product.category,
        "status": product.status.value if hasattr(product.status, "value") else product.status,
        # images 从 JSON 字符串解析为列表。
        "images": _images(product.images),
        "seller_id": product.seller_id,
        # 嵌套序列化卖家信息：前端展示商品时需要显示"卖家是谁"。
        # 如果 seller 关联对象不存在（如卖家已删除），返回 None。
        # 为什么用 if product.seller 而不是 try-except？
        # 因为 SQLAlchemy 的 lazy loading 会自动处理关联对象，
        # 如果 seller_id 指向的用户不存在，seller 为 None。
        "seller": serialize_user_brief(product.seller) if product.seller else None,
        "views": product.views,
        "created_at": _dt(product.created_at),
        "updated_at": _dt(product.updated_at),
    }


def serialize_product_comment(comment: ProductComment) -> dict:
    """
    商品留言序列化。

    【嵌套用户信息的原因】
    前端展示留言列表时需要显示"谁说的"，所以需要嵌套用户信息。
    而不是只返回 user_id 让前端再发一次请求查询用户信息（那样会增加网络开销）。
    """
    return {
        "id": comment.id,
        "product_id": comment.product_id,
        "user_id": comment.user_id,
        # 嵌套留言者的基本信息。
        "user": serialize_user_brief(comment.user) if comment.user else None,
        "content": comment.content,
        "created_at": _dt(comment.created_at),
    }


# ---------------- Venue ----------------
def serialize_venue(venue: Venue) -> dict:
    """
    场馆信息序列化。

    【注意】
    这个函数只序列化场馆基本信息，不包含时段信息。
    时段信息需要单独查询（因为一个场馆有很多时段，不需要每次都全部返回）。
    """
    return {
        "id": venue.id,
        "name": venue.name,
        # venue_type 是 Enum 类型，转换为字符串。
        "venue_type": venue.venue_type.value if hasattr(venue.venue_type, "value") else venue.venue_type,
        "location": venue.location,
        "capacity": venue.capacity,
        "description": venue.description,
        "is_active": venue.is_active,
    }


def serialize_time_slot(slot: VenueTimeSlot) -> dict:
    """
    场馆时段信息序列化。

    【和 serialize_venue 的关系】
    时段是场馆的子数据，通常在查看场馆详情或预约页面时一起返回。
    """
    return {
        "id": slot.id,
        "venue_id": slot.venue_id,
        # date 字段用 _dt() 转换为 ISO 格式字符串。
        "date": _dt(slot.date),
        "start_time": slot.start_time,     # 已经是字符串格式 "HH:MM"，不需要转换
        "end_time": slot.end_time,
        "capacity": slot.capacity,
        "booked_count": slot.booked_count,
        "is_available": slot.is_available,
    }


def serialize_booking(booking: Booking) -> dict:
    """
    预约记录序列化。

    【嵌套了两层关联对象】
    - booking.time_slot：预约对应的时段信息。
    - booking.time_slot.venue：时段对应的场馆信息。
    这样前端一次请求就能拿到完整的预约信息（哪个场馆的哪个时段）。
    """
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "time_slot_id": booking.time_slot_id,
        # status 是 Enum 类型，转换为字符串。
        "status": booking.status.value if hasattr(booking.status, "value") else booking.status,
        "created_at": _dt(booking.created_at),
        # 嵌套时段信息。
        "time_slot": serialize_time_slot(booking.time_slot) if booking.time_slot else None,
        # 嵌套场馆信息：需要先有时段，再从时段中获取场馆。
        # 为什么用 and 链式判断？因为 time_slot 可能为 None，此时访问 .venue 会报错。
        "venue": serialize_venue(booking.time_slot.venue) if booking.time_slot and booking.time_slot.venue else None,
    }


# ---------------- Bus ----------------
def serialize_bus_route(route: BusRoute) -> dict:
    """
    校车路线信息序列化。
    """
    return {
        "id": route.id,
        "name": route.name,
        "from_campus": route.from_campus,
        "to_campus": route.to_campus,
        "description": route.description,
        "is_active": route.is_active,
    }


def serialize_bus_schedule(s: BusSchedule) -> dict:
    """
    校车班次信息序列化。

    【为什么参数名用 s 而不是 schedule】
    纯粹是为了简洁，避免过长的参数名。函数内部只用到这个参数几次，短名不影响可读性。
    """
    return {
        "id": s.id,
        "route_id": s.route_id,
        "departure_time": s.departure_time,
        "seats": s.seats,
        "booked_seats": s.booked_seats,
        "weekday_only": s.weekday_only,
    }


# ---------------- Post ----------------
def serialize_post(
    post: Post,
    *,
    like_count: int = 0,
    comment_count: int = 0,
    is_liked: bool = False,
) -> dict:
    """
    生活圈动态信息序列化。

    【为什么用 * 分隔参数】
    * 号之后的参数（like_count、comment_count、is_liked）只能用关键字参数传递。
    例如：serialize_post(post, like_count=5, is_liked=True)。
    这样做的好处是：
    1. 这些参数有默认值，调用时可以省略。
    2. 不会和 post 参数混淆（positional vs keyword）。

    【like_count 和 comment_count 为什么不直接从 ORM 对象获取】
    因为这两个值需要额外查询（如 SELECT COUNT(*) FROM likes WHERE post_id=?），
    在序列化函数中做额外查询不合适（违反单一职责原则）。
    由 Service 层查询后传入更合理。

    【is_liked 的作用】
    标记当前用户是否已经点赞了这条动态。前端据此显示"已赞"或"未赞"按钮。
    这个值取决于当前登录用户，同一个动态对不同用户返回不同的 is_liked 值。
    """
    return {
        "id": post.id,
        "author_id": post.author_id,
        # 嵌套作者信息。
        "author": serialize_user_brief(post.author) if post.author else None,
        "title": post.title,
        "content": post.content,
        # category 是 Enum 类型，转换为字符串。
        "category": post.category.value if hasattr(post.category, "value") else post.category,
        "tags": post.tags,
        # images 从 JSON 字符串解析为列表。
        "images": _images(post.images),
        "views": post.views,
        # like_count 和 comment_count 由调用方传入。
        "like_count": like_count,
        "comment_count": comment_count,
        # is_liked 由调用方传入，标记当前用户是否已点赞。
        "is_liked": is_liked,
        "created_at": _dt(post.created_at),
        "updated_at": _dt(post.updated_at),
    }


def serialize_post_comment(comment: PostComment) -> dict:
    """
    动态评论序列化。
    和 serialize_product_comment 结构类似，但关联的是 Post 而不是 Product。
    """
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "user_id": comment.user_id,
        "user": serialize_user_brief(comment.user) if comment.user else None,
        "content": comment.content,
        "created_at": _dt(comment.created_at),
    }


# ---------------- Activity ----------------
def serialize_activity(
    activity: Activity,
    *,
    is_registered: bool = False,
) -> dict:
    """
    活动信息序列化。

    【is_registered 参数的作用】
    标记当前用户是否已经报名了这个活动。前端据此显示"已报名"或"立即报名"按钮。
    和 serialize_post 中的 is_liked 逻辑一样：取决于当前登录用户。
    """
    return {
        "id": activity.id,
        "publisher_id": activity.publisher_id,
        # 嵌套发布者信息。
        "publisher": serialize_user_brief(activity.publisher) if activity.publisher else None,
        "title": activity.title,
        "description": activity.description,
        "organizer": activity.organizer,
        "location": activity.location,
        # 活动时间用 _dt() 转换。
        "start_time": _dt(activity.start_time),
        "end_time": _dt(activity.end_time),
        "max_participants": activity.max_participants,
        "current_participants": activity.current_participants,
        "cover_image": activity.cover_image or "",  # 为 None 时返回空字符串
        "is_active": activity.is_active,
        # is_registered 由调用方传入。
        "is_registered": is_registered,
        "created_at": _dt(activity.created_at),
    }


def serialize_activity_registration(reg: ActivityRegistration) -> dict:
    """
    活动报名记录序列化。

    【status 字段没有用 Enum】
    和其他状态字段不同，ActivityRegistration 的 status 是 String 类型（不是 Enum），
    所以不需要 hasattr 检查和 .value 提取，直接返回即可。
    """
    return {
        "id": reg.id,
        "activity_id": reg.activity_id,
        "user_id": reg.user_id,
        # 嵌套报名者的基本信息。
        "user": serialize_user_brief(reg.user) if reg.user else None,
        "status": reg.status,    # 直接返回字符串，不需要 .value 转换
        "created_at": _dt(reg.created_at),
    }
