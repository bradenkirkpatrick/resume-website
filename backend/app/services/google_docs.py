"""
Google Docs integration service.

This module handles fetching resume data from a Google Doc.
It supports two methods:
1. Public export URL (no authentication needed for shared docs)
2. Google Docs API (requires service account credentials for private docs)

Environment variables:
    GOOGLE_DOCS_ID: The ID of the Google Doc to fetch
    GOOGLE_APPLICATION_CREDENTIALS: Path to the service account JSON (optional)
"""

import os
import re
import urllib.request
from datetime import date
from typing import Optional

from app.models import Education, Experience, Project, Resume, Skill


def fetch_document_content(document_id: str) -> Optional[str]:
    """
    Fetch the content of a Google Doc by its ID.

    Tries two methods:
    1. Google Docs API (if service account credentials are configured)
    2. Public export URL (works for any publicly shared doc)

    Args:
        document_id: The Google Doc document ID.

    Returns:
        The full text content of the document, or None if fetching fails.
    """
    # Method 1: Google Docs API (authenticated, for private docs)
    content = _fetch_via_api(document_id)
    if content is not None:
        return content

    # Method 2: Public export URL (for publicly shared docs)
    content = _fetch_via_public_export(document_id)
    if content is not None:
        return content

    return None


def _fetch_via_api(document_id: str) -> Optional[str]:
    """Try to fetch via the Google Docs API using service account credentials."""
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not os.path.exists(creds_path):
        return None

    try:
        from google.oauth2 import service_account  # pragma: no cover
        from googleapiclient.discovery import build  # pragma: no cover
        from googleapiclient.errors import HttpError  # pragma: no cover

        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/documents.readonly"],
        )
        service = build("docs", "v1", credentials=credentials)

        document = service.documents().get(documentId=document_id).execute()
        content = document.get("body", {}).get("content", [])
        return _extract_api_text(content)
    except (ImportError, HttpError, Exception) as e:
        print(f"Google Docs API fetch failed: {e}")  # pragma: no cover
        return None  # pragma: no cover


def _fetch_via_public_export(document_id: str) -> Optional[str]:
    """Fetch document content via the public Google Docs export URL."""
    export_url = (
        f"https://docs.google.com/document/d/{document_id}/export?format=txt"
    )
    try:
        with urllib.request.urlopen(export_url, timeout=15) as response:
            content = response.read().decode("utf-8")
            if content.strip():
                return content
            return None
    except Exception as e:
        print(f"Public export fetch failed: {e}")
        return None


def _extract_api_text(content: list) -> str:  # pragma: no cover
    """Extract plain text from Google Docs API response structure."""
    text_parts = []
    for element in content:
        paragraph = element.get("paragraph", {})
        for text_run in paragraph.get("elements", []):
            text_run_data = text_run.get("textRun", {})
            text = text_run_data.get("content", "")
            if text:
                text_parts.append(text)
    return "".join(text_parts)


def parse_resume_from_text(text: str) -> Resume:
    """
    Parse structured resume data from plain text.

    This parser expects sections separated by headings like:
        SUMMARY
        EXPERIENCE
        EDUCATION
        SKILLS
        PROJECTS
        CERTIFICATIONS

    Inside each section, data is parsed heuristically.

    Args:
        text: The plain text content of a resume.

    Returns:
        A Resume model populated with parsed data.
    """
    sections = _split_into_sections(text)

    name = _extract_name(text)
    email = _extract_email(text)
    phone = _extract_phone(text)
    location = _extract_location(text)
    linkedin_url = _extract_linkedin_url(text)

    summary = sections.get("summary", "")
    experience = _parse_experience(sections.get("experience", ""))
    education = _parse_education(sections.get("education", ""))
    skills = _parse_skills(sections.get("skills", ""))
    projects = _parse_projects(sections.get("projects", ""))
    certifications = _parse_certifications(sections.get("certifications", ""))

    return Resume(
        name=name,
        email=email,
        phone=phone,
        location=location,
        linkedin_url=linkedin_url,
        summary=summary.strip(),
        experience=experience,
        education=education,
        skills=skills,
        projects=projects,
        certifications=certifications,
    )


def _split_into_sections(text: str) -> dict[str, str]:
    """Split document text into named sections."""
    section_headers = {
        "SUMMARY": "summary",
        "EXPERIENCE": "experience",
        "EDUCATION": "education",
        "SKILLS": "skills",
        "SKILLS AND TECHNOLOGIES": "skills",
        "PROJECTS": "projects",
        "CERTIFICATIONS": "certifications",
        "PROFESSIONAL EXPERIENCE": "experience",
        "OTHER EXPERIENCE": "experience",
        "WORK EXPERIENCE": "experience",
    }
    sections = {}
    current_section = "header"
    current_content: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip().upper()
        # Normalize: collapse multiple spaces for matching
        normalized = " ".join(stripped.split())
        if normalized in section_headers:
            sections[current_section] = "\n".join(current_content)
            current_section = section_headers[normalized]
            current_content = []
        else:
            current_content.append(line)

    sections[current_section] = "\n".join(current_content)
    return sections


def _extract_name(text: str) -> str:
    """Extract name from the first non-empty line."""
    for line in text.split("\n"):
        stripped = line.strip().strip("\ufeff")
        if stripped and not stripped.startswith(("@", "http")):
            return stripped
    return "Unknown"


def _extract_email(text: str) -> str:
    """Extract email address from text."""
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def _extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    match = re.search(r"(\+?\d[\d\s\-().]{7,}\d)", text)
    return match.group(1).strip() if match else None


LINKEDIN_URL = "https://www.linkedin.com/in/braden-kirkpatrick/"


def _extract_location(text: str) -> Optional[str]:
    """Extract location from text near contact info, stripping LinkedIn."""
    lines = text.split("\n")
    for line in lines[1:4]:
        stripped = line.strip()
        # Remove LinkedIn mention from location string
        cleaned = re.sub(r"\s*•\s*LinkedIn\s*•?.*", "", stripped).strip()
        if re.search(r"[,]?\s*(?:CA|NY|TX|FL|IL|PA|OH|GA|NC|MI|WA|AZ|CO|MA|OR|MN)", cleaned):
            return cleaned
    return None


def _extract_linkedin_url(text: str) -> Optional[str]:
    """Detect if 'LinkedIn' appears in the contact info and return the URL."""
    lines = text.split("\n")
    for line in lines[1:4]:
        if "LinkedIn" in line:
            return LINKEDIN_URL
    return None


def _clean_tab_suffix(text: str) -> str:
    """Remove tab or multi-space separated suffix (location, date) from a field."""
    # Try tab first
    if "\t" in text:
        return text.split("\t")[0].strip()
    # Try 3+ spaces (Google Doc uses spaces not tabs)
    cleaned = re.sub(r"\s{3,}.*", "", text).strip()
    return cleaned if cleaned else text


def _extract_dates(text: str):
    """Extract start/end dates from a string like 'Aug 2022 - Aug 2023' or 'May 2026'."""
    dates = re.findall(r"(\w+\s+\d{4})", text)
    start_date = _parse_date(dates[0]) if dates else date.today()
    end_date = _parse_date(dates[1]) if len(dates) > 1 else None
    return start_date, end_date


def _parse_experience(section: str) -> list[Experience]:
    """
    Parse work experience entries.

    Handles the Google Doc format:
        Company Name\tLocation
        Job Title\tDate Range - Date Range
        * Bullet point
        * Bullet point

        Next Company...
    """
    experiences: list[Experience] = []
    lines = [ln.strip() for ln in section.split("\n") if ln.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip lines that are just bullet points without a preceding header
        if line.startswith("*") or line.startswith("-"):
            i += 1
            continue

        # Line is a company/project name (no date pattern)
        has_date = bool(re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}", line))

        if not has_date:
            company = line
            company_clean = _clean_tab_suffix(company)
            i += 1

            # Next non-bullet line is the title + date range
            title = ""
            start_date = date.today()
            end_date = None
            description = []

            if i < len(lines) and not lines[i].startswith("*") and not lines[i].startswith("-"):
                title_line = lines[i]
                title_clean = _clean_tab_suffix(title_line)
                has_date_in_title = bool(re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}", title_line))

                if has_date_in_title:
                    # Title line contains the date range
                    title = re.sub(r"\s{2,}.*", "", title_line).strip() if "  " in title_line else _clean_tab_suffix(title_line.split("\t")[0])
                    start_date, end_date = _extract_dates(title_line)
                else:
                    title = title_clean

                i += 1

                # Collect bullet points
                while i < len(lines) and (lines[i].startswith("*") or lines[i].startswith("-")):
                    bp = lines[i].lstrip("* -").strip()
                    if bp:
                        description.append(bp)
                    i += 1
            else:
                # No title line — try to extract dates from company line
                start_date, end_date = _extract_dates(company)

            experiences.append(
                Experience(
                    company=company_clean,
                    title=title,
                    start_date=start_date,
                    end_date=end_date,
                    description=description,
                )
            )
        else:
            # Line starts with a date — might be a standalone experience or leftover
            i += 1

    return experiences


def _parse_education(section: str) -> list[Education]:
    """Parse education entries from section text."""
    education_list: list[Education] = []
    entries = re.split(r"\n(?=[A-Z][a-z]+)", section.strip())

    for entry in entries:
        lines = [ln.strip() for ln in entry.split("\n") if ln.strip()]
        if len(lines) < 2:
            continue

        # Clean tab-separated suffixes from institution and degree
        institution = _clean_tab_suffix(lines[0])
        degree_line = lines[1] if len(lines) > 1 else ""
        degree = _clean_tab_suffix(degree_line)

        # Try to extract graduation date from the degree line
        grad_date = _parse_date(degree_line.split("\t")[-1].strip()) if "\t" in degree_line else date.today()
        # Also check the full section for dates
        for ln in lines:
            d = re.findall(r"(\w+\s+\d{4})", ln)
            if d:
                grad_date = _parse_date(d[-1])

        education_list.append(
            Education(
                institution=institution,
                degree=degree,
                field_of_study=lines[2].lstrip("* ").strip() if len(lines) > 2 else "",
                graduation_date=grad_date,
            )
        )

    return education_list


def _parse_skills(section: str) -> list[Skill]:
    """Parse skills from section text."""
    skills: list[Skill] = []
    for line in section.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            category, items_str = line.split(":", 1)
            items = [i.strip() for i in items_str.split(",") if i.strip()]
            skills.append(Skill(category=category.strip(), items=items))
        elif line:
            skills.append(Skill(category="General", items=[line]))
    return skills


def _parse_projects(section: str) -> list[Project]:
    """Parse project entries from section text."""
    projects: list[Project] = []
    entries = re.split(
        r"\n(?=[A-Z][a-z]+[^,\n]*(?:\n|$))",
        section.strip(),
    )

    for entry in entries:
        lines = [ln.strip() for ln in entry.split("\n") if ln.strip()]
        if not lines:
            continue

        url = None
        for line in lines:
            url_match = re.search(r"(https?://[^\s]+)", line)
            if url_match:
                url = url_match.group(1)
                break

        # Second line is typically "Role        Date" — extract the role as personal_title
        personal_title = None
        if len(lines) > 1:
            second_line = lines[1]
            # Strip trailing date pattern like "    May 2026" or "January 2024 - May 2024"
            date_match = re.search(
                r"\s{2,}(?:\w+\s+\d{4}\s*(?:[-–]\s*\w+\s+\d{4})?)$",
                second_line,
            )
            if date_match:
                personal_title = second_line[: date_match.start()].strip()
            else:
                personal_title = second_line

        # Clean project name — remove tab-separated location suffix
        project_name = _clean_tab_suffix(lines[0])
        # Also handle "Name        Location" with multiple spaces
        project_name = re.sub(r"\s{2,}.*", "", project_name).strip()

        projects.append(
            Project(
                name=project_name,
                personal_title=personal_title,
                description=lines[2].lstrip("* ").strip() if len(lines) > 2 else "",
                technologies=(
                    lines[2].split(", ")
                    if len(lines) > 2 and not lines[2].startswith("*")
                    else (
                        lines[3].split(", ")
                        if len(lines) > 3 and not lines[3].startswith("*")
                        else []
                    )
                ),
                url=url,
            )
        )

    return projects


def _parse_certifications(section: str) -> list[str]:
    """Parse certification entries from section text."""
    certs = [line.strip() for line in section.strip().split("\n") if line.strip()]
    return certs


def _parse_date(date_str: str) -> date:
    """Parse a date string like 'January 2024' or 'Jan 2024'."""
    try:
        from dateutil import parser

        return parser.parse(date_str).date()
    except (ImportError, ValueError):
        try:
            from datetime import datetime

            return datetime.strptime(date_str, "%B %Y").date()
        except ValueError:
            try:
                return datetime.strptime(date_str, "%b %Y").date()
            except ValueError:
                return date.today()
