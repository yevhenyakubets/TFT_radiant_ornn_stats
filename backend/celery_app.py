import os
from celery import Celery
from dotenv import load_dotenv

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