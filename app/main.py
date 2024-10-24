from distutils.dir_util import create_tree
from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import uvicorn

from app.oauth2 import create_access_token

from . import models, schemas, database
from .database import engine, SessionLocal
from .routers import Book, user, auth, likes

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# HTML templates with inline CSS and JavaScript
html_login = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            width: 300px;
        }
        h2 {
            margin-bottom: 20px;
            text-align: center;
        }
        form {
            display: flex;
            flex-direction: column;
        }
        input {
            margin-bottom: 10px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            padding: 10px;
            border: none;
            background-color: #333;
            color: #fff;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #555;
        }
        p {
            text-align: center;
            margin-top: 10px;
        }
        a {
            color: #333;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login</h2>
        <form action="/login" method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p>Don't have an account? <a href="/signup">Sign up</a></p>
    </div>
</body>
</html>
"""

html_signup = """
<!DOCTYPE html>
<html>
<head>
    <title>Signup</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            width: 300px;
        }
        h2 {
            margin-bottom: 20px;
            text-align: center;
        }
        form {
            display: flex;
            flex-direction: column;
        }
        input {
            margin-bottom: 10px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            padding: 10px;
            border: none;
            background-color: #333;
            color: #fff;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #555;
        }
        p {
            text-align: center;
            margin-top: 10px;
        }
        a {
            color: #333;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Signup</h2>
        <form action="/signup" method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Signup</button>
        </form>
        <p>Already have an account? <a href="/login">Login</a></p>
    </div>
</body>
</html>
"""

html_books = """
<!DOCTYPE html>
<html>
<head>
    <title>Books</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            width: 300px;
        }
        h2 {
            margin-bottom: 20px;
            text-align: center;
        }
        .book {
            margin-bottom: 20px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .book-info {
            margin-bottom: 10px;
        }
        #chat-container {
            margin-top: 20px;
        }
        #messages {
            margin-top: 10px;
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 5px;
            max-height: 200px;
            overflow-y: scroll;
        }
        #message-input {
            width: calc(100% - 22px);
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            padding: 10px;
            border: none;
            background-color: #333;
            color: #fff;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #555;
        }
    </style>
    <script>
        const token = document.cookie.split('; ').find(row => row.startsWith('access_token')).split('=')[1];
        
        async function fetchBooks() {
            const response = await axios.get('/api/books', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const books = response.data;
            const booksContainer = document.getElementById('books-container');
            booksContainer.innerHTML = '';
            books.forEach(book => {
                const bookElement = document.createElement('div');
                bookElement.classList.add('book');
                bookElement.innerHTML = `
                    <div class="book-info">
                        <h2>${book.Title}</h2>
                        <p>Author: ${book.Author}</p>
                        <p>Published: ${book.published ? 'Yes' : 'No'}</p>
                        <p>Created At: ${new Date(book.created_at).toLocaleString()}</p>
                        <p>Owner: ${book.Owners.name}</p>
                        <p>Votes: ${book.vote_count}</p>
                    </div>
                `;
                booksContainer.appendChild(bookElement);
            });
        }

        fetchBooks();

        const socket = new WebSocket('ws://127.0.0.1:8000/ws');
        
        socket.onmessage = function(event) {
            const messages = document.getElementById('messages');
            const message = document.createElement('div');
            message.textContent = event.data;
            messages.appendChild(message);
        };

        function sendMessage() {
            const input = document.getElementById('message-input');
            socket.send(input.value);
            input.value = '';
        }
    </script>
</head>
<body>
    <div class="container">
        <h2>Books</h2>
        <div id="books-container"></div>
        <div id="chat-container">
            <h3>Chat</h3>
            <input type="text" id="message-input" placeholder="Type a message">
            <button onclick="sendMessage()">Send</button>
            <div id="messages"></div>
        </div>
    </div>
</body>
</html>
"""

@app.get("/login", response_class=HTMLResponse)
async def login():
    return HTMLResponse(content=html_login)



@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    user = auth(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/books", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.get("/signup", response_class=HTMLResponse)
async def signup():
    return HTMLResponse(content=html_signup)

@app.post("/signup")
async def signup(username: str = Form(...), password: str = Form(...)):
    user = create_tree(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Username already taken")
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/books", response_class=HTMLResponse)
async def books():
    return HTMLResponse(content=html_books)

# Helper functions and routes omitted for brevity...
