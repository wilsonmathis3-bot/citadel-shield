from swarm.agents.base import BaseAgent
from swarm.config import AGENT_PROMPTS

class GrowthAgent(BaseAgent):
    def __init__(self):
        super().__init__("growth", AGENT_PROMPTS["growth"])
