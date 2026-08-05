import uvicorn
from swarm.models import init_db
from swarm.queen import Queen

if __name__ == "__main__":
    init_db()
    queen = Queen()
    print(f"◈ Swarm initialized with {len(queen.get_pending_ideas())} ideas")
    print("◈ Dashboard: http://localhost:8000")
    print("◈ API docs: http://localhost:8000/docs")
    uvicorn.run("dashboard.app:app", host="0.0.0.0", port=8000, reload=True)
