"""unified railway schema

Revision ID: b462c5b5e503
Revises: 447fd15fe3c1
Create Date: 2026-08-05 05:11:57.712860

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import os

revision: str = 'b462c5b5e503'
down_revision: Union[str, None] = '447fd15fe3c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_WORKSPACE_ID = '00000000-0000-0000-0000-000000000000'
DEFAULT_USER_ID = '11111111-1111-1111-1111-111111111111'


def _load_sql_file(filename: str) -> str:
    """Load a sibling .sql file as a string."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def _split_sql(sql: str):
    """Yield semicolon-separated statements, skipping pure comment blocks."""
    for raw in sql.split(';'):
        stmt = raw.strip()
        if not stmt:
            continue
        # Skip blocks that are only SQL comments.
        if not any(
            line.strip() and not line.strip().startswith('--')
            for line in stmt.splitlines()
        ):
            continue
        yield stmt


def upgrade() -> None:
    # Preserve legacy tables that collide with the new schema.
    op.execute(sa.text("ALTER TABLE IF EXISTS users RENAME TO legacy_users"))
    op.execute(sa.text("ALTER TABLE IF EXISTS threat_iocs RENAME TO legacy_threat_iocs"))
    # Some Railway databases may already have an unrelated 'projects' table.
    op.execute(sa.text("ALTER TABLE IF EXISTS projects RENAME TO legacy_projects"))

    # PostgreSQL extensions required by the schema.
    conn = op.get_bind()
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
    postgis_available = conn.execute(
        sa.text("SELECT 1 FROM pg_available_extensions WHERE name = 'postgis'")
    ).scalar() is not None
    if postgis_available:
        op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS postgis"))

    # Create the unified schema (extensions, tables, indexes, RLS, comments, seed projects).
    sql = _load_sql_file("b462c5b5e503_unified_railway_schema.sql")
    if not postgis_available:
        # Railway Postgres should have PostGIS; if it doesn't, fall back to a
        # native POINT type so the migration can still run.
        sql = sql.replace("GEOGRAPHY(POINT,4326)", "POINT")
    for stmt in _split_sql(sql):
        op.execute(sa.text(stmt))

    # Insert a default workspace and admin user so foreign-key requirements are satisfied.
    op.execute(sa.text(f"""
        INSERT INTO workspaces (id, name, slug, owner_id, plan_tier, settings)
        VALUES ('{DEFAULT_WORKSPACE_ID}', 'Default Workspace', 'default', '{DEFAULT_USER_ID}', 'free', '{{}}')
        ON CONFLICT (id) DO NOTHING
    """))
    op.execute(sa.text(f"""
        INSERT INTO users (id, workspace_id, email, password_hash, role, profile, mfa_enabled)
        VALUES ('{DEFAULT_USER_ID}', '{DEFAULT_WORKSPACE_ID}', 'admin@boscs.local', NULL, 'superadmin', '{{}}', FALSE)
        ON CONFLICT (id) DO NOTHING
    """))
    # Tie the default workspace owner to the default user now that the user exists.
    op.execute(sa.text(f"""
        UPDATE workspaces SET owner_id = '{DEFAULT_USER_ID}' WHERE id = '{DEFAULT_WORKSPACE_ID}'
    """))


def downgrade() -> None:
    # Drop all new unified tables in reverse dependency order.
    tables = [
        "event_log",
        "transactions",
        "bookings",
        "pitch_decks",
        "licenses",
        "products",
        "elk_configs",
        "procedure_revisions",
        "procedures",
        "em_rail_tests",
        "sensor_readings",
        "sensors",
        "audio_playlists",
        "midi_mappings",
        "midi_devices",
        "scraped_data",
        "scrape_jobs",
        "privacy_policies",
        "threat_iocs",
        "vault_items",
        "vaults",
        "parts_catalog",
        "trip_signatures",
        "obd_readings",
        "vehicles",
        "outreach_logs",
        "outreach_sequences",
        "contacts",
        "agent_runs",
        "ai_agents",
        "ai_memories",
        "ai_sessions",
        "projects",
        "api_keys",
        "users",
        "workspaces",
    ]
    for table in tables:
        op.execute(sa.text(f"DROP TABLE IF EXISTS {table} CASCADE"))

    # Restore legacy table names.
    op.execute(sa.text("ALTER TABLE IF EXISTS legacy_users RENAME TO users"))
    op.execute(sa.text("ALTER TABLE IF EXISTS legacy_threat_iocs RENAME TO threat_iocs"))
    op.execute(sa.text("ALTER TABLE IF EXISTS legacy_projects RENAME TO projects"))
