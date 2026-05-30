"""
Tests for the resume API routes and data models.
"""

from datetime import date

from httpx import AsyncClient

from app.models import (
    Education,
    Experience,
    Project,
    Resume,
    Skill,
)


class TestModels:
    """Tests for Pydantic data models."""

    def test_experience_model(self):
        """Test creating an Experience model."""
        exp = Experience(
            company="Test Corp",
            title="Engineer",
            start_date=date(2020, 1, 1),
            description=["Built things"],
        )
        assert exp.company == "Test Corp"
        assert exp.title == "Engineer"
        assert exp.start_date == date(2020, 1, 1)
        assert exp.end_date is None
        assert exp.description == ["Built things"]

    def test_experience_with_end_date(self):
        """Test Experience with an end date."""
        exp = Experience(
            company="Test Corp",
            title="Engineer",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31),
            description=["Built things"],
        )
        assert exp.end_date == date(2022, 12, 31)

    def test_education_model(self):
        """Test creating an Education model."""
        edu = Education(
            institution="University",
            degree="BS",
            field_of_study="CS",
            graduation_date=date(2020, 5, 15),
            gpa=3.5,
        )
        assert edu.institution == "University"
        assert edu.degree == "BS"
        assert edu.gpa == 3.5

    def test_education_without_gpa(self):
        """Test Education without GPA."""
        edu = Education(
            institution="University",
            degree="BS",
            field_of_study="CS",
            graduation_date=date(2020, 5, 15),
        )
        assert edu.gpa is None

    def test_skill_model(self):
        """Test creating a Skill model."""
        skill = Skill(
            category="Languages",
            items=["Python", "JavaScript"],
        )
        assert skill.category == "Languages"
        assert skill.items == ["Python", "JavaScript"]

    def test_project_model(self):
        """Test creating a Project model."""
        project = Project(
            name="Test Project",
            description="A test project",
            technologies=["Python", "React"],
            url="https://github.com/test",
        )
        assert project.name == "Test Project"
        assert project.url == "https://github.com/test"

    def test_project_without_url(self):
        """Test Project without URL."""
        project = Project(
            name="Test Project",
            description="A test project",
        )
        assert project.url is None

    def test_full_resume_model(self):
        """Test creating a complete Resume model."""
        resume = Resume(
            name="John Doe",
            email="john@example.com",
            phone="+1-555-1234",
            location="NYC",
            summary="A great engineer",
            experience=[
                Experience(
                    company="Corp",
                    title="Engineer",
                    start_date=date(2020, 1, 1),
                )
            ],
            education=[
                Education(
                    institution="Uni",
                    degree="BS",
                    field_of_study="CS",
                    graduation_date=date(2020, 5, 15),
                )
            ],
            skills=[Skill(category="Languages", items=["Python"])],
            projects=[Project(name="Proj", description="Desc")],
            certifications=["AWS Certified"],
        )
        assert resume.name == "John Doe"
        assert len(resume.experience) == 1
        assert len(resume.education) == 1
        assert len(resume.skills) == 1
        assert len(resume.projects) == 1
        assert len(resume.certifications) == 1

    def test_minimal_resume_model(self):
        """Test creating a minimal Resume."""
        resume = Resume(
            name="John Doe",
            email="john@example.com",
            summary="A great engineer",
        )
        assert resume.experience == []
        assert resume.education == []
        assert resume.skills == []
        assert resume.projects == []
        assert resume.certifications == []


class TestResumeAPI:
    """Tests for the Resume API endpoints."""

    async def test_get_resume_returns_valid_data(self, client: AsyncClient):
        """Test that /api/resume returns valid resume data."""
        response = await client.get("/api/resume")
        assert response.status_code == 200
        data = response.json()

        assert "name" in data
        assert "email" in data
        assert "summary" in data
        assert "experience" in data
        assert "education" in data
        assert "skills" in data
        assert "projects" in data
        assert "certifications" in data

    async def test_get_resume_has_name(self, client: AsyncClient):
        """Test that resume has a name field."""
        response = await client.get("/api/resume")
        data = response.json()
        assert len(data["name"]) > 0

    async def test_get_resume_has_email(self, client: AsyncClient):
        """Test that resume has an email field."""
        response = await client.get("/api/resume")
        data = response.json()
        assert "@" in data["email"]

    async def test_get_resume_experience(self, client: AsyncClient):
        """Test that resume has experience entries."""
        response = await client.get("/api/resume")
        data = response.json()
        assert len(data["experience"]) > 0

        exp = data["experience"][0]
        assert "company" in exp
        assert "title" in exp
        assert "start_date" in exp

    async def test_get_resume_education(self, client: AsyncClient):
        """Test that resume has education entries."""
        response = await client.get("/api/resume")
        data = response.json()
        assert len(data["education"]) > 0

        edu = data["education"][0]
        assert "institution" in edu
        assert "degree" in edu

    async def test_get_resume_skills(self, client: AsyncClient):
        """Test that resume has skills."""
        response = await client.get("/api/resume")
        data = response.json()
        assert len(data["skills"]) > 0

        skill = data["skills"][0]
        assert "category" in skill
        assert "items" in skill

    async def test_get_resume_projects(self, client: AsyncClient):
        """Test that resume has projects."""
        response = await client.get("/api/resume")
        data = response.json()
        assert len(data["projects"]) > 0

    async def test_get_resume_certifications(self, client: AsyncClient):
        """Test that resume has certifications."""
        response = await client.get("/api/resume")
        data = response.json()
        assert len(data["certifications"]) > 0

    async def test_download_resume(self, client: AsyncClient):
        """Test that /api/resume/download returns a downloadable file."""
        response = await client.get("/api/resume/download")
        assert response.status_code == 200
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]
        assert "filename=resume.json" in response.headers["content-disposition"]

    async def test_download_resume_content(self, client: AsyncClient):
        """Test that downloaded resume content is valid JSON."""
        response = await client.get("/api/resume/download")
        data = response.json()
        assert "name" in data
        assert "email" in data

    async def test_download_content_type(self, client: AsyncClient):
        """Test that download endpoint returns JSON content type."""
        response = await client.get("/api/resume/download")
        assert response.headers["content-type"] == "application/json"

    async def test_resume_structure_valid(self, client: AsyncClient):
        """Test that resume data validates against the Resume model."""
        response = await client.get("/api/resume")
        data = response.json()
        resume = Resume(**data)
        assert isinstance(resume, Resume)


class TestGoogleDocsService:
    """Tests for the Google Docs integration service."""

    def test_extract_email(self):
        """Test email extraction from text."""
        from app.services.google_docs import _extract_email

        text = "John Doe\njohn.doe@example.com\n123-456-7890"
        assert _extract_email(text) == "john.doe@example.com"

    def test_extract_email_not_found(self):
        """Test email extraction when no email exists."""
        from app.services.google_docs import _extract_email

        text = "No email here"
        assert _extract_email(text) == ""

    def test_extract_phone(self):
        """Test phone number extraction."""
        from app.services.google_docs import _extract_phone

        text = "Contact: +1 (555) 123-4567"
        phone = _extract_phone(text)
        assert phone is not None
        assert "555" in str(phone)

    def test_extract_phone_not_found(self):
        """Test phone extraction when no phone exists."""
        from app.services.google_docs import _extract_phone

        text = "No phone here"
        assert _extract_phone(text) is None

    def test_extract_name(self):
        """Test name extraction from first line."""
        from app.services.google_docs import _extract_name

        text = "Jane Smith\njane@example.com"
        assert _extract_name(text) == "Jane Smith"

    def test_extract_name_skips_empty(self):
        """Test name extraction skips empty lines."""
        from app.services.google_docs import _extract_name

        text = "\n\n  \nJohn Doe\njohn@example.com"
        assert _extract_name(text) == "John Doe"

    def test_parse_resume_from_text(self):
        """Test parsing a full resume from text."""
        from app.services.google_docs import parse_resume_from_text

        text = """Jane Smith
jane@example.com
(555) 123-4567
San Francisco, CA

SUMMARY
Experienced software engineer with 5+ years of experience.

EXPERIENCE
Tech Corp
Senior Engineer
January 2020 - Present
Built microservices
Led team of 5 engineers

EDUCATION
MIT
BS
Computer Science
May 2017

SKILLS
Languages: Python, JavaScript, TypeScript
Tools: Docker, AWS, Git

PROJECTS
Awesome Project
A great open source project
Python, React
https://github.com/jane/awesome

CERTIFICATIONS
AWS Certified Developer
Google Cloud Engineer
"""
        resume = parse_resume_from_text(text)
        assert resume.name == "Jane Smith"
        assert resume.email == "jane@example.com"
        assert len(resume.experience) > 0
        assert len(resume.education) > 0
        assert len(resume.skills) > 0
        assert len(resume.projects) > 0
        assert len(resume.certifications) > 0

    def test_parse_resume_empty_text(self):
        """Test parsing empty text returns fallback name."""
        from app.services.google_docs import parse_resume_from_text

        resume = parse_resume_from_text("")
        assert resume.name == "Unknown"
        assert resume.email == ""

    def test_split_into_sections(self):
        """Test splitting text into sections."""
        from app.services.google_docs import _split_into_sections

        text = """Header line
SUMMARY
This is a summary.
EXPERIENCE
Job at company
EDUCATION
School name
"""
        sections = _split_into_sections(text)
        assert "summary" in sections
        assert "experience" in sections
        assert "education" in sections

    def test_parse_date_format(self):
        """Test date parsing."""
        from app.services.google_docs import _parse_date

        result = _parse_date("January 2020")
        assert result.year == 2020
        assert result.month == 1

    def test_parse_date_short_format(self):
        """Test short date format parsing."""
        from app.services.google_docs import _parse_date

        result = _parse_date("Jan 2020")
        assert result.year == 2020
        assert result.month == 1

    def test_fetch_via_api_no_credentials(self):
        """Test that _fetch_via_api returns None without credentials."""
        from app.services.google_docs import _fetch_via_api

        result = _fetch_via_api("test-doc-id")
        assert result is None

    def test_fetch_via_public_export(self):
        """Test fetching a public Google Doc via export URL."""
        from app.services.google_docs import _fetch_via_public_export

        result = _fetch_via_public_export("1IvKov91tVgnB4mHLVjz1s18q9OJnNeWyh3mNsmG3n84")
        assert result is not None
        assert len(result.strip()) > 0
        # The doc should contain resume-like content
        assert "Braden" in result or "braden" in result.lower()

    def test_fetch_document_content_real_doc(self):
        """Test the full document fetch flow with the real public doc ID."""
        import os
        from app.services.google_docs import fetch_document_content

        # Clear any GOOGLE_APPLICATION_CREDENTIALS so it falls back to public export
        old_val = os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        try:
            content = fetch_document_content(
                "1IvKov91tVgnB4mHLVjz1s18q9OJnNeWyh3mNsmG3n84"
            )
            assert content is not None
            assert len(content.strip()) > 0
        finally:
            if old_val is not None:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = old_val

    def test_fetch_via_public_export_bad_id(self):
        """Test that public export returns None for a nonexistent doc ID."""
        from app.services.google_docs import _fetch_via_public_export

        result = _fetch_via_public_export("nonexistent-doc-id-12345")
        assert result is None

    def test_parse_skills_with_colon(self):
        """Test parsing skills with colon separator."""
        from app.services.google_docs import _parse_skills

        text = "Languages: Python, JavaScript, Go\nTools: Docker, Git"
        skills = _parse_skills(text)
        assert len(skills) == 2
        assert skills[0].category == "Languages"
        assert "Python" in skills[0].items
        assert skills[1].category == "Tools"
        assert "Docker" in skills[1].items

    def test_parse_skills_without_colon(self):
        """Test parsing skills without colon separator."""
        from app.services.google_docs import _parse_skills

        text = "Python\nJavaScript"
        skills = _parse_skills(text)
        assert len(skills) == 2
        assert all(s.category == "General" for s in skills)

    def test_parse_projects_with_url(self):
        """Test parsing projects with URL."""
        from app.services.google_docs import _parse_projects

        text = """My Project
A cool project
Python, React
https://github.com/me/my-project"""
        projects = _parse_projects(text)
        assert len(projects) == 1
        assert projects[0].name == "My Project"
        assert projects[0].url == "https://github.com/me/my-project"

    def test_parse_certifications(self):
        """Test parsing certifications."""
        from app.services.google_docs import _parse_certifications

        text = "AWS Certified Developer\nGoogle Cloud Engineer"
        certs = _parse_certifications(text)
        assert len(certs) == 2
        assert "AWS Certified Developer" in certs
