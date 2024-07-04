from fastapi import FastAPI, WebSocket, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db
from .routers import Book, user, auth, likes
from fastapi.middleware.cors import CORSMiddleware
import json

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[], # this is use to access from different domain of our project like(google.com etc)
    allow_credentials=True,
    allow_methods=["*"], # this is allow who uses our project from outside and has permission like post, delete mostly we don’t allow that
    allow_headers=["*"], # allow headers
)

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Book Collection with WebSocket Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f2f2f2;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #232f3e;
            color: white;
            padding: 1em 0;
            text-align: center;
            font-size: 2em;
        }
        .container {
            max-width: 1200px;
            margin: 2em auto;
            padding: 2em;
            background-color: white;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .book {
            display: flex;
            align-items: center;
            margin-bottom: 1em;
            border-bottom: 1px solid #ddd;
            padding-bottom: 1em;
        }
        .book img {
            max-width: 100px;
            margin-right: 1em;
        }
        .book-info {
            flex-grow: 1;
        }
        .book-info h2 {
            margin: 0;
            font-size: 1.2em;
            color: #232f3e;
        }
        .book-info p {
            margin: 0.5em 0;
            color: #555;
        }
        form {
            display: flex;
            justify-content: center;
            margin: 2em 0;
        }
        form input, form button {
            padding: 0.5em;
            font-size: 1em;
            margin-right: 0.5em;
        }
        form button {
            background-color: #232f3e;
            color: white;
            border: none;
            cursor: pointer;
        }
        #messages {
            list-style: none;
            padding: 0;
        }
        #messages li {
            padding: 0.5em;
            background-color: #eee;
            margin-bottom: 0.5em;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <header>
        Book Collection with WebSocket Chat
    </header>
    <div class="container">
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off" placeholder="Type your message here..."/>
            <button>Send</button>
        </form>
        <ul id="messages"></ul>
        <h2>Books you might like</h2>
        <div id="books">
            <!-- Books will be dynamically added here -->
        </div>
    </div>
    <script>
        var ws = new WebSocket("ws://localhost:8000/ws");
        ws.onmessage = function(event) {
            var messages = document.getElementById('messages');
            var message = document.createElement('li');
            var content = document.createTextNode(event.data);
            message.appendChild(content);
            messages.appendChild(message);
        };

        function sendMessage(event) {
            var input = document.getElementById("messageText");
            ws.send(input.value);
            input.value = '';
            event.preventDefault();
        }

        async function fetchBooks() {
            const response = await fetch('http://127.0.0.1:8000/sqlalchemy');
            const books = await response.json();
            const booksContainer = document.getElementById('books');
            booksContainer.innerHTML = ''; // Clear the container
            books.Data.forEach(book => {
                const bookElement = document.createElement('div');
                bookElement.classList.add('book');
                bookElement.innerHTML = `
                    <img src="https://via.placeholder.com/100" alt="${book.Title}">
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
    </script>
</body>
</html>

"""

@app.get("/", response_class=HTMLResponse)
async def get_home_page():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

app.include_router(Book.app)
app.include_router(user.app)
app.include_router(auth.app)
app.include_router(likes.app)