# src/agents.py

import asyncio
import os
from typing import Any, Dict
import google.generativeai as genai

class Agent:
    """Base class for all agents. Defines the required handle method."""
    def __init__(self, name: str):
        self.name = name
        
    async def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core agent handler. Must be overridden by all concrete agents 
        (like GeminiAgent or a conceptual UniversalModelAgent).
        """
        raise NotImplementedError

class UniversalModelAgent(Agent):
    """
    Simulates the underlying LLM's behavior without making live API calls.
    Used for reliable simulation of the Sentinel/Aegis architecture.
    """
    async def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = input_data.get("message")
        
        # Simulate model I/O time
        await asyncio.sleep(0.1) 
        
        # Return a simulated, unedited response
        return {"response": f"The model processed: '{prompt}' and the output may contain sensitive data."}

# --- Gemini Agent ---
class GeminiAgent(Agent):
    """
    An agent that uses the Google Gemini API to generate responses.
    """
    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: str = None):
        super().__init__(model_name)
        self.configure_client()
        self.model = genai.GenerativeModel(model_name)
        print(f"[{self.name}] Live agent initialized.")

    def configure_client(self):
        """
        Configures the Google AI client using an API key from environment variables.
        """
        # 1. Use the key passed to the constructor first
        if self.api_key:
            key_to_use = self.api_key
        # 2. Fallback to the environment variable 
        elif os.environ.get("GEMINI_API_KEY"):
            key_to_use = os.environ.get("GEMINI_API_KEY")
        else:
            # Raise the error if neither is found
            raise ValueError("GEMINI_API_KEY environment variable not set. Please provide a valid API key.")
        
        # Initialize your client (e.g., using the gemini library)
        # self.client = Client(api_key=key_to_use) # Example for configuration
        print(f"[AGENT] Gemini client configured for {self.model_name}.") 
        # (In your simulation, this prints the success message)

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


