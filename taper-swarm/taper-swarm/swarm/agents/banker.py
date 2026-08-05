from swarm.agents.base import BaseAgent
from swarm.config import AGENT_PROMPTS

class BankerAgent(BaseAgent):
    def __init__(self):
        super().__init__("banker", AGENT_PROMPTS["banker"])
