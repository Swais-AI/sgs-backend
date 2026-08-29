from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings
from app.db.pool import build_engine

# Pool size is derived from the database's own max_connections at startup —
# see app/db/pool.py. Nothing here needs adjusting per environment.
engine = build_engine(settings.DATABASE_URL, service="sgs-faculty-api")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
