"""
Database configuration and session management for the Resume Website.

Uses SQLAlchemy with SQLite for persistent storage of user-managed
projects, technologies, bullet points, and tags.
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    Column,
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


# Association table for project-tag many-to-many
class ProjectTag(Base):
    __tablename__ = "project_tags"

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    project = relationship("ProjectDB", back_populates="project_tags")
    tag = relationship("TagDB", back_populates="project_tags")


class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    personal_title = Column(String(255), nullable=True)
    start_month = Column(Integer, nullable=False)
    start_year = Column(Integer, nullable=False)
    end_month = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    technologies = relationship(
        "TechItemDB",
        back_populates="project",
        cascade="all, delete-orphan",
        primaryjoin="and_(ProjectDB.id == TechItemDB.project_id, TechItemDB.category == 'technology')",
        viewonly=True,
    )
    frameworks = relationship(
        "TechItemDB",
        back_populates="project",
        cascade="all, delete-orphan",
        primaryjoin="and_(ProjectDB.id == TechItemDB.project_id, TechItemDB.category == 'framework')",
        viewonly=True,
    )
    languages = relationship(
        "TechItemDB",
        back_populates="project",
        cascade="all, delete-orphan",
        primaryjoin="and_(ProjectDB.id == TechItemDB.project_id, TechItemDB.category == 'language')",
        viewonly=True,
    )
    all_tech_items = relationship(
        "TechItemDB",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    bullet_points = relationship(
        "BulletPointDB",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="BulletPointDB.order",
    )
    project_tags = relationship(
        "ProjectTag", back_populates="project", cascade="all, delete-orphan"
    )


class TechItemDB(Base):
    __tablename__ = "tech_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # 'technology', 'framework', or 'language'
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))

    project = relationship("ProjectDB", back_populates="all_tech_items")


class BulletPointDB(Base):
    __tablename__ = "bullet_points"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    order = Column(Integer, default=0)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))

    project = relationship("ProjectDB", back_populates="bullet_points")


class TagDB(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    project_tags = relationship("ProjectTag", back_populates="tag")


class SectionOrderDB(Base):
    """Stores the display order of resume sections as a comma-separated list."""

    __tablename__ = "section_order"

    id = Column(Integer, primary_key=True, index=True, default=1)
    section_order = Column(Text, nullable=False, default="")


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
