from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from pydantic.types import conint

# User Schema

class UserBase(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    created_at: Optional[datetime] = None

class UserCreate(UserBase):
    # id: Optional[int] = None
    password: str
    # created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        exclude = ['password']  # Exclude password from response

class userlogin(BaseModel):
    email: EmailStr
    password: str
   

# Book Schema
class BookBase(BaseModel):
    Title: str
    Author: str
    published: bool

class BookCreate(BookBase):
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class BookInDB(BookBase):
    id: int
    created_at: datetime
    Owners_id: int
    Owners: userlogin
    votes: Optional[int] = 0  # Add this field to store the vote count

    class Config:
        orm_mode = True





# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

# Vote Schema


# Vote Schema
class Vote(BaseModel):
    book_id: int
    dir: int  # Ensure dir can only be 0 or 1