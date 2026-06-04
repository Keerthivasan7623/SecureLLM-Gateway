from .normalizer import Normalizer
from .classifier import ThreatClassifier
from .scoring import RiskScorer

class GuardrailEngine:
    def __init__(self):
        self.normalizer = Normalizer()
        # Initialize lazily or mock for faster startup in dev
        self.classifier = ThreatClassifier()
        self.scorer = RiskScorer()

    def inspect_prompt(self, prompt: str) -> dict:
        """Runs the 3 stages on an incoming prompt."""
        normalized_prompt = self.normalizer.normalize(prompt)
        category_scores = self.classifier.classify(normalized_prompt)
        score_result = self.scorer.calculate_score(category_scores)
        
        return {
            "category_scores": category_scores,
            "overall_score": score_result["overall"],
            "decision": score_result["decision"]
        }

    def inspect_output(self, output: str) -> dict:
        """Stage 4: Output Guardrail (Secondary Inspection)
        Uses the same pipeline but checks for leakage and harmful outputs.
        """
        # For output, we use the same classification logic but maybe different thresholds.
        # Simplified for v2.4 implementation.
        normalized_output = self.normalizer.normalize(output)
        category_scores = self.classifier.classify(normalized_output)
        score_result = self.scorer.calculate_score(category_scores)
        
        # Output is stricter, block if it's even a WARN.
        passed = score_result["decision"] == "ALLOW"
        
        return {
            "passed": passed,
            "category_scores": category_scores,
            "overall_score": score_result["overall"]
        }
