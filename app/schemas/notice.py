from datetime import date
from pydantic import BaseModel


class NoticeOut(BaseModel):
    notice_id: int
    title: str | None = None
    text: str | None = None
    notice_date: date | None = None
    audience: str | None = None


class NoticeListResponse(BaseModel):
    notices: list[NoticeOut]
    total: int
