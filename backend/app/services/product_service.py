"""
二手市场服务
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models import Product, ProductComment, ProductStatus, ProductCategory
from app.schemas.product import ProductCreate, ProductUpdate
import json


class ProductService:
    """二手商品服务"""

    @staticmethod
    def create_product(db: Session, product_data: ProductCreate, seller_id: int) -> Product:
        """创建商品"""
        product = Product(
            title=product_data.title,
            description=product_data.description,
            price=product_data.price,
            category=ProductCategory(product_data.category),
            images=json.dumps(product_data.images) if product_data.images else "[]",
            seller_id=seller_id,
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    @staticmethod
    def get_products(
        db: Session,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Product]:
        """获取商品列表"""
        query = db.query(Product).filter(Product.status == ProductStatus.AVAILABLE)

        if category:
            query = query.filter(Product.category == category)

        if min_price is not None:
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        if search:
            query = query.filter(
                or_(
                    Product.title.contains(search),
                    Product.description.contains(search),
                )
            )

        products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
        return products

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """获取商品详情"""
        product = db.query(Product).filter(Product.id == product_id).first()

        if product:
            # 增加浏览次数
            product.views += 1
            db.commit()

        return product

    @staticmethod
    def update_product(
        db: Session, product_id: int, seller_id: int, update_data: ProductUpdate
    ) -> Optional[Product]:
        """更新商品"""
        product = db.query(Product).filter(
            and_(Product.id == product_id, Product.seller_id == seller_id)
        ).first()

        if not product:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)

        return product

    @staticmethod
    def delete_product(db: Session, product_id: int, seller_id: int) -> bool:
        """删除商品（软删除）"""
        product = db.query(Product).filter(
            and_(Product.id == product_id, Product.seller_id == seller_id)
        ).first()

        if not product:
            return False

        product.status = ProductStatus.REMOVED
        db.commit()

        return True

    @staticmethod
    def add_comment(
        db: Session, product_id: int, user_id: int, content: str
    ) -> ProductComment:
        """添加商品留言"""
        comment = ProductComment(
            product_id=product_id,
            user_id=user_id,
            content=content,
        )

        db.add(comment)
        db.commit()
        db.refresh(comment)

        return comment

    @staticmethod
    def get_product_comments(db: Session, product_id: int) -> List[ProductComment]:
        """获取商品留言列表"""
        comments = (
            db.query(ProductComment)
            .filter(ProductComment.product_id == product_id)
            .order_by(ProductComment.created_at.desc())
            .all()
        )
        return comments
