import os
from celery import Celery, chain
from celery.schedules import crontab
from dotenv import load_dotenv
from app.constants.tier_config import TIER_CONFIGS

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    'tft_stats',
    broker=redis_url,
    backend=redis_url,
    include=['app.tasks']
)

app.conf.update(
    result_expires=3600,
    timezone='UTC',
)

app.conf.beat_schedule = {
    'daily-patch-sync': {
        'task': 'tasks.patch_sync',
        'schedule': crontab(hour=4, minute=0),
    },
    'periodic-stats-processing': {
        'task': 'tasks.process_item_stats',
        'schedule': 1800.0,
        'options': {
            'link': ['tasks.process_champion_stats'] 
        }
    },
    'bi-weekly-db-cleanup': {
        'task': 'tasks.cleanup_old_patch_data',
        'schedule': crontab(minute=0, hour='*/2'),
    },
}

for entry in TIER_CONFIGS:
    app.conf.beat_schedule[f"ingest-{entry['name']}"] = {
        'task': 'tasks.ingest_matches',
        'schedule': entry['sch'],
        'args': (entry['tier'], entry['div']),
    }