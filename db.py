from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

class Base(DeclarativeBase):
    pass


def init_db(metadata) -> None:
    metadata.create_all(bind=engine)
    _run_sqlite_migrations()


def _run_sqlite_migrations() -> None:
    inspector = inspect(engine)

    existing_tables = set(inspector.get_table_names())
    required_columns = {
        "users": {
            "is_admin": "ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"
        },
        "cart_items": {
            "user_id": "ALTER TABLE cart_items ADD COLUMN user_id INTEGER"
        },
        "orders": {
            "user_id": "ALTER TABLE orders ADD COLUMN user_id INTEGER"
        },
        "products": {
            "is_active": "ALTER TABLE products ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"
        },
    }

    with engine.begin() as connection:
        for table_name, columns in required_columns.items():
            if table_name not in existing_tables:
                continue

            current_columns = {
                column["name"]
                for column in inspector.get_columns(table_name)
            }

            for column_name, statement in columns.items():
                if column_name not in current_columns:
                    connection.execute(text(statement))
