from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Product, User
from app.routers.auth import get_current_admin_user
from app.schemas import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductResponse])
def get_products():
    db: Session = SessionLocal()
    try:
        return db.query(Product).filter(Product.is_active == True).all()
    finally:
        db.close()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    db: Session = SessionLocal()
    try:
        product = (
            db.query(Product)
            .filter(Product.id == product_id, Product.is_active == True)
            .first()
        )

        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        return product
    finally:
        db.close()


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_admin_user),
):
    db: Session = SessionLocal()
    try:
        new_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            category=product.category,
            image_url=product.image_url,
            stock=product.stock,
            is_active=True,
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product
    finally:
        db.close()


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_admin_user),
):
    db: Session = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        update_data = product_data.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(product, field_name, value)

        db.commit()
        db.refresh(product)

        return product
    finally:
        db.close()


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_admin_user),
):
    db: Session = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        product.is_active = False
        db.commit()

        return {"message": f"Product with id {product_id} deactivated"}
    finally:
        db.close()
