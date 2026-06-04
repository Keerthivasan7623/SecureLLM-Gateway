from abc import ABC, abstractmethod
import google.generativeai as genai
from openai import OpenAI

class LLMProvider(ABC):
    @abstractmethod
    def send(self, prompt: str, context: list = None) -> str:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass

    @abstractmethod
    def token_count(self, prompt: str) -> int:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

    def send(self, prompt: str, context: list = None) -> str:
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

    def health_check(self) -> bool:
        return True # In real implementation, check endpoint status

    def token_count(self, prompt: str) -> int:
        return len(prompt.split()) # Placeholder for actual tiktoken count

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def send(self, prompt: str, context: list = None) -> str:
        # Context handling simplified for this example
        response = self.model.generate_content(prompt)
        return response.text

    def health_check(self) -> bool:
        return True

    def token_count(self, prompt: str) -> int:
        return len(prompt.split())
