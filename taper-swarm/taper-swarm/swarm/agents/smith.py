from swarm.agents.base import BaseAgent
from swarm.config import AGENT_PROMPTS

class SmithAgent(BaseAgent):
    def __init__(self):
        super().__init__("smith", AGENT_PROMPTS["smith"])
