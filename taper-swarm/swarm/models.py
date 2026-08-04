# swarm/models.py
import sqlite3
from datetime import datetime
from dataclasses import dataclass, asdict
import json

DB_PATH = "swarm_memory.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS ideas (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        description TEXT,
        human_need TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        final_score REAL DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS agent_reports (
        id INTEGER PRIMARY KEY,
        idea_id INTEGER,
        agent_name TEXT,
        verdict TEXT,
        confidence INTEGER,
        findings TEXT,
        risks TEXT,
        action_items TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (idea_id) REFERENCES ideas(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        idea_id INTEGER,
        agent_name TEXT,
        task_type TEXT,
        status TEXT DEFAULT 'queued',
        result TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (idea_id) REFERENCES ideas(id)
    )''')

    conn.commit()
    conn.close()


@dataclass
class Idea:
    name: str
    description: str
    human_need: str
    status: str = "pending"
    id: int = None

    def save(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO ideas (id, name, description, human_need, status)
                     VALUES ((SELECT id FROM ideas WHERE name=?), ?, ?, ?, ?)''',
                  (self.name, self.name, self.description, self.human_need, self.status))
        conn.commit()
        conn.close()


@dataclass
class AgentReport:
    idea_id: int
    agent_name: str
    verdict: str  # "GO", "NO-GO", "CONDITIONAL"
    confidence: int  # 1-10
    findings: str
    risks: str
    action_items: str

    def save(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO agent_reports
                     (idea_id, agent_name, verdict, confidence, findings, risks, action_items)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (self.idea_id, self.agent_name, self.verdict, self.confidence,
                   self.findings, self.risks, self.action_items))
        conn.commit()
        conn.close()
