# dashboard/app.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import sqlite3
import json
from swarm.queen import Queen

app = FastAPI(title="Swarm Command Center")
queen = Queen()

# Mobile-first dashboard HTML
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Swarm Command</title>
    <style>
        :root { --bg: #0a0a0a; --card: #151515; --accent: #00ff88; --warn: #ffaa00; --danger: #ff4444; --text: #e0e0e0; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: var(--bg); color: var(--text); font-family: 'Courier New', monospace; padding: 10px; }
        .header { text-align: center; padding: 20px; border-bottom: 1px solid #333; margin-bottom: 20px; }
        .header h1 { color: var(--accent); font-size: 1.5em; letter-spacing: 2px; }
        .status-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
        .status-card { background: var(--card); padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid var(--accent); }
        .status-card h3 { font-size: 0.8em; color: #888; margin-bottom: 5px; }
        .status-card .value { font-size: 1.8em; color: var(--accent); font-weight: bold; }
        .section { margin-bottom: 25px; }
        .section h2 { color: var(--accent); font-size: 1.1em; margin-bottom: 10px; padding-left: 10px; border-left: 3px solid var(--accent); }
        .idea-card { background: var(--card); padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid var(--warn); }
        .idea-card.score-high { border-left-color: var(--accent); }
        .idea-card.score-low { border-left-color: var(--danger); }
        .idea-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .idea-name { font-weight: bold; font-size: 1.1em; }
        .score { font-size: 1.2em; font-weight: bold; }
        .score-high .score { color: var(--accent); }
        .score-mid .score { color: var(--warn); }
        .score-low .score { color: var(--danger); }
        .need-tag { font-size: 0.75em; color: #888; margin-top: 5px; }
        .btn { background: #222; color: var(--accent); border: 1px solid var(--accent); padding: 8px 15px; border-radius: 4px; cursor: pointer; font-family: inherit; font-size: 0.9em; margin-top: 10px; }
        .btn:active { background: var(--accent); color: var(--bg); }
        .report-list { margin-top: 10px; font-size: 0.85em; }
        .report-item { padding: 5px 0; border-bottom: 1px solid #222; }
        .verdict-go { color: var(--accent); }
        .verdict-no { color: var(--danger); }
        .verdict-cond { color: var(--warn); }
        .loading { text-align: center; color: var(--warn); padding: 20px; }
        @media (min-width: 768px) {
            body { max-width: 800px; margin: 0 auto; }
            .status-grid { grid-template-columns: 1fr 1fr 1fr 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>◈ SWARM COMMAND ◈</h1>
        <p style="font-size:0.8em; color:#666;">Multi-Agent Idea Validation System</p>
    </div>

    <div class="status-grid" id="status">
        <div class="status-card"><h3>IDEAS</h3><div class="value" id="total-ideas">-</div></div>
        <div class="status-card"><h3>PENDING</h3><div class="value" id="pending-ideas">-</div></div>
        <div class="status-card"><h3>ANALYZED</h3><div class="value" id="completed">-</div></div>
        <div class="status-card"><h3>QUEUE</h3><div class="value" id="queued">-</div></div>
    </div>

    <div class="section">
        <h2>LEADERBOARD</h2>
        <div id="leaderboard" class="loading">Loading swarm intelligence...</div>
    </div>

    <script>
        async function loadStatus() {
            const res = await fetch('/api/status');
            const data = await res.json();
            document.getElementById('total-ideas').textContent = data.total_ideas;
            document.getElementById('pending-ideas').textContent = data.pending_ideas;
            document.getElementById('completed').textContent = data.completed_tasks;
            document.getElementById('queued').textContent = data.queued_tasks;
        }

        async function loadLeaderboard() {
            const res = await fetch('/api/leaderboard');
            const ideas = await res.json();
            const container = document.getElementById('leaderboard');

            if (ideas.length === 0) {
                container.innerHTML = '<p>No ideas analyzed yet. Run the swarm.</p>';
                return;
            }

            container.innerHTML = ideas.map(idea => {
                const scoreClass = idea.final_score >= 6 ? 'score-high' : (idea.final_score >= 3 ? 'score-mid' : 'score-low');
                return `
                    <div class="idea-card ${scoreClass}">
                        <div class="idea-header">
                            <span class="idea-name">${idea.name}</span>
                            <span class="score">${idea.final_score.toFixed(1)}</span>
                        </div>
                        <div class="need-tag">${idea.human_need}</div>
                        <button class="btn" onclick="loadReports(${idea.id})">View Reports</button>
                        <div id="reports-${idea.id}" class="report-list"></div>
                    </div>
                `;
            }).join('');
        }

        async function loadReports(ideaId) {
            const container = document.getElementById('reports-' + ideaId);
            if (container.innerHTML && !container.innerHTML.includes('loading')) {
                container.innerHTML = '';
                return;
            }
            container.innerHTML = '<div class="loading">Loading agent reports...</div>';
            const res = await fetch('/api/ideas/' + ideaId + '/reports');
            const reports = await res.json();

            if (reports.length === 0) {
                container.innerHTML = '<div style="color:#666; padding:10px;">No reports yet. Queue analysis.</div>';
                return;
            }

            container.innerHTML = reports.map(r => {
                const vClass = r.verdict === 'GO' ? 'verdict-go' : (r.verdict === 'NO-GO' ? 'verdict-no' : 'verdict-cond');
                return `
                    <div class="report-item">
                        <strong>${r.agent_name}</strong>
                        <span class="${vClass}">[${r.verdict}]</span>
                        (confidence: ${r.confidence}/10)
                        <div style="color:#888; margin-top:3px;">${r.findings.substring(0, 120)}...</div>
                    </div>
                `;
            }).join('');
        }

        loadStatus();
        loadLeaderboard();
        setInterval(loadStatus, 30000);
        setInterval(loadLeaderboard, 30000);
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD_HTML


@app.get("/api/status")
def status():
    return queen.get_swarm_status()


@app.get("/api/leaderboard")
def leaderboard():
    return queen.get_leaderboard()


@app.get("/api/ideas/{idea_id}/reports")
def idea_reports(idea_id: int):
    reports = queen.get_all_reports(idea_id)
    return reports


@app.post("/api/ideas/{idea_id}/analyze")
def trigger_analysis(idea_id: int):
    idea = queen.get_idea_by_id(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    agents = ['scout', 'smith', 'shield', 'banker', 'growth', 'critic']
    for agent in agents:
        queen.queue_analysis(idea_id, agent)

    return {"status": "queued", "agents": agents, "idea": idea["name"]}
