from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    return {
        "champion": name,
        "radiant_items": ["Radiant Rabadon", "Radiant Guinsoo"],
        "artifacts": ["Infinity Force", "Death's Dance"]
    }
