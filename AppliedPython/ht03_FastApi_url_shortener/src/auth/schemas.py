from sqlmodel import Field, Relationship, SQLModel, AutoString
from pydantic import EmailStr, BaseModel
import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(UserCreate):
    pass 

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    registered_at: datetime.datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(primary_key=True, index=True)
    email: str = Field(index=True, unique=True, nullable=False, sa_type=AutoString)
    registered_at: datetime.datetime = Field(default=datetime.datetime.utcnow(), nullable=False)
    hashed_password: str = Field(nullable=False)

    links: list["ShortURL"] = Relationship(back_populates="user")
