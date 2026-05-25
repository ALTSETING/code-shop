from app.auth import hash_password
from app.db import Base, SessionLocal, init_db
from app.models import Product, User


ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

PRODUCTS = [
    {
        "name": "Wireless Mouse",
        "description": "Compact mouse for everyday work.",
        "price": 699,
        "category": "Accessories",
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=900&q=80",
        "stock": 20,
    },
    {
        "name": "Mechanical Keyboard",
        "description": "Full-size keyboard with tactile switches.",
        "price": 2499,
        "category": "Accessories",
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=80",
        "stock": 12,
    },
    {
        "name": "USB-C Hub",
        "description": "Hub with HDMI, USB and card reader.",
        "price": 1299,
        "category": "Adapters",
        "image_url": "https://images.unsplash.com/photo-1625842268584-8f3296236761?auto=format&fit=crop&w=900&q=80",
        "stock": 15,
    },
    {
        "name": "Laptop Stand",
        "description": "Aluminum stand for a cleaner desk setup.",
        "price": 999,
        "category": "Workspace",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=900&q=80",
        "stock": 10,
    },
    {
        "name": "Noise Cancelling Headphones",
        "description": "Comfortable headphones for focus and calls.",
        "price": 3999,
        "category": "Audio",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
        "stock": 8,
    },
]


def seed_admin(db) -> None:
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if admin is None:
        db.add(
            User(
                email=ADMIN_EMAIL,
                hashed_password=hash_password(ADMIN_PASSWORD),
                is_admin=True,
            )
        )
        return

    admin.is_admin = True
    admin.is_active = True


def seed_products(db) -> None:
    for product_data in PRODUCTS:
        product = db.query(Product).filter(Product.name == product_data["name"]).first()
        if product is None:
            db.add(Product(**product_data, is_active=True))
            continue

        for field_name, value in product_data.items():
            setattr(product, field_name, value)
        product.is_active = True


def main() -> int:
    init_db(Base.metadata)
    db = SessionLocal()
    try:
        seed_admin(db)
        seed_products(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"Seed completed. Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
