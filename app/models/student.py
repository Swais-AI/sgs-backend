from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from app.db.session import Base


class StudentMaster(Base):
    __tablename__ = "sgs_student_master"

    student_id       = Column(BigInteger, primary_key=True)
    full_name        = Column(String(150), nullable=True)
    roll_no          = Column(String(20),  nullable=True)
    class_id         = Column(BigInteger,  nullable=True)
    section          = Column(String(10),  nullable=True)
    guardian_name    = Column(String(150), nullable=True)
    guardian_phone   = Column(String(20),  nullable=True)
    guardian_email   = Column(String(255), nullable=True)
    is_active        = Column(Boolean,     nullable=True)
    created_datetime = Column(DateTime,    nullable=True)
    record_status    = Column(String(20),  nullable=True)
