"""
Database configuration and session management for the Resume Website.

Uses SQLAlchemy with SQLite for persistent storage of resume data
organized into normalized tables: Person, Education, Projects, Experiences.
"""

import json
import os
from datetime import date, datetime

from dotenv import load_dotenv
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

load_dotenv()

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./resume.db")

engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# ── Person ─────────────────────────────────────────────────────────────────────

class PersonDB(Base):
    __tablename__ = "person"

    person_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)

    education = relationship("EducationDB", back_populates="person", cascade="all, delete-orphan")
    projects = relationship("ProjectDB", back_populates="person", cascade="all, delete-orphan")
    experiences = relationship("ExperienceDB", back_populates="person", cascade="all, delete-orphan")


# ── Education ──────────────────────────────────────────────────────────────────

class EducationDB(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey("person.person_id", ondelete="CASCADE"), nullable=False)
    school = Column(String(255), nullable=False)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    degree = Column(String(255), nullable=True)
    degree_minor = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    relevant_courses = Column(Text, nullable=True)  # comma-separated

    person = relationship("PersonDB", back_populates="education")


# ── Projects ───────────────────────────────────────────────────────────────────

class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey("person.person_id", ondelete="CASCADE"), nullable=False)
    project_name = Column(String(255), nullable=False)
    project_role = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    bullet_points = Column(Text, nullable=True)  # JSON array of strings
    frameworks = Column(Text, nullable=True)     # JSON array of strings
    languages = Column(Text, nullable=True)      # JSON array of strings
    technologies = Column(Text, nullable=True)   # JSON array of strings

    person = relationship("PersonDB", back_populates="projects")


# ── Experiences ────────────────────────────────────────────────────────────────

class ExperienceDB(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey("person.person_id", ondelete="CASCADE"), nullable=False)
    company = Column(String(255), nullable=False)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    role = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    bullet_points = Column(Text, nullable=True)  # JSON array of strings

    person = relationship("PersonDB", back_populates="experiences")


# ── Section Order ──────────────────────────────────────────────────────────────

class SectionOrderDB(Base):
    """Stores the display order of resume sections as a comma-separated list."""

    __tablename__ = "section_order"

    id = Column(Integer, primary_key=True, index=True, default=1)
    section_order = Column(Text, nullable=False, default="")


# ── Helpers ────────────────────────────────────────────────────────────────────

def json_list(value):
    """Serialize a list to JSON string for storage, or return empty array string."""
    if not value:
        return "[]"
    return json.dumps(value)


def parse_json_list(value):
    """Parse a JSON string back to a list."""
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
