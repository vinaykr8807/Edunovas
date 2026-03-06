import os
from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey, ARRAY, Integer, Float, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="student")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    profile = relationship("StudentProfileModel", back_populates="user", uselist=False)
    chats = relationship("ChatMessageModel", back_populates="user")
    stats = relationship("DomainStats", back_populates="user")
    progress = relationship("UserProgress", back_populates="user", uselist=False)
    achievements = relationship("Achievement", back_populates="user")
    quizzes = relationship("QuizHistory", back_populates="user")
    interviews = relationship("InterviewHistory", back_populates="user")
    coding_errors = relationship("CodingError", back_populates="user")

class StudentProfileModel(Base):
    __tablename__ = "student_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    degree = Column(String)
    branch = Column(String)
    academic_year = Column(String)
    domain = Column(String)
    skills = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")

class ChatMessageModel(Base):
    __tablename__ = "chat_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    role = Column(String)
    content = Column(Text)
    mode = Column(String)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="chats")

class DomainStats(Base):
    __tablename__ = "domain_stats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    domain = Column(String)
    interaction_count = Column(Integer, default=1)
    last_active = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (UniqueConstraint('user_id', 'domain', name='_user_domain_uc'),)
    
    user = relationship("User", back_populates="stats")

class UserProgress(Base):
    __tablename__ = "user_progress"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_active = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    badges = Column(ARRAY(String), default=[])
    career_phase = Column(String, default="Foundational")
    
    user = relationship("User", back_populates="progress")

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String)
    description = Column(String)
    date_earned = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="achievements")

class QuizHistory(Base):
    __tablename__ = "quiz_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    topic = Column(String)
    score = Column(Integer)
    weak_areas = Column(ARRAY(String))
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="quizzes")

class InterviewHistory(Base):
    __tablename__ = "interview_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    role = Column(String)
    score = Column(Integer)
    weak_topics = Column(ARRAY(String))
    feedback = Column(Text)
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="interviews")

class CodingError(Base):
    __tablename__ = "coding_errors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    language = Column(String)
    mistake_type = Column(String)
    frequency = Column(Integer, default=1)
    
    user = relationship("User", back_populates="coding_errors")

class ProgressTracking(Base):
    __tablename__ = "progress_tracking"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    topic = Column(String)
    confidence_score = Column(Float)
    last_practiced = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    times_attempted = Column(Integer, default=1)
    
    __table_args__ = (UniqueConstraint('user_id', 'topic', name='_user_topic_uc'),)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
