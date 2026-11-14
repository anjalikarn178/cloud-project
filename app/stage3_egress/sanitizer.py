import re

XSS_SQL_PATTERNS = [
    re.compile(r'<script.*?>.*?</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'\b(DROP|DELETE|UPDATE|INSERT)\s+TABLE\b', re.IGNORECASE),
    re.compile(r'javascript:', re.IGNORECASE)
]

def sanitize_output(text: str):
    for pattern in XSS_SQL_PATTERNS:
        text = pattern.sub('[REDACTED UNSAFE CODE]', text)
    return text