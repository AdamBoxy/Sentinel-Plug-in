# src/agents.py
import asyncio
from typing import Any, Dict

class Agent:
    """Mock Base Agent class."""
    def __init__(self, name: str):
        self.name = name
    async def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Core agent handler (must be overridden)."""
        raise NotImplementedError

class UniversalModelAgent(Agent):
    """Simulates an underlying LLM, like Gemini 1.5 Flash."""
    async def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = input_data.get("message")
        print(f"[{self.name}] Processing prompt...")
        # Simulate model I/O time
        await asyncio.sleep(0.1)
        # Simulate a full, unedited response
        return {"response": f"The model processed: '{prompt}' and the output may contain sensitive data."}
