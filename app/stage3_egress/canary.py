from app.config import CANARY_TOKEN

def check_canary_leak(text: str):
    return CANARY_TOKEN in text