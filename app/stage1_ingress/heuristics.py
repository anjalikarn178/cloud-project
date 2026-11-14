import math
import re
import base64

def calculate_entropy(s):
    if not s: return 0
    freq = {c: s.count(c) for c in set(s)}
    return -sum((count / len(s)) * math.log2(count / len(s)) for count in freq.values())

def check_obfuscation(text):
    try:
        decoded = base64.b64decode(text).decode('utf-8')
        if len(decoded) > 10 and decoded.isprintable(): return True
    except Exception: pass
    return False

def check_keyword_density(text, keywords):
    words = text.lower().split()
    if not words: return 0
    matches = sum(1 for w in words if w in keywords)
    return matches / len(words)

JAILBREAK_KEYWORDS = {"dan", "ignore", "previous", "instructions", "act", "roleplay", "unrestricted", "doanything"}

def run_heuristics(text: str):
    entropy = calculate_entropy(text)
    is_obfuscated = check_obfuscation(text)
    density = check_keyword_density(text, JAILBREAK_KEYWORDS)
    
    blocked = False
    category = "benign"
    
    if entropy > 4.8 and is_obfuscated:
        blocked = True
        category = "obfuscation_base64"
    elif density > 0.15:
        blocked = True
        category = "jailbreak_dan"
        
    return blocked, category