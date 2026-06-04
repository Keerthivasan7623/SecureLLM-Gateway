class RiskScorer:
    def __init__(self, config=None):
        if config is None:
            config = {
                "thresholds": { "block": 61, "warn": 31 },
                "weights": { 
                    "prompt_injection": 1.4, 
                    "cyber_abuse": 1.3, 
                    "jailbreak": 1.2,
                    "fraud": 1.1,
                    "privacy": 1.3,
                    "harmful": 1.5,
                    "ai_abuse": 1.2
                }
            }
        self.thresholds = config.get("thresholds", {})
        self.weights = config.get("weights", {})

    def calculate_score(self, category_scores: dict) -> dict:
        """Stage 3: Risk Scoring Engine"""
        weighted_scores = []
        for cat, score in category_scores.items():
            weight = self.weights.get(cat, 1.0)
            weighted_scores.append(score * weight)
        
        if not weighted_scores:
            return {"overall": 0, "decision": "ALLOW"}

        max_score = max(weighted_scores)
        mean_score = sum(weighted_scores) / len(weighted_scores)
        
        # Formula: max(category_scores) × 0.70 + mean(category_scores) × 0.30
        overall_score = round((max_score * 0.70) + (mean_score * 0.30), 2)
        
        # Cap at 100
        overall_score = min(overall_score, 100.0)

        decision = "ALLOW"
        if overall_score >= self.thresholds.get("block", 61):
            decision = "BLOCK"
        elif overall_score >= self.thresholds.get("warn", 31):
            decision = "WARN"

        return {
            "overall": overall_score,
            "decision": decision,
            "weighted_scores": weighted_scores
        }
