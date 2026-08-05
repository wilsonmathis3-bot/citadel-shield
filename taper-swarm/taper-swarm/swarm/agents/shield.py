from swarm.agents.base import BaseAgent
from swarm.config import AGENT_PROMPTS

class ShieldAgent(BaseAgent):
    def __init__(self):
        super().__init__("shield", AGENT_PROMPTS["shield"])
