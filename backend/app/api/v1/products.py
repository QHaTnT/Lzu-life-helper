"""
二手市场 API

本模块处理二手商品交易相关的所有接口，包括：
- 商品发布、查询、更新、删除（CRUD 操作）
- 商品列表查询（支持分类筛选、价格区间、关键词搜索）
- 商品留言功能

功能特点：
- 列表带分类、价格区间、关键词搜索
- 详情带卖家精简信息（使用 joinedload 预加载关联数据）
- 留言板支持嵌入用户卡片
"""

# 导入 Optional 类型，用于表示参数可以为 None
from typing import Optional

# 导入 FastAPI 核心组件
from fastapi import APIRouter, Depends, HTTPException, status, Query

# 导入 SQLAlchemy ORM 相关
from sqlalchemy.orm import Session, joinedload

# 导入数据库连接依赖
from app.core.database import get_db

# 导入统一响应格式函数
from app.core.response import ok

# 导入 Pydantic 数据模型，用于请求数据的验证和序列化
# ProductCreate：发布商品时的请求体格式
# ProductUpdate：更新商品时的请求体格式
# ProductCommentCreate：添加商品留言时的请求体格式
from app.schemas.product import ProductCreate, ProductUpdate, ProductCommentCreate

# 导入商品业务逻辑服务类
from app.services.product_service import ProductService

# 导入依赖注入函数，用于获取当前登录用户
from app.api.deps import get_current_active_user

# 导入模型类，用于数据库查询和类型注解
from app.models import User, Product, ProductComment

# 导入序列化函数，将模型对象转换为字典格式
from app.utils.serializers import (
    serialize_product, serialize_product_comment,
)

# 创建路由实例
router = APIRouter()


# ============================================================
# 发布商品接口
# ============================================================

# @router.post("/")：定义 POST 方法的接口，路径为 /products/
# 使用根路径是因为商品资源的创建是标准的 RESTful 设计
# status_code=status.HTTP_201_CREATED：创建资源成功返回 201
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    发布商品

    参数说明：
    - product_data: 商品信息请求体，包含标题、描述、价格、分类等字段
      FastAPI 会自动验证请求体是否符合 ProductCreate 模型的定义
      例如：价格必须是正数，标题不能为空等
    - current_user: 当前登录用户，通过依赖注入获取
      只有登录用户才能发布商品，未登录用户会收到 401 错误
    - db: 数据库会话，用于执行数据库操作
    """
    # 调用 ProductService 的 create_product 方法创建商品
    # 该方法会将商品的 seller_id 设置为当前用户的 ID
    product = ProductService.create_product(db, product_data, current_user.id)

    # db.refresh(product) 从数据库重新加载商品对象
    # 因为 ProductService 内部可能修改了 product 对象的某些字段（如自动生成的 ID、创建时间等）
    # refresh 会执行 SELECT 查询获取最新的数据
    db.refresh(product)

    # 返回创建成功的商品信息
    return ok(serialize_product(product), msg="发布成功")


# ============================================================
# 获取商品列表接口
# ============================================================

# @router.get("/")：定义 GET 方法的接口，路径为 /products/
# 用于获取商品列表，支持分页和多种筛选条件
@router.get("/")
def get_products(
    category: Optional[str] = Query(None, description="商品分类"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db),
):
    """
    获取商品列表

    参数说明：
    - category: 商品分类，可选参数
      用于按分类筛选商品，如 "电子产品"、"书籍" 等
    - min_price: 最低价格，可选参数
      用于筛选价格大于等于该值的商品
    - max_price: 最高价格，可选参数
      用于筛选价格小于等于该值的商品
    - search: 搜索关键词，可选参数
      用于在商品标题和描述中搜索包含该关键词的商品
    - skip: 跳过的记录数，用于分页
      例如：第一页 skip=0，第二页 skip=20
      Query(0, ge=0) 表示默认值为 0，且必须大于等于 0
    - limit: 返回的记录数，用于分页
      Query(20, ge=1, le=100) 表示默认返回 20 条，最小 1 条，最大 100 条
      限制上限是为了防止一次性返回过多数据导致服务器压力过大
    - db: 数据库会话
    """
    # 调用 ProductService 的 get_products 方法执行复杂查询
    # 该方法内部会根据传入的参数动态构建查询条件
    # 对应的 SQL 类似于：
    # SELECT * FROM products
    # WHERE category = ? AND price >= ? AND price <= ? AND (title LIKE ? OR description LIKE ?)
    # ORDER BY created_at DESC
    # LIMIT ? OFFSET ?
    products = ProductService.get_products(
        db, category, min_price, max_price, search, skip, limit
    )

    # 使用列表推导式将所有商品对象序列化为字典列表
    # serialize_product 会包含卖家的基本信息（精简版，不包含敏感数据）
    return ok([serialize_product(p) for p in products])


# ============================================================
# 获取我发布的商品接口
# ============================================================

# @router.get("/my")：定义 GET 方法的接口，路径为 /products/my
# 注意：这个路由必须在 /{product_id} 之前定义
# 因为 FastAPI 按照路由定义的顺序匹配请求
# 如果 /{product_id} 在前面，"my" 会被当作 product_id 匹配到错误的路由
@router.get("/my")
def get_my_products(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取我发布的商品

    参数说明：
    - current_user: 当前登录用户，需要认证才能查看自己的商品
    - db: 数据库会话
    """
    # SQLAlchemy ORM 查询语法
    # db.query(Product) 对应 SQL 的 SELECT * FROM products
    # .filter(Product.seller_id == current_user.id) 对应 WHERE seller_id = ?
    # .order_by(Product.created_at.desc()) 对应 ORDER BY created_at DESC（按创建时间降序）
    # .all() 执行查询并返回所有结果
    products = (
        db.query(Product)
        .filter(Product.seller_id == current_user.id)
        .order_by(Product.created_at.desc())
        .all()
    )
    return ok([serialize_product(p) for p in products])


# ============================================================
# 获取商品详情接口
# ============================================================

# @router.get("/{product_id}")：定义 GET 方法的接口，路径为 /products/{product_id}
# {product_id} 是路径参数，FastAPI 会自动提取并转换为 int 类型
# 例如：GET /products/123 会将 123 传递给 product_id 参数
@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    获取商品详情

    参数说明：
    - product_id: 商品 ID，从 URL 路径中提取
    - db: 数据库会话
    """
    # joinedload(Product.seller) 使用 SQLAlchemy 的急加载（Eager Loading）
    # 它会在查询商品的同时加载关联的卖家信息（User 对象）
    # 对应的 SQL 类似于：
    # SELECT products.*, users.*
    # FROM products
    # INNER JOIN users ON products.seller_id = users.id
    # WHERE products.id = ?
    # 使用急加载而不是懒加载（Lazy Loading）可以避免 N+1 查询问题
    # N+1 问题：如果先查商品，再逐个查卖家信息，会导致 1+N 次查询
    product = (
        db.query(Product)
        .options(joinedload(Product.seller))
        .filter(Product.id == product_id)
        .first()
    )

    # 检查商品是否存在
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

    # 更新商品浏览次数
    # (product.views or 0) 防止 views 为 None 时出现 TypeError
    # 使用 or 0 是因为数据库中 views 字段可能为 NULL
    product.views = (product.views or 0) + 1

    # 将浏览次数更新同步到数据库
    # db.commit() 会提交事务，将所有未提交的修改写入数据库
    db.commit()
    db.refresh(product)

    return ok(serialize_product(product))


# ============================================================
# 更新商品接口
# ============================================================

# @router.put("/{product_id}")：定义 PUT 方法的接口，用于更新商品
@router.put("/{product_id}")
def update_product(
    product_id: int,
    update_data: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    更新商品

    参数说明：
    - product_id: 要更新的商品 ID
    - update_data: 更新数据，只包含要修改的字段
    - current_user: 当前登录用户，只有商品所有者才能更新
    - db: 数据库会话
    """
    # 调用 ProductService 的 update_product 方法
    # 该方法会验证：
    # 1. 商品是否存在
    # 2. 当前用户是否是商品的所有者（权限检查）
    # 3. 执行更新操作
    product = ProductService.update_product(
        db, product_id, current_user.id, update_data
    )

    if not product:
        # 404 Not Found 用于两种情况：
        # 1. 商品不存在
        # 2. 商品存在但当前用户没有权限（为了安全，不暴露商品是否存在）
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在或无权限"
        )
    return ok(serialize_product(product), msg="更新成功")


# ============================================================
# 删除商品接口
# ============================================================

# @router.delete("/{product_id}")：定义 DELETE 方法的接口，用于删除商品
# DELETE 方法表示删除资源，这是 RESTful 规范的标准用法
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    删除商品

    参数说明：
    - product_id: 要删除的商品 ID
    - current_user: 当前登录用户，只有商品所有者才能删除
    - db: 数据库会话
    """
    # 调用 ProductService 的 delete_product 方法
    # 该方法会验证权限并执行删除操作
    # 注意：这里可能是逻辑删除（设置 is_deleted=True）而不是物理删除
    # 逻辑删除可以保留数据用于审计和恢复
    success = ProductService.delete_product(db, product_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在或无权限"
        )
    return ok(msg="删除成功")


# ============================================================
# 添加商品留言接口
# ============================================================

# @router.post("/{product_id}/comments")：定义 POST 方法的接口，路径为 /products/{product_id}/comments
# 这是嵌套资源的设计模式：评论是商品的子资源
# RESTful 设计中，评论路径通常是 /products/{id}/comments
@router.post("/{product_id}/comments", status_code=status.HTTP_201_CREATED)
def add_product_comment(
    product_id: int,
    comment_data: ProductCommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    添加商品留言

    参数说明：
    - product_id: 商品 ID，留言所属的商品
    - comment_data: 留言内容请求体
    - current_user: 当前登录用户
    - db: 数据库会话
    """
    # 首先验证商品是否存在
    # 如果商品不存在，返回 404 错误
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

    # 创建留言对象
    # ProductComment 是 SQLAlchemy 模型类，对应数据库中的 product_comments 表
    comment = ProductComment(
        product_id=product_id,       # 关联的商品 ID
        user_id=current_user.id,     # 留言用户 ID
        content=comment_data.content,  # 留言内容
    )

    # 将对象添加到数据库会话
    # db.add() 不会立即写入数据库，只是将对象标记为待插入状态
    db.add(comment)

    # 提交事务，将数据写入数据库
    db.commit()

    # 刷新对象，获取数据库自动生成的字段（如 id、created_at）
    db.refresh(comment)

    # 重新查询数据库，获取完整的留言信息（包含用户信息）
    # 因为前面创建的 comment 对象不包含关联的 user 对象
    # 使用 joinedload 急加载用户信息，避免后续访问 user 时触发额外查询
    comment = (
        db.query(ProductComment)
        .options(joinedload(ProductComment.user))
        .filter(ProductComment.id == comment.id)
        .first()
    )

    return ok(serialize_product_comment(comment), msg="留言成功")


# ============================================================
# 获取商品留言列表接口
# ============================================================

# @router.get("/{product_id}/comments")：获取指定商品的所有留言
@router.get("/{product_id}/comments")
def get_product_comments(product_id: int, db: Session = Depends(get_db)):
    """
    获取商品留言列表

    参数说明：
    - product_id: 商品 ID
    - db: 数据库会话
    """
    # 查询指定商品的所有留言
    # .options(joinedload(PostComment.user))：急加载每条留言的用户信息
    # .filter(PostComment.post_id == post_id)：过滤出指定商品的留言
    # .order_by(PostComment.created_at.desc())：按创建时间降序排列（最新留言在前）
    comments = (
        db.query(ProductComment)
        .options(joinedload(ProductComment.user))
        .filter(ProductComment.product_id == product_id)
        .order_by(ProductComment.created_at.desc())
        .all()
    )
    return ok([serialize_product_comment(c) for c in comments])
