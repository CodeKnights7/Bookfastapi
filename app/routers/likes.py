from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db
from datetime import datetime
from typing import List

app = APIRouter()

@app.post("/vote", status_code=status.HTTP_200_OK)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if vote.dir not in [0, 1]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vote direction")
    
    vote_query = db.query(models.vote).filter(models.vote.book_id == vote.book_id, models.vote.user_id == current_user.id)
    found_vote = vote_query.first()

    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already voted for this book")
        new_vote = models.vote(book_id=vote.book_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        return {'message': 'Vote recorded successfully'}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have not voted for this book")
        vote_query.delete()
        db.commit()

    return {"message": "Deleted vote successfully"}
