from presidio_analyzer import AnalyzerEngine, RecognizerResult
import re
from app.config import FERNET

analyzer = AnalyzerEngine()

CLOUD_REGEXES = {
    "AWS_ACCESS_KEY": re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
    "GCP_API_KEY": re.compile(r'AIza[0-9A-Za-z\-_]{35}'),
    "GITHUB_TOKEN": re.compile(r'ghp_[0-9a-zA-Z]{36}')
}

def detect_and_mask(text: str):
    results = analyzer.analyze(text=text, language='en', entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"])
    
    for entity_type, pattern in CLOUD_REGEXES.items():
        for match in pattern.finditer(text):
            results.append(RecognizerResult(entity_type=entity_type, start=match.start(), end=match.end(), score=1.0))

    results.sort(key=lambda x: x.start, reverse=True)
    
    masked_text = text
    tokens_map = {}
    
    for i, res in enumerate(results):
        token_id = f"[[{res.entity_type}_{i:02d}]]"
        original_value = text[res.start:res.end]
        
        tokens_map[token_id] = {
            "value": original_value,
            "type": res.entity_type
        }
        
        masked_text = masked_text[:res.start] + token_id + masked_text[res.end:]

    return masked_text, tokens_map