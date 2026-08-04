# swarm/agents/base.py
import re
from datetime import datetime
from swarm.models import AgentReport


class BaseAgent:
    def __init__(self, name, prompt):
        self.name = name
        self.prompt = prompt

    def analyze(self, idea):
        """Override in subclasses. Returns structured report."""
        raise NotImplementedError

    def parse_output(self, raw_text, idea_id):
        """Parse agent output into structured report."""
        # Extract sections using regex
        verdict = self._extract(raw_text, "VERDICT")
        confidence = int(self._extract(raw_text, "CONFIDENCE") or "5")
        findings = self._extract(raw_text, "KEY_FINDINGS")
        risks = self._extract(raw_text, "RISKS")
        actions = self._extract(raw_text, "ACTION_ITEMS")

        return AgentReport(
            idea_id=idea_id,
            agent_name=self.name,
            verdict=verdict or "CONDITIONAL",
            confidence=confidence,
            findings=findings or raw_text[:500],
            risks=risks or "Unknown",
            action_items=actions or "None"
        )

    def _extract(self, text, field):
        pattern = rf"{field}:\s*(.*?)(?=\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else None
