from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, models, utils
from ..database import get_db
from typing import List

app = APIRouter()

@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserCreate)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user.password = utils.hash_password(user.password)
        db_user = models.users(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/users", status_code=status.HTTP_200_OK, response_model=List[schemas.UserBase])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.users).all()
    return users

@app.get("/users/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserBase)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.users).filter(models.users.id == id).first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{id}", status_code=status.HTTP_200_OK)
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.users).filter(models.users.id == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully", "id": id}
