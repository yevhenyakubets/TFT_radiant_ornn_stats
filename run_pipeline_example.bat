@echo off
cd /d C:\path\to\your\project\backend
call venv\Scripts\activate
set PYTHONPATH=C:\path\to\your\project\backend
python -m backend.app.scripts.riot_ingest --tier diamond --division I
python -m backend.app.scripts.riot_ingest --tier diamond --division II
python -m backend.app.scripts.riot_ingest --tier diamond --division III
python -m backend.app.scripts.riot_ingest --tier diamond --division IV
python -m backend.app.scripts.riot_ingest --tier master
python -m backend.app.scripts.riot_ingest --tier grandmaster
python -m backend.app.scripts.riot_ingest --tier challenger
python -m backend.app.scripts.populate_champion_item_stats_table
python -m backend.app.scripts.populate_champion_stats_table