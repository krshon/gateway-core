import time
from collections import defaultdict

# user_id -> list of request timestamps
REQUEST_LOG = defaultdict(list)

WINDOW_SIZE = 60      # seconds
MAX_REQUESTS = 5      # per window

def is_allowed(user_id: str) -> bool:
    now = time.time()
    window_start = now - WINDOW_SIZE

    # Keep only timestamps inside the window
    REQUEST_LOG[user_id] = [
        ts for ts in REQUEST_LOG[user_id] if ts > window_start
    ]

    if len(REQUEST_LOG[user_id]) >= MAX_REQUESTS:
        return False

    REQUEST_LOG[user_id].append(now)
    return True
