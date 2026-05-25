import argparse

from app.db import SessionLocal
from app.models import User


def grant_admin(email: str) -> int:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email.strip()).first()

        if user is None:
            print("User not found")
            return 1

        if user.is_admin:
            print("User is already admin")
            return 0

        user.is_admin = True
        db.commit()
        print(f"Admin access granted to {user.email}")
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Grant admin access to an existing user."
    )
    parser.add_argument("email", help="Email of the user to promote")
    args = parser.parse_args()
    return grant_admin(args.email)


if __name__ == "__main__":
    raise SystemExit(main())
