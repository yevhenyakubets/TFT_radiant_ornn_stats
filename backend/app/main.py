import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import champions, items

load_dotenv()

origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(champions.router)
app.include_router(items.router)

@app.get("/")
def root():
    return {"status": "ok"}