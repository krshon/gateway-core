from collections import defaultdict

# simple in-memory counters
metrics = defaultdict(int)

def inc(name: str):
    metrics[name] += 1

def snapshot():
    return dict(metrics)
