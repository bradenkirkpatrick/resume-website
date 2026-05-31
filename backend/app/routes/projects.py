"""Projects API routes with normalized schema + query endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import ProjectDB, get_db, init_db, json_list, parse_json_list
from app.models import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.on_event("startup")
def on_startup():
    init_db()


def _to_out(p: ProjectDB) -> ProjectOut:
    return ProjectOut(
        id=p.id,
        person_id=p.person_id,
        project_name=p.project_name,
        project_role=p.project_role,
        start_date=p.start_date,
        end_date=p.end_date,
        bullet_points=parse_json_list(p.bullet_points),
        frameworks=parse_json_list(p.frameworks),
        languages=parse_json_list(p.languages),
        technologies=parse_json_list(p.technologies),
        tags=parse_json_list(p.tags),
    )


@router.get("", response_model=list[ProjectOut])
async def list_projects(person_id: int = None, db: Session = Depends(get_db)):
    q = db.query(ProjectDB)
    if person_id is not None:
        q = q.filter(ProjectDB.person_id == person_id)
    q = q.order_by(ProjectDB.start_date.desc().nulls_last())
    return [_to_out(p) for p in q.all()]


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    return _to_out(p)


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    p = ProjectDB(
        person_id=data.person_id,
        project_name=data.project_name,
        project_role=data.project_role,
        start_date=data.start_date,
        end_date=data.end_date,
        bullet_points=json_list(data.bullet_points),
        frameworks=json_list(data.frameworks),
        languages=json_list(data.languages),
        technologies=json_list(data.technologies),
        tags=json_list(data.tags),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _to_out(p)


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    p = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    upd = data.model_dump(exclude_unset=True)
    for lst_field in ("bullet_points", "frameworks", "languages", "technologies", "tags"):
        if lst_field in upd and upd[lst_field] is not None:
            upd[lst_field] = json_list(upd[lst_field])
    for k, v in upd.items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return _to_out(p)


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not p:
        raise HTTPException(404, "Project not found")
    db.delete(p)
    db.commit()


# ── Query Endpoints ────────────────────────────────────────────────────────────

def _collect_unique_field(db: Session, field_name: str) -> list[str]:
    items: set[str] = set()
    projects = db.query(ProjectDB).all()
    for p in projects:
        vals = parse_json_list(getattr(p, field_name))
        for v in vals:
            v = v.strip()
            if v:
                items.add(v)
    return sorted(items)


@router.get("/tech/all", response_model=list[str])
async def get_all_technologies(db: Session = Depends(get_db)):
    return _collect_unique_field(db, "technologies")


@router.get("/languages/all", response_model=list[str])
async def get_all_languages(db: Session = Depends(get_db)):
    return _collect_unique_field(db, "languages")


@router.get("/frameworks/all", response_model=list[str])
async def get_all_frameworks(db: Session = Depends(get_db)):
    return _collect_unique_field(db, "frameworks")


@router.get("/tags/all", response_model=list[str])
async def get_all_tags(db: Session = Depends(get_db)):
    return _collect_unique_field(db, "tags")
