from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.db import SessionLocal
from app.models import CartItem, Order, OrderItem, Product, User
from app.routers.auth import get_current_admin_user, get_current_user
from app.schemas import (
    OrderCreate,
    OrderDetailResponse,
    OrderResponse,
    OrderStatusUpdate,
)

router = APIRouter(prefix="/orders", tags=["Orders"])

ALLOWED_STATUSES = ["new", "confirmed", "paid", "shipped", "delivered", "cancelled"]


@router.get("/", response_model=list[OrderResponse])
def get_orders(current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        return db.query(Order).filter(Order.user_id == current_user.id).all()
    finally:
        db.close()


@router.get("/admin/all", response_model=list[OrderDetailResponse])
def get_all_orders(current_user: User = Depends(get_current_admin_user)):
    db: Session = SessionLocal()
    try:
        return (
            db.query(Order)
            .options(selectinload(Order.items))
            .order_by(Order.id.desc())
            .all()
        )
    finally:
        db.close()


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        order = (
            db.query(Order)
            .options(selectinload(Order.items))
            .filter(Order.id == order_id, Order.user_id == current_user.id)
            .first()
        )

        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        return order
    finally:
        db.close()


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(order_data: OrderCreate, current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        cart_items = (
            db.query(CartItem)
            .options(selectinload(CartItem.product))
            .filter(CartItem.user_id == current_user.id)
            .all()
        )

        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        total_price = 0
        for item in cart_items:
            product = item.product

            if product is None or not product.is_active:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product {item.product_id} is not available",
                )

            if item.quantity > product.stock:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for product {product.id}",
                )

            total_price += product.price * item.quantity

        new_order = Order(
            user_id=current_user.id,
            customer_name=order_data.customer_name,
            phone=order_data.phone,
            address=order_data.address,
            total_price=total_price,
            status="new",
        )
        db.add(new_order)
        db.flush()

        for item in cart_items:
            product = item.product
            db.add(
                OrderItem(
                    order_id=new_order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=product.price,
                )
            )
            product.stock -= item.quantity
            db.delete(item)

        db.commit()
        db.refresh(new_order)

        return new_order
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    current_user: User = Depends(get_current_admin_user),
):
    db: Session = SessionLocal()
    try:
        order = (
            db.query(Order)
            .options(selectinload(Order.items))
            .filter(Order.id == order_id)
            .first()
        )

        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        if status_data.status not in ALLOWED_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Status must be one of: {ALLOWED_STATUSES}",
            )

        if order.status == "cancelled" and status_data.status != "cancelled":
            for item in order.items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product is None or item.quantity > product.stock:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Not enough stock to restore order {order.id}",
                    )
                product.stock -= item.quantity

        if order.status != "cancelled" and status_data.status == "cancelled":
            for item in order.items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product is not None:
                    product.stock += item.quantity

        order.status = status_data.status
        db.commit()
        db.refresh(order)

        return order
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
