from celery.schedules import crontab

TIER_CONFIGS = [
    {"name": "challenger", "tier": "challenger", "div": None, "sch": crontab(hour=1, minute=0)},
    {"name": "grandmaster", "tier": "grandmaster", "div": None, "sch": crontab(hour=2, minute=0)},
    
    {"name": "master", "tier": "master", "div": None, "sch": crontab(hour='0,8,16', minute=30)},
    
    {"name": "diamond-iv", "tier": "diamond", "div": "IV", "sch": 900.0},
    {"name": "emerald-iv", "tier": "emerald", "div": "IV", "sch": 900.0},
    
    {"name": "diamond-iii", "tier": "diamond", "div": "III", "sch": 1800.0},
    {"name": "emerald-iii", "tier": "emerald", "div": "III", "sch": 1800.0},

    {"name": "diamond-ii", "tier": "diamond", "div": "II", "sch": 2700.0},
    {"name": "emerald-ii", "tier": "emerald", "div": "II", "sch": 2700.0},

    {"name": "diamond-i", "tier": "diamond", "div": "I", "sch": 3600.0},
    {"name": "emerald-i", "tier": "emerald", "div": "I", "sch": 3600.0},
]