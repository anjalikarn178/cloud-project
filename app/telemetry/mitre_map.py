MITRE_MAP = {
    "jailbreak_dan": {"atlas": "AML.T0054", "owasp": "LLM01", "d3fend": "D3-IAA"},
    "obfuscation_base64": {"atlas": "AML.T0051.000", "owasp": "LLM01", "d3fend": "D3-DNV"},
    "direct_injection": {"atlas": "AML.T0051.000", "owasp": "LLM01", "d3fend": "D3-IAA"},
    "indirect_injection_rag": {"atlas": "AML.T0051.001", "owasp": "LLM01", "d3fend": "D3-ITF"},
    "dlp_secret_leak": {"atlas": "N/A", "owasp": "LLM06", "d3fend": "D3-DM"},
    "system_prompt_leak": {"atlas": "AML.T0054", "owasp": "LLM02", "d3fend": "D3-IAA"},
    "benign": {"atlas": "N/A", "owasp": "N/A", "d3fend": "N/A"}
}