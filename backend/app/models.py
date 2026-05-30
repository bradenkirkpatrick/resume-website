"""
Data models for the Resume Website application.

These Pydantic models define the structure of resume data
serialized to/from the API.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class Experience(BaseModel):
    """Professional experience entry."""

    company: str = Field(..., description="Company name")
    title: str = Field(..., description="Job title")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date (None if current)")
    description: list[str] = Field(default_factory=list, description="List of responsibilities")


class Education(BaseModel):
    """Education entry."""

    institution: str = Field(..., description="School or university name")
    degree: str = Field(..., description="Degree obtained")
    field_of_study: str = Field(..., description="Major or field of study")
    graduation_date: date = Field(..., description="Graduation date")
    gpa: Optional[float] = Field(None, description="GPA if applicable")


class Skill(BaseModel):
    """Skill entry."""

    category: str = Field(..., description="Skill category (e.g., Languages, Tools)")
    items: list[str] = Field(..., description="List of skills in this category")


class Project(BaseModel):
    """Project entry."""

    name: str = Field(..., description="Project name")
    personal_title: Optional[str] = Field(None, description="Your role or title on this project")
    description: str = Field(..., description="Short description")
    technologies: list[str] = Field(default_factory=list, description="Technologies used")
    url: Optional[str] = Field(None, description="Project URL")


class Resume(BaseModel):
    """Complete resume data model."""

    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Location")
    summary: str = Field(..., description="Professional summary")
    experience: list[Experience] = Field(default_factory=list, description="Work experience")
    education: list[Education] = Field(default_factory=list, description="Education history")
    skills: list[Skill] = Field(default_factory=list, description="Skills")
    projects: list[Project] = Field(default_factory=list, description="Projects")
    certifications: list[str] = Field(default_factory=list, description="Certifications")


# ── Project Management Models ──────────────────────────────────────────────────


class BulletPointCreate(BaseModel):
    """Schema for creating a bullet point."""

    text: str = Field(..., min_length=1, description="Bullet point text")
    order: int = Field(0, description="Display order")


class BulletPointOut(BulletPointCreate):
    """Schema for returning a bullet point."""

    id: int


class TagOut(BaseModel):
    """Schema for returning a tag."""

    id: int
    name: str


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    title: str = Field(..., min_length=1, max_length=255, description="Project title")
    personal_title: Optional[str] = Field(None, max_length=255, description="Your role on this project")
    start_month: int = Field(..., ge=1, le=12, description="Start month (1-12)")
    start_year: int = Field(..., ge=1900, le=2100, description="Start year")
    end_month: Optional[int] = Field(None, ge=1, le=12, description="End month")
    end_year: Optional[int] = Field(None, ge=1900, le=2100, description="End year")
    technologies: list[str] = Field(default_factory=list, description="Technologies used")
    frameworks: list[str] = Field(default_factory=list, description="Frameworks used")
    languages: list[str] = Field(default_factory=list, description="Languages used")
    bullet_points: list[str] = Field(default_factory=list, description="Numbered bullet points")
    tags: list[str] = Field(default_factory=list, description="Project tags")


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    personal_title: Optional[str] = Field(None, max_length=255)
    start_month: Optional[int] = Field(None, ge=1, le=12)
    start_year: Optional[int] = Field(None, ge=1900, le=2100)
    end_month: Optional[int] = Field(None, ge=1, le=12)
    end_year: Optional[int] = Field(None, ge=1900, le=2100)
    technologies: Optional[list[str]] = None
    frameworks: Optional[list[str]] = None
    languages: Optional[list[str]] = None
    bullet_points: Optional[list[str]] = None
    tags: Optional[list[str]] = None


class ProjectOut(BaseModel):
    """Schema for returning a project."""

    id: int
    title: str
    personal_title: Optional[str] = None
    start_month: int
    start_year: int
    end_month: Optional[int] = None
    end_year: Optional[int] = None
    technologies: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    bullet_points: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
