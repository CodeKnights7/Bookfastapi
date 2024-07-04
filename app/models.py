from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, text, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship

class Book(Base):
    __tablename__ = "Booksfastapi"

    id = Column(Integer, primary_key=True, index=True)
    Title = Column(String, index=True, nullable=False)
    Author = Column(String, index=True, nullable=False)
    published = Column(Boolean, server_default='True', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    Owners_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    Owners = relationship("users")
    votes = relationship("vote", back_populates="book")
    

class users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)


class vote(Base):
    __tablename__ = "vote"
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"),primary_key=True)
    book_id = Column(Integer, ForeignKey('Booksfastapi.id', ondelete="CASCADE"),primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    user = relationship("users")
    book = relationship("Book", back_populates="votes")
