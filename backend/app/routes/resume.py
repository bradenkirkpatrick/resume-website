"""
Resume API routes.

Provides endpoints for fetching resume data and downloading
the resume as a PDF.
"""

import os

from fastapi import APIRouter, Response

from app.models import Resume
from app.services.google_docs import fetch_document_content, parse_resume_from_text

router = APIRouter(tags=["resume"])

# In-memory fallback resume data for when Google Docs is not configured
FALLBACK_RESUME = Resume(
    name="Your Name",
    email="your.email@example.com",
    phone="+1 (555) 123-4567",
    location="San Francisco, CA",
    summary="Experienced software engineer with a passion for building great products.",
    experience=[
        {
            "company": "Example Corp",
            "title": "Senior Software Engineer",
            "start_date": "2020-01-01",
            "end_date": None,
            "description": [
                "Led development of microservices architecture",
                "Improved CI/CD pipeline reducing deployment time by 60%",
                "Mentored junior developers on best practices",
            ],
        },
        {
            "company": "Tech Startup",
            "title": "Software Engineer",
            "start_date": "2017-03-01",
            "end_date": "2019-12-31",
            "description": [
                "Built RESTful APIs serving 100k+ daily requests",
                "Implemented automated testing achieving 90% code coverage",
            ],
        },
    ],
    education=[
        {
            "institution": "University of Technology",
            "degree": "Bachelor of Science",
            "field_of_study": "Computer Science",
            "graduation_date": "2017-05-15",
            "gpa": 3.7,
        }
    ],
    skills=[
        {"category": "Languages", "items": ["Python", "JavaScript", "TypeScript", "Java"]},
        {"category": "Frameworks", "items": ["React", "FastAPI", "Node.js", "Django"]},
        {"category": "Tools", "items": ["Docker", "Kubernetes", "AWS", "Git"]},
    ],
    projects=[
        {
            "name": "Resume Website",
            "description": "Automated resume generation from Google Docs",
            "technologies": ["Python", "React", "FastAPI"],
            "url": "https://github.com/example/resume-website",
        }
    ],
    certifications=["AWS Certified Solutions Architect", "Google Cloud Professional"],
)


@router.get("/resume", response_model=Resume)
async def get_resume():
    """
    Fetch the resume data.

    Attempts to fetch from Google Docs if configured. Falls back
    to built-in example data if Google Docs is not set up.
    """
    document_id = os.getenv("GOOGLE_DOCS_ID")
    if document_id:
        content = fetch_document_content(document_id)
        if content:
            return parse_resume_from_text(content)

    return FALLBACK_RESUME


@router.get("/resume/download")
async def download_resume():
    """
    Download the resume as a file.

    Returns a JSON file for download. In production, this would
    generate a PDF from the resume data.
    """
    resume = await get_resume()
    json_str = resume.model_dump_json(indent=2)

    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=resume.json"},
    )
