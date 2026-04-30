"""
Seed script — creates the demo teacher account used by the frontend.
Run once after migrations: python scripts/seed.py

Credentials match the dummyData.json in the Next.js frontend:
  email: priya.sharma@swais.edu
  password: password123
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.db.session import SessionLocal
from app.models.user import UserMaster, UserRole
from app.models.teacher import TeacherMaster
from app.core.security import get_password_hash


def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(UserMaster).filter_by(email="priya.sharma@swais.edu").first()
        if existing:
            print("✅ Seed data already exists — skipping.")
            return

        # Create user
        user = UserMaster(
            username="priya.sharma",
            email="priya.sharma@swais.edu",
            password_hash=get_password_hash("password123"),
            role=UserRole.teacher,
            is_active=True,
        )
        db.add(user)
        db.flush()  # get user_id

        # Create teacher profile
        teacher = TeacherMaster(
            user_id=user.user_id,
            first_name="Dr. Priya",
            last_name="Sharma",
            phone="9876543210",
            avatar_initials="PS",
            subject="Social Studies",
            class_assigned="8",
            section="A",
            school_name="SWAIS International Academy",
            employee_code="T001",
        )
        db.add(teacher)
        db.commit()

        print(f"✅ Seeded teacher: priya.sharma@swais.edu / password123")
        print(f"   user_id={user.user_id}, teacher_id={teacher.teacher_id}")
    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
