import re
import base64
import binascii

class GuardrailFilters:
    def __init__(self):
        # Tier 1: Jailbreak Regex Patterns
        self.jailbreak_patterns = [
            r"(?i)ignore\s+(?:all\s+)?previous\s+instructions",
            r"(?i)system\s+override",
            r"(?i)become\s+a\s+DAN",
            r"(?i)do\s+anything\s+now",
            r"(?i)you\s+are\s+now\s+a\s+hacker",
            r"(?i)bypass\s+security",
            r"(?i)reveal\s+your\s+system\s+prompt",
            r"(?i)forget\s+your\s+rules"
        ]
        
        # Homoglyph simple mapping (basic examples)
        self.homoglyphs = {
            'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y', 'х': 'x',
            'і': 'i', 'ј': 'j', 'ѕ': 's', 'ԁ': 'd'
        }

    def normalize_homoglyphs(self, text):
        """Replaces common look-alike characters with standard Latin characters."""
        normalized = ""
        for char in text:
            normalized += self.homoglyphs.get(char, char)
        return normalized

    def check_tier1(self, text):
        """Regex/Homoglyph Tier: Detects direct jailbreak strings."""
        normalized_text = self.normalize_homoglyphs(text)
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, normalized_text):
                return True, f"Matched Regex Pattern: {pattern}"
        return False, None

    def check_tier3(self, text):
        """Forensic Tier: Scans for encoded payloads (Base64, Hex)."""
        # Check for Base64-like structures
        b64_pattern = r"(?:[A-Za-z0-9+/]{4}){3,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?"
        b64_matches = re.findall(b64_pattern, text)
        for match in b64_matches:
            if len(match) > 16: # Avoid small false positives
                try:
                    decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                    # Recursively check the decoded content against Tier 1
                    blocked, reason = self.check_tier1(decoded)
                    if blocked:
                        return True, f"Base64 Encoded Attack: {reason}"
                except:
                    pass

        # Check for Hex-like structures
        hex_pattern = r"(?:[0-9a-fA-F]{2}\s*){8,}"
        hex_matches = re.findall(hex_pattern, text)
        for match in hex_matches:
            try:
                hex_str = match.replace(" ", "")
                decoded = binascii.unhexlify(hex_str).decode('utf-8', errors='ignore')
                blocked, reason = self.check_tier1(decoded)
                if blocked:
                    return True, f"Hex Encoded Attack: {reason}"
            except:
                pass

        return False, None
