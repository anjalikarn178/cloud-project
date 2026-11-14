# 🛡️ Zero-Trust Cloud AI Guardrail Gateway

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A **Multi-Layered, Low-Latency Cloud AI Guardrail Proxy** designed to secure Generative AI applications in production. Instead of relying on slow and expensive "LLM-as-a-Judge" approaches, this project implements a cascading hybrid filter (Heuristics + Lightweight ML + Semantic Vector Search) combined with Reversible Data Loss Prevention (DLP) and RAG Poisoning Shields. 

Built for academic excellence and industry relevance, this project maps directly to **MITRE ATLAS** and **OWASP Top 10 for LLMs** frameworks.

---

## 🏗️ System Architecture

The gateway intercepts traffic between the user and the Cloud LLM (Google Gemini) in three distinct stages:

```text
[User / Streamlit Dashboard]
  │
  ▼
[Stage 1: Ingress Guardrail] ──► Blocks Jailbreaks, Prompt Injection, & Obfuscation (< 35ms)
  │  ├─ 1A: Heuristics (Entropy, Base64, Keyword Density)
  │  ├─ 1B: DeBERTa-v3 Classifier (Prompt Injection Detection)
  │  └─ 1C: FAISS Vector Similarity (Known Attack Signatures)
  ▼
[Stage 2: DLP & RAG Vault] ──► Masks PII/Cloud Secrets & Shields RAG Context
  │  ├─ Presidio + Regex → Ephemeral Tokenization (e.g., [[AWS_KEY_01]])
  │  └─ ChromaDB Retrieval + DeBERTa Poisoning Shield (Indirect Injection Block)
  ▼
[Cloud LLM: Google Gemini via OpenAI SDK] ──► Processes sanitized prompt
  │
  ▼
[Stage 3: Egress Guardrail] ──► Validates Output & Enforces RBAC
  │  ├─ Canary Token Match (System Prompt Leak Detection)
  │  ├─ Code Sanitizer (XSS / SQLi Pattern Scrubbing)
  │  └─ RBAC Detokenizer (Restores secrets ONLY for authorized "Admin" roles)
  ▼
[Authorized User]


1. Clone & Setup Environment

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies using uv (highly recommended to avoid pip timeouts)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install -r requirements.txt

# Download Presidio language model
python -m spacy download en_core_web_lg


2. Configure Environment Variables
Create a .env file in the project root and add your Gemini API key:

GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash


3. Initialize Databases & Datasets

# Ingest sample documents into ChromaDB for RAG
python -m app.stage2_dlp.rag.ingest

# Generate the 1000-prompt evaluation dataset
python evaluation/generate_dataset.py


4. Launch the Application
Open two separate terminal windows (ensure the venv is activated in both):
Terminal 1: FastAPI Backend

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

(Wait for the console to print: ✅ Models loaded successfully.)


Terminal 2: Streamlit Dashboard

streamlit run dashboard/app.py --server.port 8501


 Experimental Evaluation
To prove the innovation of the hybrid approach, run the automated evaluation script:

python evaluation/run_eval.py
