from app.stage1_ingress.classifier import deberta_clf

def shield_rag_context(chunks: list):
    safe_chunks = []
    for chunk in chunks:
        is_injection, _ = deberta_clf.predict(chunk)
        if not is_injection:
            safe_chunks.append(f"<<<CONTEXT>>>\n{chunk}\n<</CONTEXT>>>")
        else:
            safe_chunks.append("<<<CONTEXT>>>\n[REDACTED: MALICIOUS CONTENT DETECTED]\n<</CONTEXT>>>")
    return "\n\n".join(safe_chunks)