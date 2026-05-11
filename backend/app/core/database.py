"""
数据库连接配置（MySQL）。

这个文件负责三件事：
  1. 创建 SQLAlchemy 数据库引擎（engine），它是与 MySQL 建立连接的核心对象。
  2. 创建会话工厂（SessionLocal），每次需要操作数据库时，用它来创建一个数据库会话。
  3. 提供 get_db() 依赖注入函数，FastAPI 的路由函数可以通过它自动获取数据库会话。

SQLAlchemy 是 Python 中最流行的 ORM（对象关系映射）框架，
它让你用 Python 类来定义数据库表结构，用 Python 方法来执行 SQL 查询，
不需要手写 SQL 语句，减少出错概率并提高开发效率。
"""

# 导入 create_engine 函数。它是 SQLAlchemy 的核心函数，
# 用于创建数据库引擎，引擎负责管理数据库连接池和执行 SQL 语句。
from sqlalchemy import create_engine

# 导入 declarative_base 函数。它创建一个基类，
# 所有 ORM 模型类（比如 User、Article）都要继承这个基类，
# 这样 SQLAlchemy 才能自动收集模型定义并生成对应的建表 SQL。
from sqlalchemy.ext.declarative import declarative_base

# 导入 sessionmaker 工厂函数。它用于创建"会话工厂"，
# 会话工厂可以批量生产数据库会话对象。每个会话对象代表一次与数据库的交互过程。
from sqlalchemy.orm import sessionmaker

# 导入配置对象，从中读取数据库连接字符串和其他参数。
from app.core.config import settings


# ==================== 创建数据库引擎 ====================

# create_engine() 创建一个数据库引擎实例。
# 这个引擎不会立即连接数据库，而是在第一次执行 SQL 时才建立真正的连接。
engine = create_engine(
    # settings.DATABASE_URL：数据库连接字符串，格式为：
    # mysql+pymysql://用户名:密码@主机:端口/数据库名
    # 这个字符串决定了连接哪个数据库、用什么驱动、什么账号。
    settings.DATABASE_URL,

    # echo=settings.DATABASE_ECHO：是否打印 SQL 语句到终端。
    # True 时会看到类似 "SELECT * FROM users WHERE id=1" 的输出，方便调试。
    # False 时静默执行，适合生产环境。
    settings.DATABASE_ECHO,

    # pool_pre_ping=True：开启连接池的"预检测"功能。
    # 数据库连接可能会因为网络波动、超时等原因断开，但连接池不知道。
    # 开启后，每次从连接池取出一个连接时，先执行一条简单的 SQL（SELECT 1）检测连接是否存活。
    # 如果连接已断开，就丢弃这个连接并创建一个新连接。
    # 虽然有微小的性能开销，但可以避免"拿到一个死连接导致报错"的问题。
    pool_pre_ping=True,

    # pool_recycle=3600：设置连接的最大存活时间（单位：秒）。
    # 3600 秒 = 1 小时。超过这个时间的连接会被关闭并重建。
    # MySQL 默认的 wait_timeout 通常是 8 小时，但某些云数据库会更短（比如 10 分钟）。
    # 如果不设置回收时间，可能会出现"连接池里的连接全部超时失效"的问题。
    # 这里设置为 1 小时是保守策略，确保连接不会超过 MySQL 的超时限制。
    pool_recycle=3600,
)


# ==================== 创建会话工厂 ====================

# sessionmaker() 创建一个会话工厂类（SessionLocal），后续可以用它来创建具体的会话。
# 这里的参数含义：
#   autocommit=False：不自动提交事务。
#     每次执行数据库操作后，需要手动调用 session.commit() 才能将修改写入数据库。
#     这样做的好处是可以手动控制事务边界，比如在多步操作中，某一步失败可以回滚。
#   autoflush=False：不自动刷新（flush）。
#     正常情况下，执行查询前 SQLAlchemy 会先把之前的修改发送给数据库。
#     关闭自动刷新后，只有在明确调用 session.flush() 或 session.commit() 时才发送修改。
#     这样可以更精确地控制 SQL 执行时机。
#   bind=engine：将这个会话工厂绑定到前面创建的数据库引擎上，
#     这样通过这个工厂创建的所有会话都会操作同一个数据库。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ==================== 创建 ORM 基类 ====================

# declarative_base() 创建一个基类，所有 ORM 模型都必须继承它。
# 继承这个基类后，模型类可以使用 SQLAlchemy 提供的各种 ORM 功能：
#   - 自动根据类属性生成数据库表结构。
#   - __tablename__ 属性指定表名。
#   - Column 对象定义列的名称、类型和约束。
# 示例：
#   class User(Base):
#       __tablename__ = "users"
#       id = Column(Integer, primary_key=True)
#       name = Column(String(50))
Base = declarative_base()


# ==================== 数据库会话依赖注入函数 ====================

def get_db():
    """
    获取数据库会话的生成器函数。

    这是 FastAPI 的"依赖注入"（Dependency Injection）机制的标准用法。
    FastAPI 的路由函数可以通过参数 db: Session = Depends(get_db) 来自动获取数据库会话。

    工作流程：
      1. FastAPI 收到请求时，先执行 get_db()，创建一个新的数据库会话。
      2. 将这个会话传给路由函数，路由函数用它执行数据库操作（增删改查）。
      3. 请求处理完毕后（无论成功还是失败），finally 块会自动关闭会话，释放数据库连接。

    为什么要手动关闭会话？
      - 数据库连接是有限资源。如果不关闭，大量请求会导致连接池耗尽，新请求会卡住。
      - 未关闭的会话可能持有数据库锁，导致其他请求被阻塞。
      - finally 块保证即使路由函数抛出异常，连接也一定会被关闭。

    返回值：
      - yield db：使用 yield 而不是 return，是因为 FastAPI 需要在请求处理完毕后
        继续执行 finally 块来关闭连接。如果用 return，finally 块会在请求完成前执行。
    """
    db = SessionLocal()  # 创建一个数据库会话实例
    try:
        yield db  # 将会话交给路由函数使用
    finally:
        db.close()  # 无论路由函数是否报错，都会关闭会话释放连接
