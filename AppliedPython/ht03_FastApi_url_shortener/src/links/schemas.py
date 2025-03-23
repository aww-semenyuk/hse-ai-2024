from pydantic import BaseModel, HttpUrl
from sqlmodel import Field, Relationship, SQLModel, AutoString
from typing import Optional
import datetime

from config import DEFAULT_URL_TTL_DAYS

class URLCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None

class URLUpdate(BaseModel):
    original_url: HttpUrl

class URLResponse(BaseModel):
    original_url: HttpUrl
    short_code: str
    created_at: datetime.datetime
    expires_at: Optional[datetime.datetime]

class StatsResponse(BaseModel):
    short_code: str
    created_at: datetime.datetime
    last_requested: Optional[datetime.datetime] = None
    num_requests: Optional[int] = None

class ShortURL(SQLModel, table=True):
    __tablename__ = "short_urls"

    id: int = Field(primary_key=True, index=True)
    short_code: str = Field(index=True, unique=True, nullable=False)
    original_url: str = Field(nullable=False, sa_type=AutoString)
    created_at: datetime.datetime = Field(default=datetime.datetime.utcnow(), nullable=False)
    expires_at: datetime.datetime = Field(default=datetime.datetime.utcnow() + datetime.timedelta(days=DEFAULT_URL_TTL_DAYS), nullable=False)
    user_id: int | None = Field(foreign_key="users.id")

    user: "User"  = Relationship(back_populates="links")

class RequestLog(SQLModel, table=True):
    __tablename__ = "requests_log"

    row_id: int = Field(primary_key=True, index=True)
    short_code: str = Field(index=True, nullable=False)
    request_timestamp: datetime.datetime = Field(default=datetime.datetime.utcnow(), nullable=False)
