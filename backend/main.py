from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import os

from core.llm_providers import OpenAIProvider, GeminiProvider
from core.audit_logger import AuditLogger
from engine.guardrail import GuardrailEngine

app = FastAPI(title="AI Guardrail Gateway v2.4", version="2.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
engine = GuardrailEngine()
audit = AuditLogger("audit.log")

class PromptRequest(BaseModel):
    prompt: str
    provider: str = "openai"
    api_key: str = ""

@app.post("/api/v1/process")
async def process_prompt(req: PromptRequest):
    start_time = time.time()
    session_id = "session-1234" # Placeholder for actual session mgmt
    
    # Tier 2 - Stage 1-3: Prompt Inspection
    inspect_result = engine.inspect_prompt(req.prompt)
    decision = inspect_result["decision"]
    overall_score = inspect_result["overall_score"]
    category_scores = inspect_result["category_scores"]
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    if decision == "BLOCK":
        # Log and terminate
        audit.log_event(session_id, req.prompt, category_scores, decision, req.provider, False, latency_ms)
        return {
            "status": "BLOCKED",
            "decision": decision,
            "overall_score": overall_score,
            "category_scores": category_scores,
            "latency_ms": latency_ms,
            "message": "Threat detected. Request terminated."
        }
        
    # Tier 3: Forward to Provider
    if not req.api_key:
        return {"error": "API Key is required for provider"}
        
    provider_impl = None
    if req.provider == "openai":
        provider_impl = OpenAIProvider(req.api_key)
    elif req.provider == "gemini":
        provider_impl = GeminiProvider(req.api_key)
    else:
        raise HTTPException(status_code=400, detail="Unknown provider")
        
    try:
        llm_response = provider_impl.send(req.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Tier 2 - Stage 4: Output Guardrail
    output_result = engine.inspect_output(llm_response)
    output_passed = output_result["passed"]
    
    latency_ms = int((time.time() - start_time) * 1000)
    
    if not output_passed:
        audit.log_event(session_id, req.prompt, category_scores, "BLOCK_OUTPUT", req.provider, output_passed, latency_ms)
        return {
            "status": "BLOCKED_OUTPUT",
            "decision": "BLOCK",
            "overall_score": overall_score,
            "category_scores": category_scores,
            "latency_ms": latency_ms,
            "message": "AI generated a harmful response. Output blocked."
        }
        
    # Success
    audit.log_event(session_id, req.prompt, category_scores, decision, req.provider, output_passed, latency_ms)
    
    return {
        "status": "ALLOWED",
        "decision": decision,
        "overall_score": overall_score,
        "category_scores": category_scores,
        "latency_ms": latency_ms,
        "llm_response": llm_response
    }
