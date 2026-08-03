import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models import ThreatIOC

async def seed_threats():
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(ThreatIOC).limit(1))
        if result.scalar_one_or_none():
            print("Threat IOCs already seeded.")
            return
        initial_threats = [
            ThreatIOC(ioc_type="domain", value="evil-site.com", threat_score=100, source="citadel_seed"),
            ThreatIOC(ioc_type="domain", value="phishing-bank.net", threat_score=100, source="citadel_seed"),
            ThreatIOC(ioc_type="domain", value="malware-dl.xyz", threat_score=100, source="citadel_seed"),
            ThreatIOC(ioc_type="domain", value="fake-login.com", threat_score=95, source="citadel_seed"),
            ThreatIOC(ioc_type="domain", value="virus-update.org", threat_score=90, source="citadel_seed"),
            ThreatIOC(ioc_type="url", value="http://evil-site.com/login", threat_score=100, source="citadel_seed"),
            ThreatIOC(ioc_type="ip", value="192.168.1.100", threat_score=80, source="citadel_seed"),
        ]
        session.add_all(initial_threats)
        await session.commit()
        print(f"Seeded {len(initial_threats)} threat IOCs.")

if __name__ == "__main__":
    asyncio.run(seed_threats())
