from swarm.agents.base import BaseAgent
from swarm.config import AGENT_PROMPTS

class BuilderAgent(BaseAgent):
    def __init__(self):
        super().__init__("builder", AGENT_PROMPTS["builder"])
