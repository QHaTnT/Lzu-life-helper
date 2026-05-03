"""
二手市场 API
- 列表带分类、价格区间、关键词搜索
- 详情带卖家精简信息
- 留言板支持嵌入用户卡片
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.response import ok
from app.schemas.product import ProductCreate, ProductUpdate, ProductCommentCreate
from app.services.product_service import ProductService
from app.api.deps import get_current_active_user
from app.models import User, Product, ProductComment
from app.utils.serializers import (
    serialize_product, serialize_product_comment,
)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """发布商品"""
    product = ProductService.create_product(db, product_data, current_user.id)
    db.refresh(product)
    return ok(serialize_product(product), msg="发布成功")


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
    """获取商品列表"""
    products = ProductService.get_products(
        db, category, min_price, max_price, search, skip, limit
    )
    return ok([serialize_product(p) for p in products])


@router.get("/my")
def get_my_products(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取我发布的商品"""
    products = (
        db.query(Product)
        .filter(Product.seller_id == current_user.id)
        .order_by(Product.created_at.desc())
        .all()
    )
    return ok([serialize_product(p) for p in products])


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取商品详情"""
    product = (
        db.query(Product)
        .options(joinedload(Product.seller))
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    product.views = (product.views or 0) + 1
    db.commit()
    db.refresh(product)
    return ok(serialize_product(product))


@router.put("/{product_id}")
def update_product(
    product_id: int,
    update_data: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """更新商品"""
    product = ProductService.update_product(
        db, product_id, current_user.id, update_data
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在或无权限"
        )
    return ok(serialize_product(product), msg="更新成功")


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """删除商品"""
    success = ProductService.delete_product(db, product_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在或无权限"
        )
    return ok(msg="删除成功")


@router.post("/{product_id}/comments", status_code=status.HTTP_201_CREATED)
def add_product_comment(
    product_id: int,
    comment_data: ProductCommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """添加商品留言"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

    comment = ProductComment(
        product_id=product_id,
        user_id=current_user.id,
        content=comment_data.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    comment = (
        db.query(ProductComment)
        .options(joinedload(ProductComment.user))
        .filter(ProductComment.id == comment.id)
        .first()
    )
    return ok(serialize_product_comment(comment), msg="留言成功")


@router.get("/{product_id}/comments")
def get_product_comments(product_id: int, db: Session = Depends(get_db)):
    """获取商品留言列表"""
    comments = (
        db.query(ProductComment)
        .options(joinedload(ProductComment.user))
        .filter(ProductComment.product_id == product_id)
        .order_by(ProductComment.created_at.desc())
        .all()
    )
    return ok([serialize_product_comment(c) for c in comments])
