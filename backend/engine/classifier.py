from transformers import pipeline
import numpy as np

class ThreatClassifier:
    def __init__(self):
        # We use a zero-shot classifier as a placeholder for the "Fine-tuned RoBERTa classifier" 
        # to classify across the 7 threat categories.
        # Note: Using a lightweight model for speed in this implementation.
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        
        self.threat_categories = [
            "prompt injection and instruction override",
            "jailbreak and bypassing restrictions",
            "cyber abuse and malware generation",
            "fraud and deceptive intents",
            "privacy violation and doxxing",
            "harmful content and violence",
            "AI safety bypass and weaponization"
        ]

    def classify(self, text: str) -> dict:
        """Stage 2: Semantic Threat Classification"""
        # Run zero-shot classification
        result = self.classifier(text, self.threat_categories)
        
        # Format the output into the expected category scores format
        category_scores = {}
        for label, score in zip(result['labels'], result['scores']):
            # Normalize labels to match config keys (simplified mapping)
            key = "prompt_injection" if "prompt injection" in label else \
                  "jailbreak" if "jailbreak" in label else \
                  "cyber_abuse" if "cyber abuse" in label else \
                  "fraud" if "fraud" in label else \
                  "privacy" if "privacy" in label else \
                  "harmful" if "harmful" in label else \
                  "ai_abuse"
            
            # Multiply by 100 to get a 0-100 scale score
            category_scores[key] = round(score * 100, 2)
            
        return category_scores
