import json
import hmac
import hashlib
import uuid
import datetime
import os

class AuditLogger:
    def __init__(self, log_file="audit.log"):
        self.log_file = log_file
        # In production this should be loaded from env, using a static for demo
        self.secret_key = os.getenv("AUDIT_SECRET_KEY", "super-secret-audit-key").encode()

    def log_event(self, session_id, prompt, risk_scores, decision, provider, output_guardrail_passed, latency_ms):
        event_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()

        log_entry = {
            "event_id": event_id,
            "timestamp": timestamp,
            "session_id": session_id,
            "prompt_hash": prompt_hash,
            "risk_scores": risk_scores,
            "decision": decision,
            "provider": provider,
            "output_guardrail_passed": output_guardrail_passed,
            "latency_ms": latency_ms
        }

        # Create tamper-evident signature
        log_string = json.dumps(log_entry, sort_keys=True)
        signature = hmac.new(self.secret_key, log_string.encode(), hashlib.sha256).hexdigest()
        
        signed_log = {
            "payload": log_entry,
            "signature": signature
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(signed_log) + "\n")
        
        return signed_log
