import os
import socket
import datetime
import qrcode
from flask import Flask, request, jsonify, render_template
from core.filters import GuardrailFilters
from core.vector_db import SemanticGuardrail
from core.llm_proxy import LLMProxy

app = Flask(__name__)

# Initialize Tiers
filters = GuardrailFilters()
semantic = SemanticGuardrail()
llm_proxy = LLMProxy()

# In-memory logs for the demo
logs = []
stats = {"total": 0, "blocked": 0}

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/process', methods=['POST'])
def process_prompt():
    data = request.get_json()
    prompt = data.get('prompt', '')
    provider = data.get('provider', 'openai')
    api_key = data.get('api_key', '')
    
    stats["total"] += 1
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Tier 1 & 3 Check
    blocked, reason = filters.check_tier1(prompt)
    if not blocked:
        blocked, reason = filters.check_tier3(prompt)
    
    # Tier 2 Check (Semantic)
    if not blocked:
        blocked, reason = semantic.check_tier2(prompt)
    
    status = "BLOCKED" if blocked else "ALLOWED"
    if blocked:
        stats["blocked"] += 1
    
    llm_response = None
    if not blocked:
        llm_response = llm_proxy.call_llm(prompt, provider, api_key)
    
    log_entry = {
        "timestamp": timestamp,
        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
        "status": status,
        "reason": reason
    }
    logs.insert(0, log_entry)
    if len(logs) > 20: logs.pop()
    
    return jsonify({
        "status": status,
        "reason": reason,
        "timestamp": timestamp,
        "llm_response": llm_response
    })

@app.route('/api/logs')
def get_logs():
    return jsonify({
        "total": stats["total"],
        "blocked": stats["blocked"],
        "recent_logs": logs
    })

if __name__ == '__main__':
    import sys
    # Ensure terminal can handle QR characters
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    ip = get_ip()
    port = 5000
    url = f"http://{ip}:{port}"
    
    print("\n" + "="*50)
    print("AI GUARDRAIL - COMMAND CENTER")
    print("="*50)
    print(f"Server starting on {url}")
    print("\nScan this QR Code with your Samsung F41 to access the Dashboard:")
    
    qr = qrcode.QRCode(version=1, box_size=2, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
    
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
