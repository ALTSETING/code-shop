from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.db import SessionLocal
from app.models import CartItem, Product, User
from app.routers.auth import get_current_user
from app.schemas import CartAdd, CartItemResponse, CartUpdate

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=list[CartItemResponse])
def get_cart(current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        return (
            db.query(CartItem)
            .options(selectinload(CartItem.product))
            .filter(CartItem.user_id == current_user.id)
            .all()
        )
    finally:
        db.close()


@router.post("/add", response_model=CartItemResponse, status_code=201)
def add_to_cart(item: CartAdd, current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        product = (
            db.query(Product)
            .filter(Product.id == item.product_id, Product.is_active == True)
            .first()
        )

        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        if item.quantity > product.stock:
            raise HTTPException(status_code=400, detail="Not enough stock available")

        cart_item = (
            db.query(CartItem)
            .filter(
                CartItem.user_id == current_user.id,
                CartItem.product_id == item.product_id,
            )
            .first()
        )

        if cart_item:
            new_quantity = cart_item.quantity + item.quantity
            if new_quantity > product.stock:
                raise HTTPException(status_code=400, detail="Not enough stock available")
            cart_item.quantity = new_quantity
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=item.product_id,
                quantity=item.quantity,
            )
            db.add(cart_item)

        db.commit()
        db.refresh(cart_item)
        cart_item.product = product

        return cart_item
    finally:
        db.close()


@router.put("/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    item_data: CartUpdate,
    current_user: User = Depends(get_current_user),
):
    db: Session = SessionLocal()
    try:
        cart_item = (
            db.query(CartItem)
            .options(selectinload(CartItem.product))
            .filter(CartItem.id == item_id, CartItem.user_id == current_user.id)
            .first()
        )

        if cart_item is None:
            raise HTTPException(status_code=404, detail="Cart item not found")

        if not cart_item.product.is_active:
            raise HTTPException(status_code=400, detail="Product is not active")

        if item_data.quantity > cart_item.product.stock:
            raise HTTPException(status_code=400, detail="Not enough stock available")

        cart_item.quantity = item_data.quantity
        db.commit()
        db.refresh(cart_item)

        return cart_item
    finally:
        db.close()


@router.delete("/clear")
def clear_cart(current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        deleted_count = (
            db.query(CartItem)
            .filter(CartItem.user_id == current_user.id)
            .delete(synchronize_session=False)
        )
        db.commit()
        return {"message": f"{deleted_count} cart items deleted"}
    finally:
        db.close()


@router.delete("/remove/{item_id}")
def remove_from_cart(item_id: int, current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        cart_item = (
            db.query(CartItem)
            .filter(CartItem.id == item_id, CartItem.user_id == current_user.id)
            .first()
        )

        if cart_item is None:
            raise HTTPException(status_code=404, detail="Cart item not found")

        db.delete(cart_item)
        db.commit()

        return {"message": f"Cart item {item_id} deleted"}
    finally:
        db.close()
