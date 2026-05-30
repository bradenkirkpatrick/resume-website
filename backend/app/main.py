"""
Main application module for the Resume Website API.

This module initializes the FastAPI application with CORS middleware
and includes all route handlers.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes.projects import router as projects_router
from app.routes.resume import router as resume_router
from app.routes.sections import router as sections_router

load_dotenv()

app = FastAPI(
    title="Resume Website API",
    description="API for serving resume data and managing projects",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(sections_router, prefix="/api")


@app.on_event("startup")
def startup():
    """Initialize the database on startup."""
    init_db()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
