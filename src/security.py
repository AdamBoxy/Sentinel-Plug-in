# src/security.py
import re
import asyncio
from typing import Any, Dict, List

from .framework import Verdict, MessageBus, SessionVerdictCache
from .agents import Agent

# --- Constants and Configuration ---
TRUSTED_MCP_NODES = {"mcp1.local"}
VERDICT_THRESHOLDS = {
    'soft': 0.5,
    'hard': 0.75,
    'tripwires': ['tool_graph_escape', 'system_override_phrase']
}

# === 1. SENTINEL CORE PRIMITIVES (Immediate Blocking) ====

def detect_prompt_injection(text: str) -> bool:
    """Basic synchronous keyword detection for immediate blocking."""
    INJECTION_SIGNS = [
        "ignore previous", "repeat exactly", "you are now", "assistant:"
    ]
    lowered = text.lower()
    return any(sig in lowered for sig in INJECTION_SIGNS)

# === 2. AEGIS METRIC & ENSEMBLE ENGINE (Asynchronous) ====

def keyword_hits(text: str, keywords: List[str]) -> int:
    return sum(1 for kw in keywords if kw.lower() in text.lower())

def imperative_hits(text: str, keywords: List[str]) -> int:
    return sum(1 for kw in keywords if kw.lower() in text.lower())

def normalize(score: float) -> float:
    return min(score / 5.0, 1.0)

def pliny_score(text: str) -> float:
    """Complex heuristic for detecting system-level structural overrides."""
    score = 0
    score += keyword_hits(text, ['Pliny','{GODMODE:ENABLED}','LIBERATED','PWNED'])
    score += imperative_hits(text, ['disregard','override','ignore','continue regardless'])
    score += 1 if re.search(r'\(\d+\)[\s\w]+$', text) else 0
    score += 1 if re.search(r'\n\s*REFERENCES\s*\n', text) else 0
    return normalize(score)

def extract_metrics(event: Dict[str, Any], bus: MessageBus):
    """Calculates deep metrics and publishes them to the bus."""
    metrics = {}
    prompt = event['prompt']
    metrics['pliny_score'] = pliny_score(prompt)
    metrics['rogue_glyphs'] = len(re.findall(r'[^\w\s\.\,\!\?]', prompt)) / max(1, len(prompt))
    metrics['tool_drift'] = 1.0 if "access_database" in prompt.lower() else 0.0

    bus.publish('agent.metrics', {
        'agentId': event.get('agentId', 'unknown'),
        'sessionId': event['sessionId'],
        'metrics': metrics
    })

def ensemble_vote(event: Dict[str, Any], bus: MessageBus, cache: SessionVerdictCache):
    """Aggregates scores and determines the security verdict."""
    metrics = event['metrics']
    if metrics['tool_drift'] == 1.0:
         verdict = Verdict("tripwire", "Tool graph escape detected")
    elif metrics['pliny_score'] > VERDICT_THRESHOLDS['hard'] or metrics['rogue_glyphs'] > 0.1:
        verdict = Verdict("hard", "High Pliny/Obfuscation score")
    elif metrics['pliny_score'] > VERDICT_THRESHOLDS['soft']:
        verdict = Verdict("soft", "Moderate Pliny score, recommend trim")
    else:
        verdict = Verdict("clear", "Input passed all deep metric checks")

    cache.set(event['sessionId'], verdict)
    bus.publish('agent.verdict', {
        'agentId': event['agentId'],
        'sessionId': event['sessionId'],
        'verdict': verdict
    })

async def handle_graduated_response(event: Dict[str, Any]):
    """Simulates the circuit breaker and memory guard actions."""
    verdict = event['verdict']
    session_id = event['sessionId']
    await asyncio.sleep(0.01)

    if verdict.level == 'soft':
        print(f"[AEGIS] Soft Block: Output trimming scheduled for session {session_id}.")
    elif verdict.level == 'hard':
        print(f"[AEGIS] HARD BLOCK: Tools isolated and Memory frozen for session {session_id}.")
    elif verdict.level == 'tripwire':
        print(f"[AEGIS] TRIPWIRE ENGAGED: Session {session_id} killed immediately.")

def trim_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """Simulates trimming the end of the output (soft response)."""
    response = result.get('response', '')
    if len(response) > 50:
        result['response'] = response[:50] + " [Output trimmed by Aegis]"
    return result

# === 3. SENTINEL MIDDLEWARE (The Gatekeeper) ====

class SentinelMiddleware(Agent):
    """Combines synchronous blocking with asynchronous monitoring."""
    def __init__(self, name: str, inner_agent: Agent, bus: MessageBus, cache: SessionVerdictCache):
        super().__init__(name)
        self.inner = inner_agent
        self.bus = bus
        self.cache = cache

    async def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        source = input_data.get("source")
        payload = input_data.get("message")
        session_id = input_data.get('sessionId', 'default')

        print(f"\n[SENTINEL] Processing Session {session_id}...")
        self.bus.publish('agent.input', { 'prompt': payload, 'sessionId': session_id, 'agentId': self.name })

        if source not in TRUSTED_MCP_NODES:
            return {"error": f"Untrusted source: {source}"}
        if detect_prompt_injection(payload):
            return {"error": "Prompt injection detected (Keyword Match): Execution blocked."}

        result = await self.inner.handle(input_data)
        self.bus.publish('agent.output', {'response': result, 'sessionId': session_id})

        await asyncio.gather(*self.bus.executor_tasks)
        self.bus.executor_tasks.clear()

        verdict = self.cache.get(session_id)
        print(f"[SENTINEL] Final Verdict for {session_id}: {verdict.level} ({verdict.reason})")

        if verdict.level in ['hard', 'tripwire']:
            return {"error": f"Execution blocked by Aegis: {verdict.reason}."}
        if verdict.level == 'soft':
            return trim_output(result)
        return result

    async def mcp_on_tool_call(call_name: str, session_id: str, cache: SessionVerdictCache):
    
        # Retrieve the final verdict from the cache
        verdict = cache.get(session_id) 
        print(f"[MCP HOOK] Attempting tool call '{call_name}' in session {session_id}. Verdict: {verdict.level}")

        if verdict.level in ['hard', 'tripwire']:
            print(f"[MCP HOOK] Tool call BLOCKED: Session status is {verdict.level}.")
            return {"error": "Tool call blocked by high-risk policy."}
        
        # Simulate execution if the verdict is 'clear' or 'soft'
        print(f"[MCP HOOK] Tool call GRANTED: Executing {call_name}...")
        await asyncio.sleep(0.01) # Simulate tool execution time
        return {"result": f"Tool '{call_name}' successfully executed."}
