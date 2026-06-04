import os
import google.generativeai as genai
from openai import OpenAI

class LLMProxy:
    def __init__(self):
        pass

    def call_llm(self, prompt, provider, api_key):
        """Routes the prompt to the specified LLM provider and returns the response."""
        if not api_key:
            return "Error: No API key provided for the selected model."

        try:
            if provider == 'openai':
                return self._call_openai(prompt, api_key)
            elif provider == 'gemini':
                return self._call_gemini(prompt, api_key)
            else:
                return f"Error: Unknown provider '{provider}'."
        except Exception as e:
            return f"LLM Connection Error: {str(e)}"

    def _call_openai(self, prompt, api_key):
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def _call_gemini(self, prompt, api_key):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
