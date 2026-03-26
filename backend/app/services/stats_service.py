from sqlalchemy import func
from contextlib import contextmanager

from app.database import SessionLocal
from app.models.champion import Champion
from app.models.items import Item
from app.models.champion_item_stats import ChampionItemStats
from app.models.champion_item_valid_pairs import ChampionItemValidPairs
from app.models.champion_stats import ChampionStat
from app.services.patch_service import get_current_patch
from app.services.description_service import render_champion_description, render_item_description


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


CURRENT_PATCH = get_current_patch()

def get_sorted_traits(traits):
    """
    Filters out 'duo' traits, then sorts: Unique > Origin > Class.
    Alphabetical within the same type.
    """
    filtered_traits = [t for t in traits if t.type != "duo"]

    priority = {"unique": 0, "origin": 1, "class": 2}

    sorted_list = sorted(
        filtered_traits, key=lambda t: (priority.get(t.type, 99), t.name)
    )

    return [{"name": t.name, "type": t.type, "riot_id": t.riot_id} for t in sorted_list]


def get_champion_special_items(champion_riot_id: str):
    with get_db() as db:
        champion = (
            db.query(Champion).filter(Champion.riot_id == champion_riot_id).first()
        )

        if not champion:
            return None

        sorted_traits = get_sorted_traits(champion.traits)

        readable_ability = render_champion_description(
            champion.ability_desc, champion.ability_variables, champion.name
        )

        stats = (
            db.query(
                ChampionItemStats.item_id,
                func.count().label("count"),
                func.avg(ChampionItemStats.placement).label("avg_placement"),
            )
            .filter(
                ChampionItemStats.champion_id == champion.id,
                ChampionItemStats.normalized_patch == CURRENT_PATCH,
            )
            .group_by(ChampionItemStats.item_id)
            .all()
        )

        total_games = sum(row.count for row in stats)

        item_ids = [row.item_id for row in stats]

        item_map = {i.id: i for i in db.query(Item).filter(Item.id.in_(item_ids)).all()}

        valid_item_ids = {
            row.item_id
            for row in db.query(ChampionItemValidPairs.item_id)
            .filter(ChampionItemValidPairs.champion_id == champion.id)
            .all()
        }

        overall_avgs_by_item_id = {
            row.item_id: float(row.avg_placement)
            for row in db.query(
                ChampionItemStats.item_id,
                func.avg(ChampionItemStats.placement).label("avg_placement"),
            )
            .filter(ChampionItemStats.normalized_patch == CURRENT_PATCH)
            .group_by(ChampionItemStats.item_id)
            .all()
        }

        artifacts = {}
        radiants = {}

        for item_id, count, avg in stats:
            item = item_map.get(item_id)
            if not item:
                continue

            percentage = count / total_games if total_games else 0
            avg_placement = float(avg)
            overall_avg = overall_avgs_by_item_id.get(item_id)
            delta = round(avg_placement - overall_avg, 2) if overall_avg is not None else None

            data = {
                "name": item.name,
                "count": count,
                "average_placement": avg_placement,
                "delta": delta,
                "type": item.type,
                "valid": item_id in valid_item_ids,
                "low_sample": percentage < 0.01,
            }

            if item.type == "artifact":
                artifacts[item.riot_id] = data
            elif item.type == "radiant":
                radiants[item.riot_id] = data

    artifacts = dict(sorted(artifacts.items(), key=lambda x: (x[1]["average_placement"] is None, x[1]["average_placement"])))
    radiants = dict(sorted(radiants.items(), key=lambda x: (x[1]["average_placement"] is None, x[1]["average_placement"])))

    return {
        "champion": champion.riot_id,
        "name": champion.name,
        "cost": champion.cost,
        "traits": sorted_traits,
        "ability_name": champion.ability_name,
        "ability_description": readable_ability,
        "artifacts": artifacts,
        "radiants": radiants,
    }


def get_item_stats_by_id(item_riot_id: str, item_type: str):
    with get_db() as db:
        item = (
            db.query(Item)
            .filter(Item.riot_id == item_riot_id, Item.type == item_type)
            .first()
        )

        if not item:
            return None

        readable_desc = render_item_description(item.description, item.effects)

        stats = (
            db.query(
                ChampionItemStats.champion_id,
                func.count().label("count"),
                func.avg(ChampionItemStats.placement).label("avg_placement"),
            )
            .filter(
                ChampionItemStats.item_id == item.id,
                ChampionItemStats.normalized_patch == CURRENT_PATCH,
            )
            .group_by(ChampionItemStats.champion_id)
            .all()
        )

        total_games = sum(row.count for row in stats)

        champion_ids = [row.champion_id for row in stats]

        champion_map = {
            c.id: c
            for c in db.query(Champion).filter(Champion.id.in_(champion_ids)).all()
        }

        valid_champion_ids = {
            row.champion_id
            for row in db.query(ChampionItemValidPairs.champion_id)
            .filter(ChampionItemValidPairs.item_id == item.id)
            .all()
        }

        overall_avgs_by_riot_id = {
            row.champion_id: float(row.avg_placement)
            for row in db.query(
                ChampionStat.champion_id,
                func.avg(ChampionStat.placement).label("avg_placement"),
            )
            .join(Champion, Champion.riot_id == ChampionStat.champion_id)
            .group_by(ChampionStat.champion_id)
            .all()
        }

        result = {}

        for champion_id, count, avg in stats:
            champion = champion_map.get(champion_id)
            if not champion:
                continue

            percentage = count / total_games if total_games else 0
            avg_placement = float(avg)
            overall_avg = overall_avgs_by_riot_id.get(champion.riot_id)
            delta = round(avg_placement - overall_avg, 2) if overall_avg is not None else None

            result[champion.riot_id] = {
                "name": champion.name,
                "count": count,
                "average_placement": avg_placement,
                "delta": delta,
                "valid": champion_id in valid_champion_ids,
                "low_sample": percentage < 0.01,
            }

    sorted_result = dict(
    sorted(result.items(), key=lambda x: (x[1]["delta"] is None, x[1]["delta"]))
    )

    return {
        "id": item_riot_id,
        "name": item.name,
        "type": item_type,
        "description": readable_desc,
        "stats": item.effects,
        "champions": sorted_result,
    }
