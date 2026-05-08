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
    """Context manager that provides a database session and ensures it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


CURRENT_PATCH = get_current_patch()


def get_sorted_traits(traits):
    """
    Filters and sorts a champion's traits for display.

    Filters out 'duo' traits (internal Riot trait type, not displayed in game),
    then sorts by type priority: Unique > Origin > Class, with alphabetical
    ordering within the same type.

    Args:
        traits: List of trait ORM objects with .type, .name, .riot_id attributes.

    Returns:
        List of dicts with keys: name, type, riot_id.
    """
    filtered_traits = [t for t in traits if t.type != "duo"]
    priority = {"Unique": 0, "Origin": 1, "Class": 2}
    sorted_list = sorted(
        filtered_traits, key=lambda t: (priority.get(t.type, 99), t.name)
    )
    return [{"name": t.name, "type": t.type, "riot_id": t.riot_id} for t in sorted_list]


def get_champion_special_items(champion_riot_id: str):
    """
    Returns stats for all radiant items and artifacts used by a given champion.

    For each item, computes:
    - count: number of games the champion used this item
    - average_placement: champion's avg placement when using this item
    - delta: difference between this champion's avg placement with the item
             vs the item's overall avg placement across all champions.
             Negative delta means the champion performs better than average with the item.
    - valid: whether this item/champion pair is considered a valid pair (item at least somewhat matches the champion's role, 
            so tank items are ignored for carries and such), data is taken from champion_item_valid_pairs table
    - low_sample: whether the item appears with a frequency of less than 1% of the total number of items of that specific type (Artifact or Radiant).

    Args:
        champion_riot_id: Riot's string ID for the champion (e.g. "TFT16_Jinx").

    Returns:
        Dict with champion info and two sub-dicts: artifacts and radiants,
        each sorted by average_placement ascending.
        Returns None if the champion is not found.
    """
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
                ChampionItemStats.patch == CURRENT_PATCH,
            )
            .group_by(ChampionItemStats.item_id)
            .all()
        )

        item_ids = [row.item_id for row in stats]
        item_map = {i.id: i for i in db.query(Item).filter(Item.id.in_(item_ids)).all()}
        total_artifacts = sum(row.count for row in stats if item_map.get(row.item_id) and item_map[row.item_id].type == "artifact")
        total_radiants = sum(row.count for row in stats if item_map.get(row.item_id) and item_map[row.item_id].type == "radiant")

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
            .filter(ChampionItemStats.patch == CURRENT_PATCH)
            .group_by(ChampionItemStats.item_id)
            .all()
        }

        artifacts = {}
        radiants = {}

        for item_id, count, avg in stats:
            item = item_map.get(item_id)
            if not item:
                continue

            avg_placement = float(avg)
            overall_avg = overall_avgs_by_item_id.get(item_id)
            delta = round(avg_placement - overall_avg, 2) if overall_avg is not None else None

            if item.type == "artifact":
                percentage = count / total_artifacts if total_artifacts else 0
                is_low_sample = percentage < 0.02
            else: # radiant
                percentage = count / total_radiants if total_radiants else 0
                is_low_sample = percentage < 0.02

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
    """
    Returns stats for all champions who used a given item.

    For each champion, computes:
    - count: number of games this champion used the item
    - average_placement: champion's avg placement when using this item
    - delta: difference between the champion's avg placement with this item
             vs their overall avg placement across all games (from champion_stats table).
             Negative delta means the champion performs better than their baseline when using this item.
    - valid: whether this item/champion pair is considered a valid pair (item at least somewhat matches the champion's role, 
            so tank items are ignored for carries and such), data is taken from champion_item_valid_pairs table
    - low_sample: whether the champion appears in fewer than 1% of the item's games

    Results are sorted by delta ascending (best performing champions first).

    Args:
        item_riot_id: Riot's string ID for the item (e.g. "TFT_Item_Artifact_Fishbones").
        item_type: Either "artifact" or "radiant".

    Returns:
        Dict with item info and a champions sub-dict sorted by delta ascending.
        Returns None if the item is not found.
    """
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
                ChampionItemStats.patch == CURRENT_PATCH,
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

        overall_avgs_by_id = {
            row.champion_id: float(row.avg_placement)
            for row in db.query(
                ChampionStat.champion_id,
                func.avg(ChampionStat.placement).label("avg_placement"),
            )
            .join(Champion, Champion.id == ChampionStat.champion_id)
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
            
            overall_avg = overall_avgs_by_id.get(champion_id)
            delta = round(avg_placement - overall_avg, 2) if overall_avg is not None else None

            result[champion.riot_id] = {
                "name": champion.name,
                "cost": champion.cost,
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