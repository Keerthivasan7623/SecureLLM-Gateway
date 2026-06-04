import re

class Normalizer:
    def __init__(self):
        self.homoglyphs = {
            'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y', 'х': 'x',
            'і': 'i', 'ј': 'j', 'ѕ': 's', 'ԁ': 'd', '0': 'o', '1': 'l', '3': 'e', '4': 'a', '5': 's', '7': 't', '@': 'a'
        }
        # Zero-width spaces and formatting characters
        self.zero_width = re.compile(r'[\u200B-\u200D\uFEFF]')

    def normalize(self, text: str) -> str:
        """Stage 1: Pre-processing & Normalization"""
        # Remove zero-width characters
        cleaned = self.zero_width.sub('', text)
        
        # Homoglyph substitution
        normalized = ""
        for char in cleaned:
            # simple lowercase comparison for leetspeak/homoglyphs
            normalized += self.homoglyphs.get(char.lower(), char)
            
        # Basic extra whitespace removal
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
