"""
Project management API routes.

Provides CRUD endpoints for user-managed projects with
technologies, frameworks, languages, bullet points, and tags.
"""

import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import (
    BulletPointDB,
    ProjectDB,
    ProjectTag,
    TagDB,
    TechItemDB,
    get_db,
    init_db,
)
from app.models import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.google_docs import fetch_document_content, parse_resume_from_text

router = APIRouter(prefix="/projects", tags=["projects"])


@router.on_event("startup")
def on_startup():
    """Initialize the database and seed default projects on first run."""
    init_db()
    _seed_default_projects()


def _seed_default_projects():
    """Seed the projects table with resume projects if it's empty."""
    from app.database import SessionLocal as _SessionLocal

    db = _SessionLocal()
    try:
        existing = db.query(ProjectDB).count()
        if existing > 0:
            return

        # Fetch resume data (Google Doc → fallback)
        document_id = os.getenv("GOOGLE_DOCS_ID")
        resume = None
        if document_id:
            content = fetch_document_content(document_id)
            if content:
                resume = parse_resume_from_text(content)

        if not resume:
            from app.routes.resume import FALLBACK_RESUME
            resume = FALLBACK_RESUME

        # Create a managed project from each resume project entry
        for proj in resume.projects:
            bp_lines = [d for d in proj.description.split("\n") if d.strip()] if proj.description else []
            if not bp_lines:
                bp_lines = [proj.description] if proj.description else []

            project = ProjectDB(
                title=proj.name.split("        ")[0] if "        " in proj.name else proj.name,
                personal_title=proj.personal_title,
                start_month=1,
                start_year=2026,
            )
            db.add(project)
            db.flush()

            # Add technologies
            for tech in proj.technologies:
                item = TechItemDB(name=tech.strip(), category="technology", project_id=project.id)
                db.add(item)

            # Add bullet points
            for i, line in enumerate(bp_lines):
                bp = BulletPointDB(text=line.strip(), order=i, project_id=project.id)
                db.add(bp)

            # Auto-tags from technologies
            known_tags = {
                "python": "python",
                "react": "react",
                "fastapi": "fastapi",
                "docker": "docker",
                "aws": "aws",
                "node": "node.js",
                "javascript": "javascript",
                "typescript": "typescript",
                "keras": "machine-learning",
                "scikit": "machine-learning",
                "sklearn": "machine-learning",
                "mpi": "hpc",
                "cuda": "hpc",
                "openmp": "hpc",
                "kubernetes": "kubernetes",
                "postgresql": "database",
                "sql": "database",
                "sqlite": "database",
                "next.js": "next.js",
                "ktor": "kotlin",
            }
            added_tags = set()
            for tech in proj.technologies:
                key = tech.lower().strip().rstrip(",*")
                tag_name = known_tags.get(key)
                if tag_name and tag_name not in added_tags:
                    _get_or_create_project_tag(db, project.id, tag_name)
                    added_tags.add(tag_name)

        db.commit()
    finally:
        db.close()


def _get_or_create_project_tag(db: Session, project_id: int, tag_name: str):
    """Helper to create a tag and associate it with a project."""
    tag = db.query(TagDB).filter(TagDB.name == tag_name).first()
    if not tag:
        tag = TagDB(name=tag_name)
        db.add(tag)
        db.flush()
    existing = db.query(ProjectTag).filter(
        ProjectTag.project_id == project_id,
        ProjectTag.tag_id == tag.id,
    ).first()
    if not existing:
        db.add(ProjectTag(project_id=project_id, tag_id=tag.id))


def _items_by_category(project: ProjectDB, category: str) -> list[str]:
    """Get tech item names for a given category."""
    return [
        t.name
        for t in project.all_tech_items
        if t.category == category
    ]


def _project_to_out(project: ProjectDB) -> ProjectOut:
    """Convert a database project to a Pydantic output model."""
    return ProjectOut(
        id=project.id,
        title=project.title,
        personal_title=project.personal_title,
        start_month=project.start_month,
        start_year=project.start_year,
        end_month=project.end_month,
        end_year=project.end_year,
        technologies=_items_by_category(project, "technology"),
        frameworks=_items_by_category(project, "framework"),
        languages=_items_by_category(project, "language"),
        bullet_points=[bp.text for bp in sorted(project.bullet_points, key=lambda x: x.order)],
        tags=[pt.tag.name for pt in project.project_tags],
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _get_or_create_tag(db: Session, name: str) -> TagDB:
    """Get an existing tag by name or create a new one."""
    tag = db.query(TagDB).filter(TagDB.name == name).first()
    if not tag:
        tag = TagDB(name=name)
        db.add(tag)
        db.flush()
    return tag


@router.get("", response_model=list[ProjectOut])
async def list_projects(db: Session = Depends(get_db)):
    """List all user-managed projects ordered by newest first."""
    projects = (
        db.query(ProjectDB)
        .order_by(ProjectDB.start_year.desc(), ProjectDB.start_month.desc())
        .all()
    )
    return [_project_to_out(p) for p in projects]


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project with technologies, bullet points, and tags."""
    project = ProjectDB(
        title=data.title,
        personal_title=data.personal_title,
        start_month=data.start_month,
        start_year=data.start_year,
        end_month=data.end_month,
        end_year=data.end_year,
    )
    db.add(project)
    db.flush()

    # Add tech items by category
    CATEGORIES = {
        "technologies": "technology",
        "frameworks": "framework",
        "languages": "language",
    }
    for field, category in CATEGORIES.items():
        for name in getattr(data, field):
            item = TechItemDB(name=name, category=category, project_id=project.id)
            db.add(item)

    # Add bullet points
    for i, bp_text in enumerate(data.bullet_points):
        bp = BulletPointDB(text=bp_text, order=i, project_id=project.id)
        db.add(bp)

    # Add tags
    for tag_name in data.tags:
        tag = _get_or_create_tag(db, tag_name)
        pt = ProjectTag(project_id=project.id, tag_id=tag.id)
        db.add(pt)

    db.commit()
    db.refresh(project)
    return _project_to_out(project)


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a single project by ID."""
    project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_to_out(project)


CATEGORY_MAP = {
    "technologies": "technology",
    "frameworks": "framework",
    "languages": "language",
}


def _update_category_items(
    db: Session, project_id: int, items: list[str], category: str
):
    """Replace all items in a given category for a project."""
    db.query(TechItemDB).filter(
        TechItemDB.project_id == project_id,
        TechItemDB.category == category,
    ).delete()
    for name in items:
        db.add(TechItemDB(name=name, category=category, project_id=project_id))


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing project."""
    project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update scalar fields
    update_data = data.model_dump(exclude_unset=True)
    for field in ["title", "personal_title", "start_month", "start_year", "end_month", "end_year"]:
        if field in update_data:
            setattr(project, field, update_data[field])

    # Update tech items by category
    for field, category in CATEGORY_MAP.items():
        if field in update_data:
            _update_category_items(db, project_id, update_data[field], category)

    # Update bullet points
    if "bullet_points" in update_data:
        db.query(BulletPointDB).filter(BulletPointDB.project_id == project_id).delete()
        for i, bp_text in enumerate(update_data["bullet_points"]):
            bp = BulletPointDB(text=bp_text, order=i, project_id=project.id)
            db.add(bp)

    # Update tags
    if "tags" in update_data:
        db.query(ProjectTag).filter(ProjectTag.project_id == project_id).delete()
        for tag_name in update_data["tags"]:
            tag = _get_or_create_tag(db, tag_name)
            pt = ProjectTag(project_id=project.id, tag_id=tag.id)
            db.add(pt)

    db.commit()
    db.refresh(project)
    return _project_to_out(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project and all associated data."""
    project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()


@router.get("/tags/all", response_model=list[str])
async def list_tags(db: Session = Depends(get_db)):
    """List all unique tag names."""
    tags = db.query(TagDB).order_by(TagDB.name).all()
    return [t.name for t in tags]
