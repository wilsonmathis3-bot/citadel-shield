"""Queen orchestrator - coordinates the swarm."""
import sqlite3
from datetime import datetime
from swarm.models import DB_PATH, Idea, init_db
from swarm.config import SEED_IDEAS

class Queen:
    def __init__(self):
        init_db()
        self._seed_ideas()

    def _seed_ideas(self):
        for idea_data in SEED_IDEAS:
            idea = Idea(**idea_data)
            idea.save()

    def get_pending_ideas(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM ideas WHERE status = 'pending'")
        ideas = [dict(row) for row in c.fetchall()]
        conn.close()
        return ideas

    def get_idea_by_id(self, idea_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def queue_analysis(self, idea_id, agent_name):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO tasks (idea_id, agent_name, task_type, status) VALUES (?, ?, 'analysis', 'queued')",
            (idea_id, agent_name)
        )
        conn.commit()
        conn.close()

    def get_all_reports(self, idea_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT * FROM agent_reports WHERE idea_id = ? ORDER BY created_at DESC",
            (idea_id,)
        )
        reports = [dict(row) for row in c.fetchall()]
        conn.close()
        return reports

    def get_swarm_status(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("SELECT COUNT(*) as total FROM ideas")
        total = c.fetchone()[0]

        c.execute("SELECT COUNT(*) as pending FROM ideas WHERE status = 'pending'")
        pending = c.fetchone()[0]

        c.execute("SELECT COUNT(*) as completed FROM tasks WHERE status = 'completed'")
        completed = c.fetchone()[0]

        c.execute("SELECT COUNT(*) as queued FROM tasks WHERE status = 'queued'")
        queued = c.fetchone()[0]

        c.execute("""
            SELECT ideas.name, COUNT(agent_reports.id) as report_count
            FROM ideas
            LEFT JOIN agent_reports ON ideas.id = agent_reports.idea_id
            GROUP BY ideas.id
            ORDER BY report_count DESC
        """)
        idea_coverage = [dict(row) for row in c.fetchall()]

        conn.close()

        return {
            "total_ideas": total,
            "pending_ideas": pending,
            "completed_tasks": completed,
            "queued_tasks": queued,
            "idea_coverage": idea_coverage
        }

    def calculate_final_score(self, idea_id):
        """Calculate weighted score across all agent reports."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute("""
            SELECT agent_name, verdict, confidence 
            FROM agent_reports 
            WHERE idea_id = ? 
            ORDER BY created_at DESC
        """, (idea_id,))

        reports = c.fetchall()
        conn.close()

        if not reports:
            return 0

        # Keep only latest report per agent
        latest = {}
        for r in reports:
            if r['agent_name'] not in latest:
                latest[r['agent_name']] = r

        score = 0
        weights = {
            'critic': 0.30,
            'banker': 0.25,
            'scout': 0.20,
            'smith': 0.15,
            'shield': 0.05,
            'growth': 0.05
        }

        for agent, report in latest.items():
            weight = weights.get(agent, 0.1)
            verdict_mult = 1.0 if report['verdict'] == 'GO' else (0.5 if report['verdict'] == 'CONDITIONAL' else 0)
            score += report['confidence'] * weight * verdict_mult

        # Update idea score
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE ideas SET final_score = ? WHERE id = ?", (round(score, 2), idea_id))
        conn.commit()
        conn.close()

        return round(score, 2)

    def get_leaderboard(self):
        """Return ideas ranked by final score."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT id, name, human_need, final_score, status 
            FROM ideas 
            ORDER BY final_score DESC, name ASC
        """)
        results = [dict(row) for row in c.fetchall()]
        conn.close()
        return results
