from datetime import datetime, timezone

# Maps each TFT patch version to its release date.
# Note: the Riot API reports the previous patch in the game_version string,
# so patch detection is done by match timestamp rather than parsing the version string.
PATCH_SCHEDULE = {
    "16.2": datetime(2026, 1, 8, tzinfo=timezone.utc),
    "16.3": datetime(2026, 1, 22, tzinfo=timezone.utc),
    "16.4": datetime(2026, 2, 4, tzinfo=timezone.utc),
    "16.5": datetime(2026, 2, 19, tzinfo=timezone.utc),
    "16.6": datetime(2026, 3, 4, tzinfo=timezone.utc),
    "16.7": datetime(2026, 3, 18, tzinfo=timezone.utc),
    "16.8": datetime(2026, 4, 1, tzinfo=timezone.utc),
    "17.1": datetime(2026, 4, 15, tzinfo=timezone.utc),
    "17.2": datetime(2026, 4, 29, tzinfo=timezone.utc),
    "17.3": datetime(2026, 5, 13, tzinfo=timezone.utc),
    "17.4": datetime(2026, 5, 28, tzinfo=timezone.utc),
    "17.5": datetime(2026, 6, 10, tzinfo=timezone.utc),
    "17.6": datetime(2026, 6, 24, tzinfo=timezone.utc),
    "17.7": datetime(2026, 7, 15, tzinfo=timezone.utc),
    "18.1": datetime(2026, 7, 29, tzinfo=timezone.utc),
    "18.2": datetime(2026, 8, 12, tzinfo=timezone.utc),
    "18.3": datetime(2026, 8, 26, tzinfo=timezone.utc),
    "18.4": datetime(2026, 9, 10, tzinfo=timezone.utc),
    "18.5": datetime(2026, 9, 23, tzinfo=timezone.utc),
    "18.6": datetime(2026, 10, 7, tzinfo=timezone.utc),
    "18.7": datetime(2026, 10, 21, tzinfo=timezone.utc),
    "18.8": datetime(2026, 11, 4, tzinfo=timezone.utc),
    "19.1": datetime(2026, 11, 18, tzinfo=timezone.utc),
    "19.2": datetime(2026, 12, 7, tzinfo=timezone.utc),
}


def get_current_patch() -> str | None:
    """
    Returns the current TFT patch version based on today's date.
    Iterates through PATCH_SCHEDULE in chronological order and returns
    the last patch whose start date is on or before now.
    Returns None if the current date is before all known patches.
    """
    now = datetime.now(timezone.utc)
    sorted_patches = sorted(PATCH_SCHEDULE.items(), key=lambda x: x[1])
    current_patch = None

    for patch, start_date in sorted_patches:
        if now >= start_date:
            current_patch = patch
        else:
            break

    return current_patch


def get_patch_for_timestamp(timestamp_ms: int) -> str | None:
    """
    Returns the TFT patch version that was active when a match was played.

    Args:
        timestamp_ms: Match start time in milliseconds (from Riot API game_datetime field).

    Returns:
        Patch version string (e.g. "16.7") or None if the match predates all known patches.
    """
    match_date = datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc)
    sorted_patches = sorted(PATCH_SCHEDULE.items(), key=lambda x: x[1])
    current_patch = None

    for patch, start_date in sorted_patches:
        if match_date >= start_date:
            current_patch = patch
        else:
            break

    return current_patch

def get_current_set() -> int | None:
    """
    Returns the current TFT Set number based on today's date.
    
    Extracts the major version number from the current patch identified 
    in the PATCH_SCHEDULE. For example, if the current patch is "17.2", 
    this returns 17.
    
    Returns:
        The current Set as an integer (e.g., 17) or None if no patch is active.
    """
    patch = get_current_patch()
    if patch:
        try:
            # Splits "17.2" into ["17", "2"] and takes the first part
            return int(patch.split('.')[0])
        except (ValueError, IndexError):
            return None
    return None

def get_set_for_timestamp(timestamp_ms: int) -> int | None:
    """
    Returns the TFT Set number that was active when a match was played.

    Args:
        timestamp_ms: Match start time in milliseconds.

    Returns:
        The Set number as an integer or None if the match predates the schedule.
    """
    patch = get_patch_for_timestamp(timestamp_ms)
    if patch:
        try:
            return int(patch.split('.')[0])
        except (ValueError, IndexError):
            return None
    return None