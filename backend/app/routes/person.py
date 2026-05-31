"""Person API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import PersonDB, get_db
from app.models import PersonCreate, PersonOut, PersonUpdate

router = APIRouter(prefix="/person", tags=["person"])


@router.get("", response_model=list[PersonOut])
async def list_persons(db: Session = Depends(get_db)):
    return db.query(PersonDB).all()


@router.get("/{person_id}", response_model=PersonOut)
async def get_person(person_id: int, db: Session = Depends(get_db)):
    p = db.query(PersonDB).filter(PersonDB.person_id == person_id).first()
    if not p:
        raise HTTPException(404, "Person not found")
    return p


@router.post("", response_model=PersonOut, status_code=201)
async def create_person(data: PersonCreate, db: Session = Depends(get_db)):
    p = PersonDB(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{person_id}", response_model=PersonOut)
async def update_person(person_id: int, data: PersonUpdate, db: Session = Depends(get_db)):
    p = db.query(PersonDB).filter(PersonDB.person_id == person_id).first()
    if not p:
        raise HTTPException(404, "Person not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{person_id}", status_code=204)
async def delete_person(person_id: int, db: Session = Depends(get_db)):
    p = db.query(PersonDB).filter(PersonDB.person_id == person_id).first()
    if not p:
        raise HTTPException(404, "Person not found")
    db.delete(p)
    db.commit()
