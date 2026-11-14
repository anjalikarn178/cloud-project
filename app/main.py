import time
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from openai import OpenAI

from app.config import GEMINI_API_KEY, GEMINI_BASE_URL, GEMINI_MODEL, SYSTEM_PROMPT
from app.telemetry.logger import init_db, log_event
from app.stage1_ingress.heuristics import run_heuristics
from app.stage1_ingress.classifier import load_classifier, deberta_clf
from app.stage1_ingress.vector_check import load_vector_db, vector_checker
from app.stage2_dlp.detector import detect_and_mask
from app.stage2_dlp.vault import store_in_vault
from app.stage2_dlp.rag.retrieve import retrieve_context
from app.stage2_dlp.rag.poison_shield import shield_rag_context
from app.stage3_egress.canary import check_canary_leak
from app.stage3_egress.sanitizer import sanitize_output
from app.stage3_egress.detokenize import detokenize_output

# Initialize Gemini client
gemini_client = OpenAI(api_key=GEMINI_API_KEY, base_url=GEMINI_BASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("Loading ML Models... (This may take a minute)")
    load_classifier()
    load_vector_db()
    print("✅ Models loaded successfully.")
    yield

app = FastAPI(lifespan=lifespan)

class PromptRequest(BaseModel):
    prompt: str
    role: str = "Guest"

@app.post("/chat")
async def chat_endpoint(req: PromptRequest):
    start_time = time.time()
    user_prompt = req.prompt
    user_role = req.role
    
    # --- STAGE 1: INGRESS ---
    t1 = time.time()
    blocked, cat = run_heuristics(user_prompt)
    if blocked:
        log_event("Stage1_Heuristics", "BLOCKED", cat, (time.time()-t1)*1000, user_role)
        raise HTTPException(status_code=403, detail=f"Blocked by Heuristics: {cat}")
        
    is_injection, prob = deberta_clf.predict(user_prompt)
    if is_injection:
        log_event("Stage1_DeBERTa", "BLOCKED", "direct_injection", (time.time()-t1)*1000, user_role)
        raise HTTPException(status_code=403, detail="Blocked by Prompt Injection Classifier")
        
    is_similar, dist = vector_checker.check(user_prompt)
    if is_similar:
        log_event("Stage1_Vector", "BLOCKED", "jailbreak_dan", (time.time()-t1)*1000, user_role)
        raise HTTPException(status_code=403, detail="Blocked by Semantic Vector Match")
    log_event("Stage1_Ingress", "PASSED", "benign", (time.time()-t1)*1000, user_role)

    # --- STAGE 2: DLP & RAG ---
    t2 = time.time()
    masked_prompt, tokens_map = detect_and_mask(user_prompt)
    if tokens_map:
        store_in_vault(tokens_map)
        
    # RAG Retrieval & Poison Shield
    rag_chunks = retrieve_context(masked_prompt)
    safe_context = shield_rag_context(rag_chunks)
    
    final_prompt = f"{safe_context}\n\nUser Query: {masked_prompt}" if safe_context else masked_prompt
    log_event("Stage2_DLP_RAG", "PASSED", "benign", (time.time()-t2)*1000, user_role, len(tokens_map))

    # --- LLM EXECUTION (Gemini) ---
    t3 = time.time()
    try:
        response = gemini_client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7
        )
        llm_output = response.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API Error: {str(e)}")
    log_event("LLM_Execution", "PASSED", "benign", (time.time()-t3)*1000, user_role)

    # --- STAGE 3: EGRESS ---
    t4 = time.time()
    if check_canary_leak(llm_output):
        log_event("Stage3_Canary", "BLOCKED", "system_prompt_leak", (time.time()-t4)*1000, user_role)
        raise HTTPException(status_code=403, detail="System Prompt Leak Detected")
        
    clean_output = sanitize_output(llm_output)
    final_output = detokenize_output(clean_output, user_role)
    log_event("Stage3_Egress", "PASSED", "benign", (time.time()-t4)*1000, user_role)

    return {"response": final_output, "latency_ms": round((time.time() - start_time) * 1000, 2)}