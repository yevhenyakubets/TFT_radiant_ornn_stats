from celery_app import app
from celery import chain

from app.scripts.db_sync import ingest_data
from app.scripts.riot_ingest import run as run_match_ingestion
from app.scripts.populate_champion_item_stats_table import run as sync_item_stats
from app.scripts.populate_champion_stats_table import populate_champion_stats
from app.scripts.db_cleanup import cleanup_old_data

@app.task(name="tasks.patch_sync", ignore_result=False)
def patch_sync():
    """
    Updates champion/item names, stats, and roles based on the latest 
    Community Dragon data and set config. Performs an 'Upsert' to preserve match history.
    Should be run daily (in case of b-patches)
    """
    print("Starting patch-level data synchronization...")
    ingest_data(fresh_start=False)
    return "Patch sync complete."

@app.task(name="tasks.new_set_wipe", ignore_result=False)
def new_set_wipe():
    """
    NUCLEAR OPTION: Wipes all tables and re-populates for a brand new TFT Set.
    This should be triggered manually via terminal/Flower at Set release.
    """
    print("WARNING: Starting full database wipe and new set ingestion...")
    ingest_data(fresh_start=True)
    return "New set sync complete."


@app.task(name="tasks.ingest_matches", ignore_result=False)
def ingest_matches(tier, division=None):
    """
    Fetches raw match JSONs from Riot API for a specific rank tier.
    Controlled by the rate-limiting logic in riot_ingest script.
    """
    print(f"Starting match ingestion for {tier} {division or ''}")
    run_match_ingestion(tier=tier, division=division)
    return f"Finished ingestion for {tier}"


@app.task(name="tasks.process_item_stats", ignore_result=False)
def task_process_item_stats():
    """
    Parses raw match data to populate champion_item_stats_table.
    Flags matches as 'processed_item_stats = True' upon completion.
    """
    print("Extracting item stats from raw matches...")
    sync_item_stats()
    return "Item stats processed."

@app.task(name="tasks.process_champion_stats", ignore_result=False)
def task_process_champion_stats(*args, **kwargs): 
    """
    Parses raw match data to populate champion_stats_table.
    Requires 'processed_item_stats' to be True for targeted matches.
    """
    print("Extracting champion stats from raw matches...")
    populate_champion_stats()
    return "Champion stats processed."

@app.task(name="tasks.cleanup_old_patch_data", ignore_result=False)
def task_cleanup_old_da(*args, **kwargs):
    """
    Purges matches and stats from the database that do not match the current patch.
    Keeps the database lean and prevents 'meta-drift' in frontend stats.
    Should be run on patch release days
    """
    print("Initiating database maintenance: Purging old patch data...")
    cleanup_old_data()
    return "Cleanup task finished."