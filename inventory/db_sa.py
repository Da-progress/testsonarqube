"""
SQLAlchemy engine, session factory and ORM models.
These mirror the Django ORM tables and are used for advanced
query / reporting operations (search, sort, aggregations).
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, ForeignKey, Text, Boolean, func
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from django.conf import settings
import datetime

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


# ---------------------------------------------------------------------------
# SA mirror models (map to Django-managed tables)
# ---------------------------------------------------------------------------

class SACategory(Base):
    __tablename__ = "inventory_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    products = relationship("SAProduct", back_populates="category")


class SASupplier(Base):
    __tablename__ = "inventory_supplier"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(254), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    products = relationship("SAProduct", back_populates="supplier")


class SAProduct(Base):
    __tablename__ = "inventory_product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    quantity = Column(Integer, nullable=False, default=0)
    min_quantity = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey("inventory_category.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("inventory_supplier.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    category = relationship("SACategory", back_populates="products")
    supplier = relationship("SASupplier", back_populates="products")
    movements = relationship("SAStockMovement", back_populates="product")


class SAStockMovement(Base):
    __tablename__ = "inventory_stockmovement"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("inventory_product.id"), nullable=False)
    movement_type = Column(String(10), nullable=False)   # 'in' | 'out' | 'adj'
    quantity = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship("SAProduct", back_populates="movements")


# ---------------------------------------------------------------------------
# Dependency helper
# ---------------------------------------------------------------------------

def get_db():
    """Yield a SQLAlchemy session; close on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# SA-powered query helpers used by views
# ---------------------------------------------------------------------------

def sa_search_products(query: str = "", sort_by: str = "name", sort_dir: str = "asc",
                       category_id: int = None, low_stock: bool = False):
    """Return list of SAProduct dicts via SQLAlchemy."""
    db = SessionLocal()
    try:
        q = db.query(SAProduct)

        if query:
            q = q.filter(
                SAProduct.name.ilike(f"%{query}%") |
                SAProduct.sku.ilike(f"%{query}%") |
                SAProduct.description.ilike(f"%{query}%")
            )

        if category_id:
            q = q.filter(SAProduct.category_id == category_id)

        if low_stock:
            q = q.filter(SAProduct.quantity <= SAProduct.min_quantity)

        # Dynamic sort
        sort_col = getattr(SAProduct, sort_by, SAProduct.name)
        if sort_dir == "desc":
            q = q.order_by(sort_col.desc())
        else:
            q = q.order_by(sort_col.asc())

        return q.all()
    finally:
        db.close()


def sa_warehouse_stats():
    """Aggregate statistics via SQLAlchemy."""
    db = SessionLocal()
    try:
        total_products = db.query(func.count(SAProduct.id)).scalar()
        total_value = db.query(func.sum(SAProduct.price * SAProduct.quantity)).scalar() or 0
        low_stock_count = db.query(func.count(SAProduct.id)).filter(
            SAProduct.quantity <= SAProduct.min_quantity
        ).scalar()
        categories_count = db.query(func.count(SACategory.id)).scalar()
        return {
            "total_products": total_products,
            "total_value": round(total_value, 2),
            "low_stock_count": low_stock_count,
            "categories_count": categories_count,
        }
    finally:
        db.close()
