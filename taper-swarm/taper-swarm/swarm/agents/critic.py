from swarm.agents.base import BaseAgent
from swarm.config import AGENT_PROMPTS

class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__("critic", AGENT_PROMPTS["critic"])
