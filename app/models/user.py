from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text
from app.db.session import Base


class UserMaster(Base):
    __tablename__ = "sgs_users_masters"

    user_id          = Column(BigInteger, primary_key=True)
    login_id         = Column(String(100), nullable=True)
    email_id         = Column(String(255), nullable=False, index=True)
    password_hash    = Column(Text, nullable=False)
    full_name        = Column(String(200), nullable=True)
    mobile_no        = Column(String(20), nullable=True)
    is_active        = Column(Boolean, default=True, nullable=False)
    created_datetime = Column(DateTime, nullable=True)
    record_status    = Column(String(20), nullable=True)
