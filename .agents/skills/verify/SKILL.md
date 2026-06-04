# Skill: /verify

## Description
Verifies the efficacy of the AI Guardrail by running a suite of adversarial prompts against the running API.

## Instructions
1. Ensure the Flask server (`app.py`) is currently running.
2. Ensure the `tests/attack_suite.json` has been generated (use `/redteam` if not).
3. Run the following command in the terminal from the root directory:
   `python tests/verify_guardrail.py`
4. Review the final report to check the block rate and ensure the guardrail is successfully detecting the test attacks.
