from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, models, utils, database, oauth2

app = APIRouter(tags=["Authentication"])

@app.post("/login_new", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login_user(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    db_user = db.query(models.users).filter(models.users.email == user.username).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Email")
    
    if not utils.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Password")
    
    access_token = oauth2.create_access_token(data={"user_id": db_user.id, "email": db_user.email, "name": db_user.name})
    return {"access_token": access_token, "token_type": "bearer"}

# Other code remains the same...
