import json
import logging

logging.basicConfig(level=logging.INFO)

def log_event(data: dict):
    logging.info(json.dumps(data))
