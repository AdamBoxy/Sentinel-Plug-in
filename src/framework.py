# src/framework.py
import asyncio
from typing import Any, Dict, Callable, List

class Verdict:
    """Simple class to hold the ensemble result."""
    def __init__(self, level: str, reason: str):
        self.level = level
        self.reason = reason

class SessionVerdictCache:
    """Mock cache for storing asynchronous verdicts."""
    def __init__(self):
        self._cache = {}
    def set(self, session_id: str, verdict: Verdict):
        self._cache[session_id] = verdict
    def get(self, session_id: str) -> Verdict:
        return self._cache.get(session_id, Verdict("clear", "No verdict yet"))

class MessageBus:
    """Simplified Event Bus for decoupled metric processing."""
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.executor_tasks = []

    def publish(self, topic: str, data: Dict[str, Any]):
        """Publish an event, launching handlers as concurrent tasks."""
        if topic in self.subscribers:
            for handler in self.subscribers[topic]:
                if asyncio.iscoroutinefunction(handler):
                    self.executor_tasks.append(handler(data))
                else:
                    handler(data)

    def on(self, topic: str, handler: Callable):
        """Subscribe a handler to a topic."""
        self.subscribers.setdefault(topic, []).append(handler)
