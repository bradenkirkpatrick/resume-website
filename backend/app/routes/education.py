"""Education API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import EducationDB, get_db
from app.models import EducationCreate, EducationOut, EducationUpdate

router = APIRouter(prefix="/education", tags=["education"])


@router.get("", response_model=list[EducationOut])
async def list_education(person_id: int = None, db: Session = Depends(get_db)):
    q = db.query(EducationDB)
    if person_id:
        q = q.filter(EducationDB.person_id == person_id)
    return q.all()


@router.get("/{edu_id}", response_model=EducationOut)
async def get_education(edu_id: int, db: Session = Depends(get_db)):
    e = db.query(EducationDB).filter(EducationDB.id == edu_id).first()
    if not e:
        raise HTTPException(404, "Education not found")
    return e


@router.post("", response_model=EducationOut, status_code=201)
async def create_education(data: EducationCreate, db: Session = Depends(get_db)):
    e = EducationDB(**data.model_dump())
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


@router.put("/{edu_id}", response_model=EducationOut)
async def update_education(edu_id: int, data: EducationUpdate, db: Session = Depends(get_db)):
    e = db.query(EducationDB).filter(EducationDB.id == edu_id).first()
    if not e:
        raise HTTPException(404, "Education not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(e, k, v)
    db.commit()
    db.refresh(e)
    return e


@router.delete("/{edu_id}", status_code=204)
async def delete_education(edu_id: int, db: Session = Depends(get_db)):
    e = db.query(EducationDB).filter(EducationDB.id == edu_id).first()
    if not e:
        raise HTTPException(404, "Education not found")
    db.delete(e)
    db.commit()
