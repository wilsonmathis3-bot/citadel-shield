"""Task queue and worker for the swarm."""
import sqlite3
import time
from datetime import datetime
from swarm.models import DB_PATH, init_db
from swarm.agents import ScoutAgent, SmithAgent, ShieldAgent, BankerAgent, GrowthAgent, CriticAgent, BuilderAgent

AGENTS = {
    "scout": ScoutAgent(),
    "smith": SmithAgent(),
    "shield": ShieldAgent(),
    "banker": BankerAgent(),
    "growth": GrowthAgent(),
    "critic": CriticAgent(),
    "builder": BuilderAgent(),
}


def queue_task(idea_id, agent_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO tasks (idea_id, agent_name, task_type, status) VALUES (?, ?, 'analysis', 'queued')",
        (idea_id, agent_name)
    )
    conn.commit()
    conn.close()


def get_pending_tasks():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM tasks WHERE status = 'queued' ORDER BY created_at LIMIT 10"
    )
    tasks = [dict(row) for row in c.fetchall()]
    conn.close()
    return tasks


def update_task_status(task_id, status, result=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if result:
        c.execute(
            "UPDATE tasks SET status = ?, result = ?, completed_at = ? WHERE id = ?",
            (status, result, datetime.now().isoformat(), task_id)
        )
    else:
        c.execute(
            "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
            (status, datetime.now().isoformat(), task_id)
        )
    conn.commit()
    conn.close()


def process_task(task):
    agent_name = task["agent_name"]
    idea_id = task["idea_id"]

    # Get idea details
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        update_task_status(task["id"], "failed", "Idea not found")
        return

    idea = dict(row)

    if agent_name not in AGENTS:
        update_task_status(task["id"], "failed", f"Unknown agent: {agent_name}")
        return

    try:
        agent = AGENTS[agent_name]
        report = agent.analyze(idea)
        update_task_status(task["id"], "completed", f"Report saved: {report.verdict} (confidence: {report.confidence})")
    except Exception as e:
        update_task_status(task["id"], "failed", str(e))


def run_worker(cycles=1, sleep_seconds=2):
    """Run the task worker. Set cycles=-1 for infinite loop."""
    init_db()
    cycle = 0
    while True:
        if cycles != -1 and cycle >= cycles:
            break
        tasks = get_pending_tasks()
        if not tasks:
            if cycles == 1:
                break
            time.sleep(sleep_seconds)
            cycle += 1
            continue

        for task in tasks:
            print(f"[Worker] Processing task {task['id']}: {task['agent_name']} on idea {task['idea_id']}")
            process_task(task)

        cycle += 1
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    run_worker(cycles=-1, sleep_seconds=2)
