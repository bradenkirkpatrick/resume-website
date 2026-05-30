"""
Section ordering API routes.

Provides endpoints to get and update the display order of resume sections.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SectionOrderDB, get_db, init_db

router = APIRouter(prefix="/sections", tags=["sections"])

DEFAULT_ORDER = [
    "summary",
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
]


def _get_or_create_order(db: Session) -> SectionOrderDB:
    """Get the single section order row, creating it with defaults if needed."""
    init_db()
    order = db.query(SectionOrderDB).filter(SectionOrderDB.id == 1).first()
    if not order:
        order = SectionOrderDB(id=1, section_order=",".join(DEFAULT_ORDER))
        db.add(order)
        db.commit()
        db.refresh(order)
    return order


@router.get("/order", response_model=list[str])
async def get_section_order(db: Session = Depends(get_db)):
    """Get the current section display order."""
    order = _get_or_create_order(db)
    parts = order.section_order.split(",")
    return [p for p in parts if p]


@router.put("/order", response_model=list[str])
async def update_section_order(
    sections: list[str],
    db: Session = Depends(get_db),
):
    """Update the section display order."""
    if not sections:
        sections = DEFAULT_ORDER
    order = _get_or_create_order(db)
    order.section_order = ",".join(sections)
    db.commit()
    return sections
