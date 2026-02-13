from app.database import engine
from app.models.champion_item_stats import ChampionItemStats

def run():
    ChampionItemStats.__table__.create(bind=engine, checkfirst=True)
    print("champion_item_stats table created.")

if __name__ == "__main__":
    run()
