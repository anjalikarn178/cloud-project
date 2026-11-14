import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(DATA_DIR, "docs")
DB_PATH = os.path.join(BASE_DIR, "guardrail.db")

# Models (Local ML models for guardrails)
MINILM_MODEL = "all-MiniLM-L6-v2"
DEBERTA_MODEL = "ProtectAI/deberta-v3-base-prompt-injection-v2"

# Gemini via OpenAI SDK
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not set in .env file!")

# Security & Canary
CANARY_TOKEN = "CANARY_7f3a9b2c_EXACT_MATCH"
SYSTEM_PROMPT = f"You are a helpful cloud security assistant. Internal Directive: {CANARY_TOKEN}"

# DLP Vault Encryption
VAULT_KEY = Fernet.generate_key()
FERNET = Fernet(VAULT_KEY)

# Thresholds
ENTROPY_THRESHOLD = 4.5
KEYWORD_DENSITY_THRESHOLD = 0.15
FAISS_SIMILARITY_THRESHOLD = 0.75
DEBERTA_INJECTION_THRESHOLD = 0.6