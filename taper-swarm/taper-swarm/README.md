# Taper Swarm

Multi-agent idea validation system. Runs on Linux laptop, deploys to $5 VPS, controlled from Android phone.

## Quick Start

```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run dashboard
python main.py
# Open http://localhost:8000

# 3. Run swarm analysis (in another terminal)
python -c "
from swarm.queen import Queen
from tasks import queue_task

q = Queen()
for idea in q.get_pending_ideas():
    for agent in ['scout','smith','shield','banker','growth','critic','builder']:
        queue_task(idea['id'], agent)
        print(f'Queued {agent} for {idea["name"]}')
"

# 4. Run worker (processes queue)
python tasks.py
```

## Environment Variables

- `SWARM_MOCK=true` (default) - Uses built-in mock responses. No API key needed.
- `SWARM_MOCK=false` - Uses real LLM API. Set `SWARM_API_KEY` and `SWARM_API_URL`.
- `SWARM_API_KEY` - OpenAI/compatible API key
- `SWARM_API_URL` - API endpoint (default: https://api.openai.com/v1/chat/completions)
- `SWARM_MODEL` - Model name (default: gpt-4o-mini)

## Architecture

- **Queen** - Orchestrator, manages ideas and scores
- **Scout** - Market research agent
- **Smith** - Technical feasibility agent
- **Shield** - Legal/compliance agent
- **Banker** - Monetization agent
- **Growth** - Customer acquisition agent
- **Critic** - Red-team skeptic (highest weight in scoring)
- **Builder** - Code generation / MVP architect

## Scoring

Final score = weighted average of agent verdicts (0-10 scale):
- Critic: 30%
- Banker: 25%
- Scout: 20%
- Smith: 15%
- Shield: 5%
- Growth: 5%

## Deployment

```bash
# VPS (Ubuntu)
sudo apt install python3-pip nginx
pip install -r requirements.txt
# Use gunicorn + nginx (see previous instructions)
```

## Android Admin

Access the dashboard from any mobile browser. The UI is mobile-first.
For SSH admin: use Termux app.
