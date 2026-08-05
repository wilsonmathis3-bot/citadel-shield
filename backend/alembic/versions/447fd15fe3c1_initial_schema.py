"""Initial CITADEL + Sentinel Secretary schema

Revision ID: 447fd15fe3c1
Revises: 
Create Date: 2026-08-05 10:32:13.707000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '447fd15fe3c1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('auth_hash', sa.String(length=255), nullable=False),
        sa.Column('salt', sa.String(length=255), nullable=False),
        sa.Column('kdf_params', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    # vault_blobs
    op.create_table(
        'vault_blobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('encrypted_data', sa.LargeBinary(), nullable=False),
        sa.Column('nonce', sa.String(length=255), nullable=False),
        sa.Column('version', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('checksum', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vault_blobs_user_id'), 'vault_blobs', ['user_id'], unique=False)

    # breach_records
    op.create_table(
        'breach_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email_hash', sa.String(length=64), nullable=True),
        sa.Column('breach_name', sa.String(length=255), nullable=True),
        sa.Column('breached_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_classes', sa.JSON(), nullable=True),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_breach_records_email_hash'), 'breach_records', ['email_hash'], unique=False)

    # threat_iocs
    op.create_table(
        'threat_iocs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ioc_type', sa.String(length=50), nullable=True),
        sa.Column('value', sa.String(length=512), nullable=False),
        sa.Column('threat_score', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('first_seen', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_seen', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_threat_iocs_ioc_type'), 'threat_iocs', ['ioc_type'], unique=False)
    op.create_index(op.f('ix_threat_iocs_value'), 'threat_iocs', ['value'], unique=False)

    # secretary_accounts
    op.create_table(
        'secretary_accounts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('google_refresh_token', sa.Text(), nullable=True),
        sa.Column('google_token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('imap_host', sa.String(length=255), nullable=True),
        sa.Column('imap_port', sa.Integer(), nullable=True),
        sa.Column('imap_username', sa.String(length=255), nullable=True),
        sa.Column('imap_password_encrypted', sa.Text(), nullable=True),
        sa.Column('smtp_host', sa.String(length=255), nullable=True),
        sa.Column('smtp_port', sa.Integer(), nullable=True),
        sa.Column('smtp_username', sa.String(length=255), nullable=True),
        sa.Column('smtp_password_encrypted', sa.Text(), nullable=True),
        sa.Column('whisper_endpoint', sa.String(length=512), nullable=True),
        sa.Column('whisper_api_key_encrypted', sa.Text(), nullable=True),
        sa.Column('local_llm_endpoint', sa.String(length=512), nullable=True),
        sa.Column('remote_llm_provider', sa.String(length=50), nullable=True),
        sa.Column('remote_llm_api_key_encrypted', sa.Text(), nullable=True),
        sa.Column('remote_llm_model', sa.String(length=100), nullable=True),
        sa.Column('briefing_time', sa.String(length=5), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('voice_enabled', sa.Boolean(), nullable=True),
        sa.Column('remote_llm_fallback_enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_secretary_accounts_user_id'), 'secretary_accounts', ['user_id'], unique=False)

    # secretary_context
    op.create_table(
        'secretary_context',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('confidence', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'key', 'category', name='uix_secretary_context_user_key_category')
    )
    op.create_index(op.f('ix_secretary_context_category'), 'secretary_context', ['category'], unique=False)
    op.create_index(op.f('ix_secretary_context_key'), 'secretary_context', ['key'], unique=False)
    op.create_index(op.f('ix_secretary_context_user_id'), 'secretary_context', ['user_id'], unique=False)

    # secretary_tasks
    op.create_table(
        'secretary_tasks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('snoozed_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('source_reference', sa.String(length=255), nullable=True),
        sa.Column('related_contact', sa.String(length=255), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_secretary_tasks_related_contact'), 'secretary_tasks', ['related_contact'], unique=False)
    op.create_index(op.f('ix_secretary_tasks_user_due'), 'secretary_tasks', ['user_id', 'due_at', 'status'], unique=False)
    op.create_index(op.f('ix_secretary_tasks_user_id'), 'secretary_tasks', ['user_id'], unique=False)

    # secretary_briefings
    op.create_table(
        'secretary_briefings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('for_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('sections', sa.JSON(), nullable=False),
        sa.Column('feedback_score', sa.Integer(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_secretary_briefings_user_date'), 'secretary_briefings', ['user_id', 'for_date'], unique=True)
    op.create_index(op.f('ix_secretary_briefings_user_id'), 'secretary_briefings', ['user_id'], unique=False)

    # secretary_conversations
    op.create_table(
        'secretary_conversations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(length=50), nullable=True),
        sa.Column('extracted_entities', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_secretary_conversations_user_created'), 'secretary_conversations', ['user_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_secretary_conversations_user_id'), 'secretary_conversations', ['user_id'], unique=False)

    # secretary_email_drafts
    op.create_table(
        'secretary_email_drafts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('thread_id', sa.String(length=255), nullable=True),
        sa.Column('provider', sa.String(length=20), nullable=True),
        sa.Column('to_address', sa.String(length=255), nullable=False),
        sa.Column('cc_address', sa.String(length=500), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_secretary_email_drafts_user_id'), 'secretary_email_drafts', ['user_id'], unique=False)
    op.create_index(op.f('ix_secretary_email_drafts_user_status'), 'secretary_email_drafts', ['user_id', 'status'], unique=False)

    # secretary_calendar_events
    op.create_table(
        'secretary_calendar_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('provider', sa.String(length=20), nullable=False),
        sa.Column('external_event_id', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=500), nullable=True),
        sa.Column('start_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('attendees', sa.JSON(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=True),
        sa.Column('recurrence_rule', sa.String(length=255), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'provider', 'external_event_id', name='uix_secretary_calendar_event_external')
    )
    op.create_index(op.f('ix_secretary_calendar_events_external_event_id'), 'secretary_calendar_events', ['external_event_id'], unique=False)
    op.create_index(op.f('ix_secretary_calendar_events_start_at'), 'secretary_calendar_events', ['start_at'], unique=False)
    op.create_index(op.f('ix_secretary_calendar_events_user_id'), 'secretary_calendar_events', ['user_id'], unique=False)

    # secretary_logs
    op.create_table(
        'secretary_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_secretary_logs_action'), 'secretary_logs', ['action'], unique=False)
    op.create_index(op.f('ix_secretary_logs_user_created'), 'secretary_logs', ['user_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_secretary_logs_user_id'), 'secretary_logs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('secretary_logs')
    op.drop_table('secretary_calendar_events')
    op.drop_table('secretary_email_drafts')
    op.drop_table('secretary_conversations')
    op.drop_table('secretary_briefings')
    op.drop_table('secretary_tasks')
    op.drop_table('secretary_context')
    op.drop_table('secretary_accounts')
    op.drop_table('threat_iocs')
    op.drop_table('breach_records')
    op.drop_table('vault_blobs')
    op.drop_table('users')
