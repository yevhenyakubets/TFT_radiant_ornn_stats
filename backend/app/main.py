from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.champion_service import get_champion_data
from app.services.riot_service import get_match, get_matches
from app.routers import debug

app = FastAPI()

app.include_router(debug.router)

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

@app.get("/riot/test")
def riot_test():
    return get_match("EUW1_7682122066")

@app.get("/riot/units")
def riot_units():
    match = get_match("EUW1_7682122066")
    return extract_units(match)