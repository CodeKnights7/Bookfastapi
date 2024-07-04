from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db
from datetime import datetime
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import joinedload

app = APIRouter()

@app.post("/")
def get_books(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    books = db.query(models.Book).filter(models.Book.Owners_id == current_user.id).all()
    results = db.query(models.Book, func.count(models.vote.book_id).label("vote_count")) \
                .join(models.vote, models.Book.id == models.vote.book_id, isouter=True) \
                .group_by(models.Book.id).all()
    print(results)
    # Serialize the results
    serialized_results = []
    for book, vote_count in results:
        serialized_results.append({
            "id": book.id,
            "Title": book.Title,
            "Author": book.Author,
            "published": book.published,
            "created_at": book.created_at,
            "Owners_id": book.Owners_id,
            "vote_count": vote_count
        })

    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books found for the current user")

    return serialized_results


@app.get("/sqlalchemy", response_model=List[schemas.BookInDB], status_code=status.HTTP_200_OK)
def sqlalchemy(db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user)):
    books = db.query(models.Book).filter(models.Book.Owners_id == current_user.id).all()
    return books

@app.post("/create_new_book", response_model=schemas.BookInDB, status_code=status.HTTP_201_CREATED)
def create_new_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    if not book.created_at:
        book.created_at = datetime.utcnow()

    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/{id}", status_code=status.HTTP_200_OK)
def get_book(id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == id).first()
    if book:
        return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{id}", status_code=status.HTTP_200_OK)
def delete_book(id: int, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    book = db.query(models.Book).filter(models.Book.id == id, models.Book.Owners_id == current_user.id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully", "id": id}

@app.put("/books/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_book(id: int, book_data: schemas.BookCreate, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    book = db.query(models.Book).filter(models.Book.id == id, models.Book.Owners_id == current_user.id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book_data.dict().items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return {"message": "Book updated successfully", "book": book}

@app.post("/newpost", status_code=status.HTTP_201_CREATED)
def add_books(new_books: List[schemas.BookCreate], db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    for book in new_books:
        if book.created_at is None:
            book.created_at = datetime.utcnow()

        db_book = models.Book(**book.dict(), Owners_id=current_user.id)
        db.add(db_book)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create books: {str(e)}")
    
    return {"books": new_books}

