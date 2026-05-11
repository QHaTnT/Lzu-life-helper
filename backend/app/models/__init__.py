"""
数据库模型定义 - 全关联建模
所有业务表均持有 user_id 外键，关键多对多/报名场景配唯一约束。

【本文件的职责】
本文件是整个后端的"数据字典"，定义了数据库里每张表的结构。
用 SQLAlchemy ORM 框架来定义，这样 Python 代码可以直接操作数据库表，
而不需要手写 SQL 语句。

【为什么用 ORM 而不是直接写 SQL】
1. ORM 让你用 Python 类来表示数据库表，代码更易读、易维护。
2. ORM 自动处理数据库方言差异（MySQL/PostgreSQL/SQLite 语法不同）。
3. ORM 提供类型检查和自动补全，减少运行时错误。
4. ORM 的 relationship 可以自动处理表之间的关联查询，避免手写 JOIN。

【文件结构概览】
- 用户模块：User 表 + UserRole 枚举
- 二手市场：Product 表、ProductComment 表 + 分类/状态枚举
- 场馆预约：Venue 表、VenueTimeSlot 表、Booking 表 + 类型/状态枚举
- 校车模块：BusRoute 表、BusSchedule 表
- 生活圈：Post 表、PostComment 表、Like 表 + 分类枚举
- 校园活动：Activity 表、ActivityRegistration 表
"""
from datetime import datetime
from sqlalchemy import (
    Column,      # 定义表的每一列
    Integer,     # 整数类型，用于主键、外键、计数器等
    String,      # 变长字符串，需要指定最大长度，对应数据库的 VARCHAR
    Text,        # 长文本类型，不限长度，对应数据库的 TEXT
    DateTime,    # 日期时间类型，存储年月日时分秒
    Float,       # 浮点数类型，用于存储价格等数值
    Boolean,     # 布尔类型，存储 True/False，数据库中通常是 TINYINT(1)
    ForeignKey,  # 外键约束，建立表与表之间的关联关系
    Enum,        # 枚举类型，限制字段只能取预定义的值
    UniqueConstraint,  # 唯一约束，确保某列或某组列的值不重复
    Index,       # 索引定义，加速特定列的查询速度
)
from sqlalchemy.orm import relationship  # 用于定义表之间的关联关系，支持双向导航
from app.core.database import Base       # 导入声明式基类，所有模型类都要继承它
import enum                              # Python 标准库的枚举模块，用于定义枚举类


# ============================================================
# 用户
# ============================================================
class UserRole(str, enum.Enum):
    """
    用户角色枚举，定义系统中允许的用户类型。

    【为什么继承 str】
    继承 str 后，枚举值可以直接当字符串使用（例如 UserRole.STUDENT == "student"），
    这样在序列化为 JSON 时不需要额外转换，数据库存储时也直接存字符串值。

    【为什么用枚举而不是普通字符串】
    1. 枚举限制了可选值，防止出现 "stuent"（拼写错误）这种非法值。
    2. 代码中可以用 UserRole.STUDENT 代替 "student"，IDE 能自动补全。
    3. 如果将来要改某个值，只需要改一个地方，不会遗漏。
    """
    STUDENT = "student"   # 学生角色，普通用户，拥有基本功能权限
    TEACHER = "teacher"   # 教师角色，可能拥有发布活动等额外权限
    ADMIN = "admin"       # 管理员角色，拥有后台管理、审核等最高权限


class User(Base):
    """
    用户模型，对应数据库中的 users 表。

    【为什么需要用户表】
    用户表是整个系统的核心，所有业务数据（商品、预约、帖子等）都需要关联到具体用户，
    这样才能实现"谁发布的"、"谁预约的"等业务逻辑。
    """
    __tablename__ = "users"
    # __tablename__ 指定数据库中的表名。如果不写，SQLAlchemy 会自动生成，
    # 但自动生成的名字可能不符合命名规范，所以显式指定更稳妥。

    id = Column(Integer, primary_key=True, index=True)
    # 主键：每行数据的唯一标识。
    # primary_key=True 表示这是主键，数据库会自动建索引并保证唯一。
    # index=True 额外创建索引，加速按 id 查询（虽然主键通常自带索引，但显式声明更明确）。
    # Integer 类型：用户 id 是整数，自增的，不需要手动设置。

    student_id = Column(String(20), unique=True, index=True, nullable=False, comment="学号/工号")
    # 学号/工号：每个用户唯一的身份标识。
    # String(20)：长度限制为 20 个字符，学号通常 10-15 位，留有余量。
    # 为什么用 String(20) 而不是 Text？因为学号长度固定且较短，VARCHAR 比 TEXT 更节省存储空间，
    # 而且数据库对 VARCHAR 列建索引效率更高。
    # unique=True：确保不会有两个用户使用同一个学号。
    # index=True：登录时需要按学号查询，索引加速查询。
    # nullable=False：学号是必填项，不允许为空。

    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    # 用户名：登录凭证之一，需要全局唯一。
    # String(50)：用户名通常不超过 20 个字符，50 给足余量。
    # unique=True：防止重名，这是业务需求。
    # index=True：登录时按用户名查询，索引加速。
    # nullable=False：必填项。

    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    # 密码哈希：存储的是经过哈希处理的密码，不是明文。
    # 为什么用 String(255)？因为常用的哈希算法（如 bcrypt）输出约 60 个字符，
    # 但为了兼容未来可能更换的哈希算法（如 Argon2 可能更长），给到 255 最安全。
    # 为什么不用 Text？密码哈希长度固定且较短，VARCHAR(255) 对索引和查询更友好。
    # 绝对不能存明文密码！这是基本的安全要求。

    real_name = Column(String(50), comment="真实姓名")
    # 真实姓名：可选项，用于展示和联系。
    # String(50)：中文姓名一般不超过 4 个字，但考虑少数民族姓名较长，给 50 个字符。
    # 没有 nullable=False，说明这是可选字段（部分用户可能不想填写真实姓名）。

    phone = Column(String(11), comment="手机号")
    # 手机号：11 位数字，用 String 而不是 Integer 存储。
    # 为什么用 String 而不是 Integer？
    # 1. 手机号不需要做数学运算（加减乘除）。
    # 2. 手机号可能以 0 开头（虽然中国大陆手机号不会，但国际号码会）。
    # 3. Integer 存储会丢失前导零。
    # String(11)：中国大陆手机号固定 11 位。

    email = Column(String(100), comment="邮箱")
    # 邮箱地址：长度通常不超过 50 个字符，100 给足余量。
    # 用 String 而不是 Text，原因同上：长度有限且需要建索引时效率更高。

    avatar = Column(String(255), comment="头像URL")
    # 头像 URL：存储图片的网络地址，不是图片本身。
    # 为什么不在数据库存图片？因为图片是二进制大对象，存数据库会撑爆表，
    # 正确做法是把图片存到文件服务器/OSS，数据库只存 URL。
    # String(255)：URL 长度一般不超过 200 个字符。

    role = Column(Enum(UserRole), default=UserRole.STUDENT, comment="用户角色")
    # 用户角色：使用 Enum 类型，数据库层面就限制只能存预定义的值。
    # default=UserRole.STUDENT：新注册的用户默认是学生角色。
    # 为什么用 Enum 而不是 String？因为 Enum 在数据库层面有约束，
    # 即使代码出错传入非法值，数据库也会拒绝，起到双重保险作用。

    is_active = Column(Boolean, default=True, comment="是否激活")
    # 是否激活：用于软删除或账号禁用。
    # 为什么不用物理删除（直接删记录）？因为用户的数据（帖子、商品等）需要保留，
    # 把 is_active 设为 False 就可以让用户"消失"但数据还在。
    # default=True：新用户默认是激活状态。

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    # 创建时间：记录用户注册的时间。
    # default=datetime.utcnow：当新建用户对象时，如果没有指定时间，自动用当前 UTC 时间。
    # 为什么用 UTC 而不是北京时间？因为 UTC 是全球统一时区，不会因为服务器时区不同而出错。
    # 在前端展示时再转换为北京时间即可。

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    # 更新时间：记录最后一次修改的时间。
    # onupdate=datetime.utcnow：当这条记录被修改并提交时，自动更新为当前时间。
    # 这样不需要手动设置 updated_at，减少代码出错的可能。

    # ── 反向关系（relationship） ──
    # 以下 relationship 定义了"从 User 出发能查到哪些关联数据"。
    # back_populates 表示双向关联：通过 User 可以查 products，
    # 通过 Product 也可以查 seller（即 User）。

    products = relationship("Product", back_populates="seller", cascade="all,delete-orphan")
    # 该用户发布的所有二手商品。
    # cascade="all,delete-orphan" 的含义：
    # - "all" 表示所有操作都级联（包括 save-update、merge、refresh-expire、delete）。
    # - "delete-orphan" 表示当一个 Product 不再属于这个 User 时（比如从 products 列表中移除），
    #   该 Product 会被自动删除，而不仅仅是解除关联。
    # 这确保了"用户删除后，其发布的所有商品也自动删除"，不会留下孤立数据。

    product_comments = relationship("ProductComment", back_populates="user", cascade="all,delete-orphan")
    # 该用户发表的所有商品留言。级联删除同理：用户删除后，留言也自动清理。

    bookings = relationship("Booking", back_populates="user", cascade="all,delete-orphan")
    # 该用户的所有场馆预约记录。级联删除同理。

    posts = relationship("Post", back_populates="author", cascade="all,delete-orphan")
    # 该用户发布的所有生活圈动态。级联删除同理。

    post_comments = relationship("PostComment", back_populates="user", cascade="all,delete-orphan")
    # 该用户发表的所有动态评论。级联删除同理。

    likes = relationship("Like", back_populates="user", cascade="all,delete-orphan")
    # 该用户的所有点赞记录。级联删除同理。

    activities_published = relationship(
        "Activity", back_populates="publisher", cascade="all,delete-orphan"
    )
    # 该用户发布的所有活动。注意是"发布"不是"参与"，参与关系在 ActivityRegistration 中。

    activity_registrations = relationship(
        "ActivityRegistration", back_populates="user", cascade="all,delete-orphan"
    )
    # 该用户的所有活动报名记录。级联删除同理。


# ============================================================
# 二手市场
# ============================================================
class ProductCategory(str, enum.Enum):
    """
    商品分类枚举，定义二手商品的类别。

    【为什么需要分类】
    分类帮助用户快速筛选商品，比如学生只想看教材，就选 BOOKS 分类。
    后端用枚举而不是自由文本，确保分类值统一、不会出现拼写错误。
    """
    ELECTRONICS = "electronics"  # 电子产品：手机、电脑、耳机、平板等
    BOOKS = "books"              # 图书教材：教科书、辅导书、小说等
    DAILY = "daily"              # 日用百货：台灯、水壶、收纳盒等宿舍常用物品
    SPORTS = "sports"            # 运动器材：球拍、哑铃、瑜伽垫等
    CLOTHING = "clothing"        # 服饰鞋帽：二手衣物、鞋子等
    OTHER = "other"              # 其他：无法归入以上分类的商品


class ProductStatus(str, enum.Enum):
    """
    商品状态枚举，定义商品在生命周期中的状态。

    【为什么需要状态】
    商品不是一直都在售的：可能卖掉了，也可能被卖家下架了。
    用状态字段区分，而不是直接删除记录，可以保留历史数据。
    """
    AVAILABLE = "available"  # 在售：买家可以看到并联系卖家
    SOLD = "sold"            # 已售出：商品还在但标记为不可购买
    REMOVED = "removed"      # 已下架：卖家主动下架，其他人看不到


class Product(Base):
    """
    二手商品模型，对应数据库中的 products 表。

    【这张表的核心作用】
    存储所有二手商品的信息，包括标题、描述、价格、图片、分类等。
    每条记录代表一个商品，seller_id 关联到 users 表，表示谁发布的。
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    # 商品主键，自增整数，每件商品有唯一 id。

    title = Column(String(100), nullable=False, comment="商品标题")
    # 商品标题：买家看到的第一行文字。
    # String(100)：标题通常不超过 50 个汉字，100 个字符给足余量。
    # nullable=False：标题是必填的，没有标题的商品没有意义。

    description = Column(Text, comment="商品描述")
    # 商品详细描述：可能很长，包含商品状况、使用时长等信息。
    # 为什么用 Text 而不是 String？因为描述长度不可预测，
    # 有的卖家只写一句话，有的可能写几百字，Text 不限制长度。
    # Text 在数据库中的存储方式和 String 不同，它不存储在行内，而是存一个指针，
    # 所以即使内容很长也不会影响其他列的查询效率。

    price = Column(Float, nullable=False, comment="价格")
    # 商品价格：用浮点数存储。
    # 为什么用 Float 而不是 Decimal？对于校园二手交易场景，
    # 价格精度要求不高（通常精确到分就够了），Float 够用且性能更好。
    # 如果是金融系统，应该用 Decimal 避免浮点精度问题。
    # nullable=False：价格是必填的。

    category = Column(Enum(ProductCategory), nullable=False, index=True, comment="分类")
    # 商品分类：使用枚举类型。
    # index=True：用户按分类筛选商品时（如"只看电子产品"），索引加速查询。
    # nullable=False：分类是必填的。

    status = Column(Enum(ProductStatus), default=ProductStatus.AVAILABLE, comment="状态")
    # 商品状态：新商品默认为"在售"。
    # 没有建索引，因为状态查询通常配合其他条件一起使用，单独的索引意义不大。

    images = Column(Text, comment="图片URL列表，JSON格式")
    # 商品图片：存储为 JSON 字符串，例如 '["url1.jpg", "url2.jpg"]'。
    # 为什么用 Text 而不是单独建一张图片表？
    # 因为图片列表是商品的附属信息，不需要单独查询或关联，
    # 用 JSON 存储更简单，前端拿到后解析即可。
    # 如果需要对图片做复杂查询（如"搜索包含某张图片的商品"），才需要单独建表。

    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="卖家ID")
    # 外键：关联到 users 表的 id 字段，表示这个商品是谁发布的。
    # ForeignKey("users.id") 告诉数据库这个字段的值必须是 users 表中已存在的 id。
    # index=True：按卖家查询商品时（如"查看我发布的商品"）需要索引加速。
    # nullable=False：每个商品必须有卖家。

    views = Column(Integer, default=0, comment="浏览次数")
    # 浏览次数：记录有多少人看过这个商品。
    # default=0：新商品的浏览次数从 0 开始。
    # 每次有人查看商品详情，这个值加 1。

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    # 商品发布时间。

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    # 商品最后修改时间，自动更新。

    # ── 关联关系 ──
    seller = relationship("User", back_populates="products")
    # 反向关联：通过这个关系可以获取商品的卖家信息（User 对象）。
    # back_populates="products" 对应 User 模型中的 products 属性，形成双向关联。
    # 没有 cascade，因为删除商品不应该删除用户（卖家还在呢）。

    comments = relationship(
        "ProductComment", back_populates="product", cascade="all,delete-orphan"
    )
    # 该商品下的所有留言。级联删除：商品删除后，留言也自动删除。


class ProductComment(Base):
    """
    商品留言模型，对应数据库中的 product_comments 表。

    【为什么叫"留言"而不是"评论"】
    二手交易场景下，买家通常是在"问问题"（还有吗？能便宜吗？能面交吗？），
    而不是"评价商品"，所以叫"留言"更准确。
    """
    __tablename__ = "product_comments"

    id = Column(Integer, primary_key=True, index=True)
    # 留言主键。

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True, comment="商品ID")
    # 外键：这条留言属于哪个商品。
    # index=True：按商品查询留言时需要索引（查看某个商品的全部留言）。

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    # 外键：这条留言是谁发的。
    # index=True：查询"我的留言"时需要索引。

    content = Column(Text, nullable=False, comment="留言内容")
    # 留言正文：用 Text 因为长度不可预测。
    # nullable=False：留言不能为空。

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    # 留言时间。

    product = relationship("Product", back_populates="comments")
    # 反向关联：通过留言可以获取对应的商品信息。

    user = relationship("User", back_populates="product_comments")
    # 反向关联：通过留言可以获取留言者的信息（头像、用户名等），
    # 前端展示留言列表时需要显示"谁说的"。


# ============================================================
# 场馆预约
# ============================================================
class VenueType(str, enum.Enum):
    """
    场馆类型枚举，定义学校提供的运动场馆种类。

    【为什么需要区分类型】
    用户可能只想看"羽毛球馆"，不想看"篮球场"。
    分类筛选是场馆预约的核心功能，枚举确保类型值统一。
    """
    BASKETBALL = "basketball"    # 篮球场
    BADMINTON = "badminton"      # 羽毛球馆
    TABLE_TENNIS = "table_tennis"  # 乒乓球室（用下划线连接是因为枚举值不能有空格）
    SWIMMING = "swimming"        # 游泳馆
    GYM = "gym"                  # 健身房
    CLASSROOM = "classroom"      # 教室/自习室（也可以预约用于活动）


class Venue(Base):
    """
    场馆模型，对应数据库中的 venues 表。

    【这张表的作用】
    存储所有可供预约的场馆信息。场馆是静态的（名称、位置、类型不变），
    而时段是动态的（每天都有新的可预约时段），所以分开两张表。
    """
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    # 场馆主键。

    name = Column(String(100), nullable=False, comment="场馆名称")
    # 场馆名称，如"羽毛球馆 A 区"。必填。

    venue_type = Column(Enum(VenueType), nullable=False, comment="场馆类型")
    # 场馆类型，如 BASKETBALL、BADMINTON 等。必填。
    # 没有建索引，因为场馆总数很少，全表扫描也很快，不需要索引。

    location = Column(String(200), comment="位置")
    # 场馆的具体位置，如"城关校区体育馆一楼"。
    # String(200)：地址可能较长，给足空间。

    capacity = Column(Integer, comment="容量")
    # 场馆同时可容纳的人数/场次数。
    # 例如羽毛球馆有 4 片场地，capacity 就是 4。

    description = Column(Text, comment="描述")
    # 场馆的详细描述，如设施说明、注意事项等。

    is_active = Column(Boolean, default=True, comment="是否开放")
    # 场馆是否对外开放。维修期间可以设为 False，用户就看不到了。

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    # 场馆录入时间。

    time_slots = relationship(
        "VenueTimeSlot", back_populates="venue", cascade="all,delete-orphan"
    )
    # 该场馆下的所有可预约时段。级联删除：场馆删除后，时段也自动删除。


class VenueTimeSlot(Base):
    """
    场馆时段模型，对应数据库中的 venue_time_slots 表。

    【为什么需要单独的时段表】
    场馆是静态资源，但"什么时候可以预约"是动态的。
    例如羽毛球馆有 4 片场地，每天有 4 个时段（8-10、10-12、14-16、19-21），
    这些时段需要提前生成，用户预约时选择具体时段。

    【时段 vs 场馆】
    一个场馆有多个时段，一个时段属于一个场馆，这是"一对多"关系。
    """
    __tablename__ = "venue_time_slots"

    id = Column(Integer, primary_key=True, index=True)
    # 时段主键。

    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False, index=True, comment="场馆ID")
    # 外键：这个时段属于哪个场馆。
    # index=True：按场馆查询时段时需要索引。

    date = Column(DateTime, nullable=False, index=True, comment="日期")
    # 日期：存储为 DateTime 类型，但实际只用日期部分（时分秒为 00:00:00）。
    # 为什么不用 Date 类型？因为 SQLAlchemy 的 Date 类型在某些数据库中处理方式不同，
    # DateTime 更通用，兼容性更好。
    # index=True：按日期查询时段时需要索引（"查这个场馆今天有哪些时段"）。

    start_time = Column(String(5), nullable=False, comment="开始时间 HH:MM")
    # 开始时间：用 String(5) 存储，格式为 "08:00"、"14:00"。
    # 为什么用 String 而不是 Time 类型？
    # 因为只需要存储和比较时间字符串，不需要做时间运算，
    # String 更简单直观，也更容易调试。
    # String(5) 刚好是 "HH:MM" 的长度。

    end_time = Column(String(5), nullable=False, comment="结束时间 HH:MM")
    # 结束时间：同上。

    capacity = Column(Integer, nullable=False, comment="容量")
    # 这个时段的最大可预约人数/场次数。
    # 从 venue 表复制过来，因为不同时段的容量可能不同（如某些时段有维护）。

    booked_count = Column(Integer, default=0, comment="已预约数量")
    # 已经被预约的次数。每次有人预约就加 1，取消就减 1。
    # default=0：新时段开始时没人预约。

    is_available = Column(Boolean, default=True, comment="是否可预约")
    # 这个时段是否还可以预约。当 booked_count >= capacity 时，自动设为 False。
    # 也可以手动设为 False（如场馆临时关闭某个时段）。

    venue = relationship("Venue", back_populates="time_slots")
    # 反向关联：通过时段可以获取场馆信息。

    bookings = relationship("Booking", back_populates="time_slot")
    # 该时段的所有预约记录。没有 cascade，因为删除时段不应该自动删除预约记录。


class BookingStatus(str, enum.Enum):
    """
    预约状态枚举，定义预约记录的生命周期状态。

    【为什么需要多个状态】
    预约不是简单地"有/没有"，而是有一个流程：
    用户提交预约 -> 系统确认 -> 用户取消 或 使用完成。
    不同状态下能做的操作不同（如已取消的预约不能再取消）。
    """
    PENDING = "pending"        # 待确认：用户刚提交，等待系统确认
    CONFIRMED = "confirmed"    # 已确认：预约成功，用户可以按时到场
    CANCELLED = "cancelled"    # 已取消：用户主动取消，名额释放
    COMPLETED = "completed"    # 已完成：用户已使用，预约流程结束


class Booking(Base):
    """
    预约记录模型，对应数据库中的 bookings 表。

    【这张表的核心作用】
    记录"哪个用户预约了哪个时段"。这是场馆预约系统的核心业务表。
    """
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    # 预约记录主键。

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    # 外键：谁预约的。
    # index=True：查询"我的预约"时需要索引。

    time_slot_id = Column(Integer, ForeignKey("venue_time_slots.id"), nullable=False, index=True, comment="时段ID")
    # 外键：预约的哪个时段。
    # index=True：查询"这个时段有哪些预约"时需要索引。

    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, comment="状态")
    # 预约状态：新预约默认为"待确认"。

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    # 预约创建时间。

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    # 预约最后修改时间（如状态变更时自动更新）。

    user = relationship("User", back_populates="bookings")
    # 反向关联：通过预约记录可以获取用户信息。

    time_slot = relationship("VenueTimeSlot", back_populates="bookings")
    # 反向关联：通过预约记录可以获取时段信息（进而获取场馆信息）。


# ============================================================
# 校车
# ============================================================
class BusRoute(Base):
    """
    校车路线模型，对应数据库中的 bus_routes 表。

    【为什么路线和时刻表分开】
    路线是固定的（如"城关校区 -> 榆中校区"），而时刻表是该路线下多个发车时间。
    这是"一对多"关系：一条路线有多个班次。
    如果合并到一张表，每条班次都要重复存储路线信息，浪费空间。
    """
    __tablename__ = "bus_routes"

    id = Column(Integer, primary_key=True, index=True)
    # 路线主键。

    name = Column(String(100), nullable=False, comment="路线名称")
    # 路线名称，如"城关->榆中"。必填。

    from_campus = Column(String(50), nullable=False, comment="起点校区")
    # 起点校区名称。必填。
    # 为什么校区名单独一列而不是外键？因为校区数据简单且固定，
    # 没有必要建一张校区表再关联，直接存字符串更简单。

    to_campus = Column(String(50), nullable=False, comment="终点校区")
    # 终点校区名称。必填。

    description = Column(Text, comment="路线描述")
    # 路线描述，如"途经盘旋路，约 50 分钟"。

    is_active = Column(Boolean, default=True, comment="是否运营")
    # 路线是否在运营。停运的路线可以设为 False。

    schedules = relationship(
        "BusSchedule", back_populates="route", cascade="all,delete-orphan"
    )
    # 该路线下的所有时刻表。级联删除：路线删除后，班次也自动删除。


class BusSchedule(Base):
    """
    校车时刻表模型，对应数据库中的 bus_schedules 表。

    【这张表的作用】
    存储某条路线下的具体发车时间、座位数等信息。
    用户查询校车时，先选路线，再看该路线有哪些班次。
    """
    __tablename__ = "bus_schedules"

    id = Column(Integer, primary_key=True, index=True)
    # 班次主键。

    route_id = Column(Integer, ForeignKey("bus_routes.id"), nullable=False, index=True, comment="路线ID")
    # 外键：这个班次属于哪条路线。
    # index=True：按路线查询班次时需要索引。

    departure_time = Column(String(5), nullable=False, comment="发车时间 HH:MM")
    # 发车时间：用 String(5) 存储，格式 "07:30"。
    # 和场馆时段的 start_time 一样，用 String 更简单。

    seats = Column(Integer, nullable=False, comment="座位数")
    # 总座位数：固定值，如 45 座大巴。

    booked_seats = Column(Integer, default=0, comment="已预订座位数")
    # 已被预订的座位数。每次有人预订就加 1。
    # 当 booked_seats >= seats 时，该班次显示"已满"。

    weekday_only = Column(Boolean, default=False, comment="仅工作日")
    # 这个班次是否只在工作日运行。
    # True：周一到周五运行，周末不发车。
    # False：每天都运行（包括周末）。
    # 为什么需要这个字段？因为校车在周末的班次通常比工作日少。

    route = relationship("BusRoute", back_populates="schedules")
    # 反向关联：通过班次可以获取路线信息。


# ============================================================
# 生活圈（朋友圈式动态 + 评论 + 点赞）
# ============================================================
class PostCategory(str, enum.Enum):
    """
    动态分类枚举，定义生活圈帖子的类型。

    【为什么需要分类】
    生活圈内容多样（失物招领、吐槽、提问等），分类帮助用户快速找到感兴趣的内容。
    后端也可以按分类做不同的处理逻辑（如失物招领自动推送）。
    """
    LOST_FOUND = "lost_found"  # 失物招领：捡到东西或丢了东西
    COMPLAINT = "complaint"    # 吐槽：对学校设施、食堂等的不满
    ACTIVITY = "activity"      # 活动：线下活动的宣传
    SHARING = "sharing"        # 分享：日常分享、心情、见闻等
    QA = "qa"                  # 问答：学习或生活上的求助
    OTHER = "other"            # 其他：无法归入以上分类的内容


class Post(Base):
    """
    生活圈动态模型，对应数据库中的 posts 表。

    【这张表的核心作用】
    存储所有生活圈帖子，类似朋友圈/微博的功能。
    每条动态有一个作者（author_id）、内容、分类等。
    """
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    # 动态主键。

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="作者ID")
    # 外键：谁发的这条动态。
    # index=True：查询"某人发的所有动态"时需要索引。

    title = Column(String(100), comment="标题")
    # 标题：可选项，不是所有动态都需要标题（如简单的分享可能只写内容）。
    # nullable 允许为空，所以没有设置 nullable=False。

    content = Column(Text, nullable=False, comment="内容")
    # 动态正文：必填，用 Text 因为长度不可预测。
    # 短动态可能只有几个字，长动态可能有上千字。

    category = Column(Enum(PostCategory), nullable=False, index=True, comment="分类")
    # 分类：必填，用于筛选和推荐。
    # index=True：按分类查询时需要索引（如"只看失物招领"）。

    images = Column(Text, comment="图片URL列表，JSON格式（最多9张）")
    # 图片列表：JSON 格式存储，最多 9 张。
    # 最多 9 张是产品设计决定的（和微信朋友圈一致）。
    # 后端在接收数据时应该验证图片数量不超过 9 张。

    tags = Column(String(200), comment="标签，逗号分隔")
    # 标签：用逗号分隔的字符串，如"失物招领,校园卡"。
    # 为什么不用单独的标签表？因为标签是轻量级的辅助信息，
    # 不需要复杂的关联查询，逗号分隔的字符串足够用。
    # String(200)：限制标签总长度，防止滥用。

    views = Column(Integer, default=0, comment="浏览数")
    # 浏览次数：每次有人查看详情就加 1。

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    # 发布时间。

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    # 最后修改时间。

    author = relationship("User", back_populates="posts")
    # 反向关联：通过动态可以获取作者信息（头像、用户名等），
    # 前端展示动态列表时需要显示"谁发的"。

    comments = relationship(
        "PostComment",
        back_populates="post",
        cascade="all,delete-orphan",
        order_by="PostComment.created_at",
    )
    # 该动态下的所有评论。
    # cascade="all,delete-orphan"：动态删除后，评论也自动删除。
    # order_by="PostComment.created_at"：默认按评论时间排序（旧的在前，新的在后），
    # 这样查询时不需要额外指定排序。

    like_records = relationship(
        "Like", back_populates="post", cascade="all,delete-orphan"
    )
    # 该动态的所有点赞记录。级联删除同理。


class PostComment(Base):
    """
    动态评论模型，对应数据库中的 post_comments 表。

    【和 ProductComment 的区别】
    ProductComment 是对商品的留言，PostComment 是对动态的评论。
    虽然结构类似，但分属不同业务模块，各自独立管理。
    """
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True, index=True)
    # 评论主键。

    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True, comment="动态ID")
    # 外键：这条评论属于哪个动态。
    # index=True：查看某个动态的所有评论时需要索引。

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    # 外键：谁发的评论。

    content = Column(Text, nullable=False, comment="评论内容")
    # 评论正文：必填。

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    # 评论时间。

    post = relationship("Post", back_populates="comments")
    # 反向关联：通过评论可以获取对应的动态。

    user = relationship("User", back_populates="post_comments")
    # 反向关联：通过评论可以获取评论者的信息。


class Like(Base):
    """
    点赞记录模型，对应数据库中的 likes 表。

    【为什么点赞要单独建表而不是在 Post 上加字段】
    如果在 Post 表上加一个 like_count 字段，只能知道"有多少人点赞"，
    但无法知道"谁点了赞"（需要判断当前用户是否已经点过赞）。
    单独建表可以记录每个用户的点赞行为，支持"取消点赞"和"是否已点赞"功能。

    【为什么需要唯一约束】
    UniqueConstraint("user_id", "post_id") 确保同一个用户不能对同一条动态点赞两次。
    这在数据库层面防止了重复点赞，比在代码层面检查更可靠。
    """
    __tablename__ = "likes"
    # __table_args__ 用于定义表级别的约束和索引（不是列级别的）。
    __table_args__ = (
        # 唯一约束：user_id + post_id 的组合必须唯一。
        # 也就是说，一个用户对一条动态最多只能有一条点赞记录。
        UniqueConstraint("user_id", "post_id", name="uq_like_user_post"),
        # 额外索引：按 post_id 查询点赞记录时加速（统计某条动态的点赞数）。
        # 虽然外键通常会自动建索引，但显式定义索引名方便后续维护。
        Index("ix_like_post", "post_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    # 点赞记录主键。

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="点赞用户ID")
    # 外键：谁点的赞。注意这里没有加 index=True，因为在 __table_args__ 中已经通过
    # UniqueConstraint 隐含了索引（大多数数据库会自动为唯一约束建索引）。

    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, comment="动态ID")
    # 外键：对哪条动态点的赞。

    created_at = Column(DateTime, default=datetime.utcnow, comment="点赞时间")
    # 点赞时间。可以用来实现"最新点赞"排序等功能。

    user = relationship("User", back_populates="likes")
    # 反向关联：通过点赞记录可以获取用户信息。

    post = relationship("Post", back_populates="like_records")
    # 反向关联：通过点赞记录可以获取动态信息。


# ============================================================
# 校园活动
# ============================================================
class Activity(Base):
    """
    活动模型，对应数据库中的 activities 表。

    【这张表的核心作用】
    存储校园活动信息（如社团招新、讲座、比赛等），支持发布、查看、报名等功能。
    任何登录用户都可以发布活动（不只是管理员）。

    【和 Venue 的区别】
    场馆预约是"预约固定场馆的固定时段"，而活动是"某个组织/个人发起的具体事件"。
    活动有开始时间、结束时间、最大参与人数等信息，场馆没有这些概念。
    """
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    # 活动主键。

    publisher_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True, comment="发布者ID"
    )
    # 外键：谁发布的这个活动。
    # index=True：查询"某人发布的活动"时需要索引。

    title = Column(String(100), nullable=False, comment="活动标题")
    # 活动标题：必填。

    description = Column(Text, comment="活动描述")
    # 活动详情：可选，但通常都会有。

    organizer = Column(String(100), comment="主办方/社团（可选展示名）")
    # 主办方名称：如"兰大摄影协会"、"学生会文艺部"。
    # 这个字段是展示用的文本，不是外键。
    # 为什么不用外键？因为主办方可能不是系统用户（如校外机构），
    # 用文本存储更灵活。

    location = Column(String(200), comment="活动地点")
    # 活动地点。

    start_time = Column(DateTime, nullable=False, index=True, comment="开始时间")
    # 活动开始时间：必填。
    # index=True：查询"即将开始的活动"时需要按 start_time 排序。

    end_time = Column(DateTime, comment="结束时间")
    # 活动结束时间：可选。有些活动可能没有明确的结束时间。

    max_participants = Column(Integer, comment="最大参与人数")
    # 最大参与人数：活动的人数上限。
    # 可选：如果不限人数，这个字段可以为空。

    current_participants = Column(Integer, default=0, comment="当前参与人数")
    # 当前已报名人数。
    # default=0：新活动开始时没人报名。
    # 每次有人报名就加 1，取消就减 1。
    # 和 max_participants 配合使用：当 current_participants >= max_participants 时，活动满员。

    cover_image = Column(String(255), comment="封面图片")
    # 活动封面图的 URL。用于在活动列表中展示缩略图。

    is_active = Column(Boolean, default=True, comment="是否有效")
    # 活动是否有效。活动结束后可以设为 False，用户就看不到了。

    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    # 活动发布时间。

    publisher = relationship("User", back_populates="activities_published")
    # 反向关联：通过活动可以获取发布者信息。

    registrations = relationship(
        "ActivityRegistration",
        back_populates="activity",
        cascade="all,delete-orphan",
    )
    # 该活动的所有报名记录。级联删除：活动删除后，报名记录也自动删除。


class ActivityRegistration(Base):
    """
    活动报名模型，对应数据库中的 activity_registrations 表。

    【为什么需要唯一约束】
    UniqueConstraint("activity_id", "user_id") 确保同一个用户不能重复报名同一个活动。
    这和 Like 表的唯一约束原理一样：在数据库层面防止重复数据。
    如果只在代码层面检查，高并发时可能出现两个请求同时通过检查，导致重复报名。

    【和 Booking 的区别】
    Booking 是场馆预约，关联到具体的时段；ActivityRegistration 是活动报名，关联到具体活动。
    两者虽然都是"报名"，但业务逻辑不同（场馆有时段限制，活动有人数限制）。
    """
    __tablename__ = "activity_registrations"
    __table_args__ = (
        # 唯一约束：同一个用户不能重复报名同一个活动。
        # name 参数给约束起个名字，方便数据库报错时识别是哪个约束触发的。
        UniqueConstraint(
            "activity_id", "user_id", name="uq_activity_user_registration"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    # 报名记录主键。

    activity_id = Column(
        Integer, ForeignKey("activities.id"), nullable=False, index=True, comment="活动ID"
    )
    # 外键：报的是哪个活动。

    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID"
    )
    # 外键：谁报的名。

    status = Column(String(20), default="registered", comment="状态")
    # 报名状态：默认 "registered"（已报名）。
    # 为什么用 String 而不是 Enum？因为报名状态可能比较简单（只有已报名/已取消），
    # 用 String 更灵活，将来新增状态不需要改数据库结构。
    # 也可以改为 "cancelled" 表示取消报名。

    created_at = Column(DateTime, default=datetime.utcnow, comment="报名时间")
    # 报名时间。

    activity = relationship("Activity", back_populates="registrations")
    # 反向关联：通过报名记录可以获取活动信息。

    user = relationship("User", back_populates="activity_registrations")
    # 反向关联：通过报名记录可以获取用户信息。
