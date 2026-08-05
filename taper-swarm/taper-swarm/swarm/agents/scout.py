from swarm.agents.base import BaseAgent
from swarm.config import AGENT_PROMPTS

class ScoutAgent(BaseAgent):
    def __init__(self):
        super().__init__("scout", AGENT_PROMPTS["scout"])
