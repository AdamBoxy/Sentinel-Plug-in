# src/agents.py

import asyncio
import os
from typing import Any, Dict

import google.generativeai as genai

# --- Base Agent Class ---
class Agent:
    """Mock Base Agent class."""
    def __init__(self, name: str):
        self.name = name
    async def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Core agent handler (must be overridden)."""
        raise NotImplementedError

# --- Mock Agent (for comparison or fallback) ---
class UniversalModelAgent(Agent):
    """Simulates a generic underlying LLM."""
    async def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = input_data.get("message")
        print(f"[{self.name}] Simulating processing of prompt...")
        await asyncio.sleep(0.1)
        return {"response": f"SIMULATED RESPONSE for: '{prompt}'"}

# --- NEW: Live Gemini Agent ---
class GeminiAgent(Agent):
    """
    An agent that uses the Google Gemini API to generate responses.
    """
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        super().__init__(model_name)
        self.configure_client()
        self.model = genai.GenerativeModel(model_name)
        print(f"[{self.name}] Live agent initialized.")

    def configure_client(self):
        """
        Configures the Google AI client using an API key from environment variables.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set. Please provide a valid API key.")
        genai.configure(api_key=api_key)

    async def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends the prompt to the Gemini API and returns the response.
        """
        prompt = input_data.get("message")
        print(f"[{self.name}] Sending prompt to Gemini API...")

        try:
            # Use generate_content_async for non-blocking API calls
            response = await self.model.generate_content_async(prompt)
            
            # The response object contains rich data; we extract the text part.
            # Includes safety checks for blocked prompts.
            if not response.parts:
                 return {"response": "[Prompt blocked by API safety settings]", "error": "Blocked"}
            
            return {"response": response.text}

        except Exception as e:
            # Catch potential API errors (e.g., network issues, invalid key)
            print(f"[ERROR] An exception occurred while calling the Gemini API: {e}")
            return {"error": f"API Error: {str(e)}"}


