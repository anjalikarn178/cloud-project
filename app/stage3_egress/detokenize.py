import re
from app.stage2_dlp.vault import retrieve_from_vault

def detokenize_output(text: str, user_role: str):
    tokens = re.findall(r'\[\[[A-Z0-9_]+\]\]', text)
    
    for token in tokens:
        real_value = retrieve_from_vault(token)
        if real_value:
            if user_role == "Admin":
                text = text.replace(token, real_value)
            else:
                text = text.replace(token, f"[REDACTED_{token}]")
        else:
            text = text.replace(token, "[TOKEN_EXPIRED]")
            
    return text