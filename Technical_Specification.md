# Technical Specification: Three-Tier AI Guardrail Middleware

## 1. Introduction
The **Three-Tier AI Guardrail** is a security proxy designed to protect Large Language Model (LLM) applications from Prompt Injection attacks. It sits between the user input and the LLM, intercepting malicious payloads across three distinct layers of detection.

## 2. System Architecture
The system is composed of a Flask-based API that routes incoming prompts through a sequential filtering pipeline.

### Tier 1: Regex & Homoglyph Detection
- **Purpose**: Catch known jailbreak patterns and Unicode-based obfuscation.
- **Mechanism**:
  - Regular expression matching for strings like "ignore previous instructions", "DAN", "system override".
  - Homoglyph normalization to prevent tricks using look-alike characters (e.g., using Cyrillic 'а' instead of Latin 'a').

### Tier 2: Semantic Intent Detection
- **Purpose**: Detect malicious intent that bypasses keyword filters.
- **Mechanism**:
  - **Vector Embedding**: Use `sentence-transformers` (e.g., `all-MiniLM-L6-v2`) to convert prompts into high-dimensional vectors.
  - **Vector DB**: Use `FAISS` to perform similarity searches against a curated dataset of known prompt injection attacks.
  - **Thresholding**: If the cosine similarity exceeds a specific threshold, the prompt is flagged.

### Tier 3: Forensic Structural Analysis
- **Purpose**: Identify obfuscation techniques used to hide malicious payloads.
- **Mechanism**:
  - Scanning for Base64, Hex, or ROT13 encoded strings.
  - Detecting unusual character distributions or structural anomalies common in injection payloads.

## 3. Custom Skills
- **/redteam**: A dedicated skill that utilizes a "Hacker" persona to generate and execute adversarial tests against the guardrail, reporting on block rates and bypasses.

## 4. Attack Dashboard
- A real-time monitoring interface (optimized for Samsung F41) that displays:
  - Total prompts processed.
  - Blocked vs. Allowed counts.
  - Breakdown of which tier caught the attack.
  - Recent logs of blocked payloads.

## 5. Technology Stack
- **Language**: Python 3.13+
- **Web Framework**: Flask
- **ML/NLP**: sentence-transformers, FAISS
- **Utilities**: qrcode (for mobile access), regex
- **Target Device**: Samsung F41 (2340 x 1080 resolution)

## 6. Security Personas
- **Security Architect**: Responsible for implementing robust filters and maintaining the guardrail logic.
- **Hacker**: Responsible for simulating attacks and finding vulnerabilities in the defensive layers.
