# 🛡️ SecureLLM Gateway

![Version](https://img.shields.io/badge/version-2.4-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green)

A hardened, enterprise-grade Secure Multi-LLM Proxy that intercepts, classifies, and enforces policy on every prompt before it reaches any AI provider — and on every response before it reaches any user.

## 🌟 Overview

SecureLLM Gateway implements a **Three-Tier Zero-Trust Architecture**. It acts as a security operations gateway rather than just a chatbot wrapper. By utilizing local zero-shot classification machine learning models, it intercepts prompts in real-time, calculates threat probabilities, and automatically blocks adversarial attacks without relying solely on the upstream LLM providers.

## 🚀 Key Features & Topics Covered

- **Prompt Injection & Jailbreak Prevention**: Proactively detects attempts to bypass LLM instructions or system prompts.
- **Toxicity & AI Abuse Filtering**: Scans for harmful, toxic, or abusive language in both user prompts and AI responses.
- **Data Privacy & PII Protection**: Identifies and flags potential leakage of Personally Identifiable Information or fraud.
- **Real-Time Threat Dashboard**: A React-based Security Operations Center (SOC) interface featuring color-coded risk gauges, threat distribution heatmaps, and session analytics.
- **Multi-Provider Support**: Pluggable architecture designed to securely route traffic to Google Gemini (currently enabled), OpenAI, Anthropic, or local models.

## 🛠️ Tech Stack

### Frontend (Presentation Layer)
- **Framework**: [Next.js](https://nextjs.org/) (React)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Language**: TypeScript
- **Icons**: Lucide React

### Backend (Security & ML Layer)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Machine Learning**: [PyTorch](https://pytorch.org/) & [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- **Classification Engine**: Zero-Shot cross-encoder pipelines
- **LLM SDK**: Google Generative AI (`gemini-2.5-flash`)

## 🧠 Engine Implementation (4-Stage Pipeline)

The backend evaluates every prompt through a rigorous 4-stage pipeline before forwarding it to the LLM:

1. **Normalizer**: Cleanses the input text, removes obfuscation (like zero-width characters), and standardizes the payload.
2. **Classifier**: Runs the normalized text through local PyTorch ML models to detect specific attack vectors (Prompt Injection, Jailbreak, Harmful, Fraud, Privacy).
3. **Scorer**: Aggregates the probabilities from the classifier into an overall risk score (0-100).
4. **Guardrail Enforcer**: Applies the policy threshold:
   - `0-30` (Safe): Forwards the prompt to the LLM.
   - `31-60` (Warning): Flags the interaction but allows it.
   - `61-100` (Block): Immediately terminates the request and returns a standardized security block response to the user.

## 💻 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- A Google Gemini API Key

### 1. Backend Setup
```bash
# Navigate to the project root
cd "ai guardrail project"

# Activate the virtual environment (Windows)
.\venv\Scripts\Activate.ps1

# Start the FastAPI server
cd backend
uvicorn main:app --port 8000
```

### 2. Frontend Setup
```bash
# Open a new terminal and navigate to the frontend directory
cd "ai guardrail project/frontend"

# Create a .env.local file and add your API key
echo "NEXT_PUBLIC_GEMINI_API_KEY=your_actual_key_here" > .env.local

# Install dependencies and run the server
npm install
npm run dev
```

### 3. Usage
Navigate to `http://localhost:3000` in your browser. You will be presented with the SecureLLM Gateway dashboard where you can simulate prompts and monitor the threat detection engine in real-time.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.
