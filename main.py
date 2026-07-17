# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import admin, tickets, webhook

app = FastAPI(title="Municipal Triage Tool API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Allow the Vite dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(tickets.router)
app.include_router(admin.router)
app.include_router(webhook.router)
