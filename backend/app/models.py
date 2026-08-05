from sqlalchemy import Column, String, DateTime, LargeBinary, Integer, Boolean, JSON, Text, Float, ForeignKey, Index, UniqueConstraint, Enum
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    auth_hash = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    kdf_params = Column(JSON, default={"iterations": 600000, "algorithm": "pbkdf2+argon2id"})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

class VaultBlob(Base):
    __tablename__ = "vault_blobs"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    encrypted_data = Column(LargeBinary, nullable=False)
    nonce = Column(String(255), nullable=False)
    version = Column(Integer, default=1)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    checksum = Column(String(255), nullable=False)

class BreachRecord(Base):
    __tablename__ = "breach_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email_hash = Column(String(64), index=True)
    breach_name = Column(String(255))
    breached_date = Column(DateTime(timezone=True))
    data_classes = Column(JSON)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

class ThreatIOC(Base):
    __tablename__ = "threat_iocs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ioc_type = Column(String(50), index=True)
    value = Column(String(512), nullable=False, index=True)
    threat_score = Column(Integer, default=0)
    source = Column(String(100))
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())

# ============================================================
# Sentinel Secretary — AI executive assistant models
# ============================================================

class SecretaryAccount(Base):
    """Encrypted integration credentials and preferences per user."""
    __tablename__ = "secretary_accounts"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # Provider identifiers
    google_refresh_token = Column(Text, nullable=True)
    google_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    imap_host = Column(String(255), nullable=True)
    imap_port = Column(Integer, default=993)
    imap_username = Column(String(255), nullable=True)
    imap_password_encrypted = Column(Text, nullable=True)
    smtp_host = Column(String(255), nullable=True)
    smtp_port = Column(Integer, default=587)
    smtp_username = Column(String(255), nullable=True)
    smtp_password_encrypted = Column(Text, nullable=True)
    # AI / voice endpoints
    whisper_endpoint = Column(String(512), nullable=True)
    whisper_api_key_encrypted = Column(Text, nullable=True)
    local_llm_endpoint = Column(String(512), nullable=True, default="http://localhost:11434")
    remote_llm_provider = Column(String(50), nullable=True)  # openai, anthropic, google
    remote_llm_api_key_encrypted = Column(Text, nullable=True)
    remote_llm_model = Column(String(100), nullable=True)
    # User preferences
    briefing_time = Column(String(5), nullable=True, default="07:00")  # HH:MM
    timezone = Column(String(50), nullable=True, default="UTC")
    voice_enabled = Column(Boolean, default=True)
    remote_llm_fallback_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SecretaryContext(Base):
    """Long-term facts, contacts, preferences, and communication style."""
    __tablename__ = "secretary_context"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)
    category = Column(String(50), nullable=True, index=True)  # contact, preference, commitment, style
    confidence = Column(Integer, default=5)  # 1-10
    source = Column(String(100), nullable=True)  # voice, email, explicit, inferred
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    __table_args__ = (UniqueConstraint("user_id", "key", "category", name="uix_secretary_context_user_key_category"),)

class SecretaryTask(Base):
    """Tasks, reminders, and follow-ups extracted from voice, email, or calendar."""
    __tablename__ = "secretary_tasks"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, in_progress, done, snoozed, delegated
    priority = Column(Integer, default=0)  # 0-100, higher = more urgent
    due_at = Column(DateTime(timezone=True), nullable=True, index=True)
    snoozed_until = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(50), nullable=True)  # voice, email, calendar, explicit, briefing
    source_reference = Column(String(255), nullable=True)  # email thread id, calendar event id, transcript id
    related_contact = Column(String(255), nullable=True, index=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    __table_args__ = (Index("ix_secretary_tasks_user_due", "user_id", "due_at", "status"),)

class SecretaryBriefing(Base):
    """Generated daily briefings stored for retrieval and feedback."""
    __tablename__ = "secretary_briefings"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    for_date = Column(DateTime(timezone=True), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    sections = Column(JSON, nullable=False, default=dict)
    feedback_score = Column(Integer, nullable=True)  # 1-5
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (Index("ix_secretary_briefings_user_date", "user_id", "for_date", unique=True),)

class SecretaryConversation(Base):
    """Recent conversation turns for short-term memory and context windows."""
    __tablename__ = "secretary_conversations"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True)
    extracted_entities = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (Index("ix_secretary_conversations_user_created", "user_id", "created_at"),)

class SecretaryEmailDraft(Base):
    """Draft emails awaiting review/send."""
    __tablename__ = "secretary_email_drafts"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    thread_id = Column(String(255), nullable=True)
    provider = Column(String(20), nullable=True, default="gmail")  # gmail, imap
    to_address = Column(String(255), nullable=False)
    cc_address = Column(String(500), nullable=True)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="draft")  # draft, approved, sent, discarded
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    __table_args__ = (Index("ix_secretary_email_drafts_user_status", "user_id", "status"),)

class SecretaryCalendarEvent(Base):
    """Cache/mirror of calendar events for conflict detection and briefing."""
    __tablename__ = "secretary_calendar_events"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(20), nullable=False, default="google")  # google, caldav
    external_event_id = Column(String(255), nullable=False, index=True)
    summary = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    start_at = Column(DateTime(timezone=True), nullable=False, index=True)
    end_at = Column(DateTime(timezone=True), nullable=False)
    attendees = Column(JSON, nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(255), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("user_id", "provider", "external_event_id", name="uix_secretary_calendar_event_external"),)

class SecretaryLog(Base):
    """Audit log of every integration call, action, and fallback."""
    __tablename__ = "secretary_logs"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    provider = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False)  # success, error, fallback
    details = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (Index("ix_secretary_logs_user_created", "user_id", "created_at"),)
