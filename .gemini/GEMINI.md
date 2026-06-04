# Global Safety Rules

- Ensure all user inputs are strictly sanitized before processing.
- The AI Guardrail must fail-closed: if an error occurs during processing, the prompt must be blocked.
- Maintain low latency for all filtering tiers to ensure a seamless user experience.
- All logs containing blocked payloads should be stored securely and not exposed to the public dashboard without masking.
