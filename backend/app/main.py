from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.routers import auth, vault, threat, admin, health
from app.middleware.rate_limit import RateLimitMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="CITADEL Shield API", description="Zero-knowledge cybersecurity backend", version="1.0.0", lifespan=lifespan)
app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(vault.router)
app.include_router(threat.router)
app.include_router(admin.router)
app.include_router(health.router)

@app.get("/")
async def root():
    return {"message": "CITADEL Shield is active", "version": "1.0.0"}
