"""
Data models for the Resume Website application.

Pydantic models for the normalized schema:
  Person, Education, Projects, Experiences
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# ── Person ─────────────────────────────────────────────────────────────────────

class PersonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    city: Optional[str] = None
    state: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class PersonOut(BaseModel):
    person_id: int
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


# ── Education ──────────────────────────────────────────────────────────────────

class EducationCreate(BaseModel):
    person_id: int
    school: str = Field(..., min_length=1, max_length=255)
    city: Optional[str] = None
    state: Optional[str] = None
    degree: Optional[str] = None
    degree_minor: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    relevant_courses: Optional[str] = None


class EducationUpdate(BaseModel):
    school: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    degree: Optional[str] = None
    degree_minor: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    relevant_courses: Optional[str] = None


class EducationOut(BaseModel):
    id: int
    person_id: int
    school: str
    city: Optional[str] = None
    state: Optional[str] = None
    degree: Optional[str] = None
    degree_minor: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    relevant_courses: Optional[str] = None

    class Config:
        from_attributes = True


# ── Projects ───────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    person_id: int
    project_name: str = Field(..., min_length=1, max_length=255)
    project_role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    bullet_points: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    project_role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    bullet_points: Optional[list[str]] = None
    frameworks: Optional[list[str]] = None
    languages: Optional[list[str]] = None
    technologies: Optional[list[str]] = None
    tags: Optional[list[str]] = None


class ProjectOut(BaseModel):
    id: int
    person_id: int
    project_name: str
    project_role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    bullet_points: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── Experiences ────────────────────────────────────────────────────────────────

class ExperienceCreate(BaseModel):
    person_id: int
    company: str = Field(..., min_length=1, max_length=255)
    city: Optional[str] = None
    state: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    bullet_points: list[str] = Field(default_factory=list)


class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    bullet_points: Optional[list[str]] = None


class ExperienceOut(BaseModel):
    id: int
    person_id: int
    company: str
    city: Optional[str] = None
    state: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    bullet_points: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── Query Results ──────────────────────────────────────────────────────────────

class TechItemOut(BaseModel):
    name: str

# ── Legacy models (for Google Doc parser compatibility) ────────────────────────

class LegacyExperience(BaseModel):
    company: str = ""
    title: str = ""
    start_date: date = date.today()
    end_date: Optional[date] = None
    description: list[str] = Field(default_factory=list)


class LegacyEducation(BaseModel):
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    graduation_date: date = date.today()
    gpa: Optional[float] = None


class LegacySkill(BaseModel):
    category: str = ""
    items: list[str] = Field(default_factory=list)


class LegacyProject(BaseModel):
    name: str = ""
    personal_title: Optional[str] = None
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    url: Optional[str] = None


class ResumeLegacy(BaseModel):
    name: str = ""
    email: str = ""
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    summary: str = ""
    experience: list[LegacyExperience] = Field(default_factory=list)
    education: list[LegacyEducation] = Field(default_factory=list)
    skills: list[LegacySkill] = Field(default_factory=list)
    projects: list[LegacyProject] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


# Aliases for backward compat with Google Doc parser
Experience = LegacyExperience
Education = LegacyEducation
Skill = LegacySkill
Project = LegacyProject
Resume = ResumeLegacy
