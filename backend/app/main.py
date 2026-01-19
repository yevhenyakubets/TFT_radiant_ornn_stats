from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/champion/{name}")
def get_champion(name: str):
    return {
        "champion": name,
        "radiant_items": ["Radiant Rabadon", "Radiant Guinsoo"],
        "ornn_items": ["Infinity Force", "Death's Dance"]
    }
