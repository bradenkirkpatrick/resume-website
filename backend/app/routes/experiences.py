"""Experiences API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import ExperienceDB, get_db, json_list, parse_json_list
from app.models import ExperienceCreate, ExperienceOut, ExperienceUpdate

router = APIRouter(prefix="/experiences", tags=["experiences"])


def _to_out(e: ExperienceDB) -> ExperienceOut:
    return ExperienceOut(
        id=e.id,
        person_id=e.person_id,
        company=e.company,
        city=e.city,
        state=e.state,
        role=e.role,
        start_date=e.start_date,
        end_date=e.end_date,
        bullet_points=parse_json_list(e.bullet_points),
    )


@router.get("", response_model=list[ExperienceOut])
async def list_experiences(person_id: int = None, db: Session = Depends(get_db)):
    q = db.query(ExperienceDB)
    if person_id:
        q = q.filter(ExperienceDB.person_id == person_id)
    return [_to_out(e) for e in q.all()]


@router.get("/{exp_id}", response_model=ExperienceOut)
async def get_experience(exp_id: int, db: Session = Depends(get_db)):
    e = db.query(ExperienceDB).filter(ExperienceDB.id == exp_id).first()
    if not e:
        raise HTTPException(404, "Experience not found")
    return _to_out(e)


@router.post("", response_model=ExperienceOut, status_code=201)
async def create_experience(data: ExperienceCreate, db: Session = Depends(get_db)):
    e = ExperienceDB(
        person_id=data.person_id,
        company=data.company,
        city=data.city,
        state=data.state,
        role=data.role,
        start_date=data.start_date,
        end_date=data.end_date,
        bullet_points=json_list(data.bullet_points),
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return _to_out(e)


@router.put("/{exp_id}", response_model=ExperienceOut)
async def update_experience(exp_id: int, data: ExperienceUpdate, db: Session = Depends(get_db)):
    e = db.query(ExperienceDB).filter(ExperienceDB.id == exp_id).first()
    if not e:
        raise HTTPException(404, "Experience not found")
    upd = data.model_dump(exclude_unset=True)
    if "bullet_points" in upd:
        upd["bullet_points"] = json_list(upd["bullet_points"])
    for k, v in upd.items():
        setattr(e, k, v)
    db.commit()
    db.refresh(e)
    return _to_out(e)


@router.delete("/{exp_id}", status_code=204)
async def delete_experience(exp_id: int, db: Session = Depends(get_db)):
    e = db.query(ExperienceDB).filter(ExperienceDB.id == exp_id).first()
    if not e:
        raise HTTPException(404, "Experience not found")
    db.delete(e)
    db.commit()
