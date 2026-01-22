from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.champion_service import get_champion_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/champion/{name}")
def get_champion(name: str):
     return get_champion_data(name)