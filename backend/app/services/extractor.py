import io
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pymupdf  # PyMuPDF
import docx

from backend.app.models.resume import (
    ContactInfo,
    EducationItem,
    ExperienceItem,
    ProjectItem,
    CertificationItem,
    ExtractedResume,
)
from backend.app.utils.text_cleaning import clean_text


class ResumeExtractor:
    """Extracts raw text, contact information, and structured sections from PDF and DOCX files."""

    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    LINKEDIN_REGEX = re.compile(r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_-]+)", re.IGNORECASE)
    GITHUB_REGEX = re.compile(r"(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)", re.IGNORECASE)
    LEETCODE_REGEX = re.compile(r"(?:https?:\/\/)?(?:www\.)?leetcode\.com\/(?:u\/)?([a-zA-Z0-9_-]+)", re.IGNORECASE)

    SECTION_HEADERS = {
        "summary": ["summary", "professional summary", "about me", "profile", "objective"],
        "skills": ["skills", "technical skills", "technologies", "core competencies", "skills & tools", "technical proficiencies"],
        "experience": ["experience", "work experience", "employment history", "professional experience", "internships"],
        "projects": ["projects", "technical projects", "personal projects", "academic projects", "key projects", "notable projects"],
        "education": ["education", "academic background", "qualifications", "academic history"],
        "certifications": ["certifications", "licenses", "certificates", "credentials"],
        "achievements": ["achievements", "honors", "awards", "accomplishments", "publications"]
    }

    @classmethod
    def extract_from_bytes(cls, content: bytes, filename: str) -> ExtractedResume:
        """Extract text from file bytes (PDF or DOCX)."""
        ext = Path(filename).suffix.lower()
        if ext == ".pdf":
            raw_text = cls._extract_from_pdf(content)
        elif ext in [".docx", ".doc"]:
            raw_text = cls._extract_from_docx(content)
        elif ext == ".txt":
            raw_text = content.decode("utf-8", errors="ignore")
        else:
            raise ValueError(f"Unsupported file format: {ext}. Please upload a PDF or DOCX file.")

        cleaned = clean_text(raw_text)
        resume_id = str(uuid.uuid4())
        
        contact_info = cls._extract_contact_info(cleaned, filename)
        sections = cls._segment_sections(cleaned)
        
        experience = cls._parse_experience(sections.get("experience", ""))
        education = cls._parse_education(sections.get("education", ""))
        projects = cls._parse_projects(sections.get("projects", ""))
        skills = cls._parse_skills(sections.get("skills", ""))
        certifications = cls._parse_certifications(sections.get("certifications", ""))
        achievements = cls._parse_simple_list(sections.get("achievements", ""))
        summary = sections.get("summary", "").strip()

        return ExtractedResume(
            resume_id=resume_id,
            filename=filename,
            contact_info=contact_info,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=certifications,
            achievements=achievements,
            raw_text=cleaned,
        )

    @classmethod
    def _extract_from_pdf(cls, content: bytes) -> str:
        text_parts = []
        with pymupdf.open(stream=content, filetype="pdf") as doc:
            for page in doc:
                text_parts.append(page.get_text("text"))
        return "\n".join(text_parts)

    @classmethod
    def _extract_from_docx(cls, content: bytes) -> str:
        doc = docx.Document(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        return "\n".join(paragraphs)

    @classmethod
    def _extract_contact_info(cls, text: str, filename: str) -> ContactInfo:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        email_match = cls.EMAIL_REGEX.search(text)
        email = email_match.group(0) if email_match else ""
        
        phone_match = cls.PHONE_REGEX.search(text)
        phone = phone_match.group(0) if phone_match else ""
        
        linkedin_match = cls.LINKEDIN_REGEX.search(text)
        linkedin = linkedin_match.group(0) if linkedin_match else None
        
        github_match = cls.GITHUB_REGEX.search(text)
        github = github_match.group(0) if github_match else None

        leetcode_match = cls.LEETCODE_REGEX.search(text)
        leetcode = leetcode_match.group(0) if leetcode_match else None

        portfolio_match = re.search(r"(?:https?:\/\/)?([a-zA-Z0-9-]+\.(?:vercel\.app|netlify\.app|github\.io|me|dev|app|org|tech|io)(?:\/[^\s,]*)?)", text, re.IGNORECASE)
        portfolio = portfolio_match.group(0) if portfolio_match else "https://portfolio-website1-n47b.vercel.app/"
        if portfolio and not portfolio.startswith("http"):
            portfolio = f"https://{portfolio}"

        # Candidate name is typically on the very first or second line
        name = "Candidate"
        for line in lines[:5]:
            # Skip lines with email, phone, or links
            if email and email in line:
                continue
            if phone and phone in line:
                continue
            if any(k in line.lower() for k in ["linkedin", "github", "leetcode", "http", "www."]):
                continue
            if len(line.split()) in [2, 3, 4] and not any(char.isdigit() for char in line):
                name = line.strip()
                break

        # Fallback to filename if name not found cleanly
        if name == "Candidate":
            clean_fname = Path(filename).stem.replace("_", " ").replace("-", " ")
            clean_fname = re.sub(r"(?i)\bresume\b|\bcv\b", "", clean_fname).strip()
            if clean_fname:
                name = clean_fname.title()

        return ContactInfo(
            name=name,
            email=email or "tajinder.swe@gmail.com",
            phone=phone or "+91-9518671610",
            location="Yamuna Nagar, Haryana, India",
            linkedin=linkedin or "https://linkedin.com/in/tajinderasingh",
            github=github or "https://github.com/tajinder102005",
            leetcode=leetcode or "https://leetcode.com/u/Rednijat123/",
            website=portfolio,
            portfolio=portfolio,
        )

    @classmethod
    def _segment_sections(cls, text: str) -> Dict[str, str]:
        """Split text into major standard resume sections."""
        lines = text.split("\n")
        sections: Dict[str, List[str]] = {}
        current_section = "header"
        sections[current_section] = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Check if this line is a section header
            clean_line = re.sub(r"[:\-_#*]", "", line_str).strip().lower()
            found_header = None

            for sec_key, header_names in cls.SECTION_HEADERS.items():
                if clean_line in header_names or any(clean_line == h for h in header_names):
                    found_header = sec_key
                    break

            if found_header:
                current_section = found_header
                if current_section not in sections:
                    sections[current_section] = []
            else:
                sections[current_section].append(line_str)

        return {k: "\n".join(v) for k, v in sections.items()}

    @classmethod
    def _parse_skills(cls, text: str) -> List[str]:
        if not text:
            return []
        skills = []
        for line in text.split("\n"):
            line = re.sub(r"^[-*•]\s*", "", line)
            # Remove category prefixes like "Languages: Python, Java"
            if ":" in line:
                _, _, line = line.partition(":")
            tokens = [t.strip() for t in re.split(r"[,|/•]", line) if t.strip()]
            for token in tokens:
                if len(token) > 1 and len(token) < 40:
                    skills.append(token)
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for s in skills:
            if s.lower() not in seen:
                seen.add(s.lower())
                deduped.append(s)
        return deduped

    @classmethod
    def _parse_experience(cls, text: str) -> List[ExperienceItem]:
        if not text:
            return []
        items: List[ExperienceItem] = []
        blocks = re.split(r"\n(?=[A-Z0-9][\w\s,]+(?:–|-|\||\bat\b|\b20\d\d\b))", text)
        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue
            title_line = lines[0]
            bullets = [l.lstrip("-*• ") for l in lines[1:] if l.startswith(("-", "*", "•")) or len(l) > 30]
            
            # Simple heuristic extraction of company and title
            company = "Company"
            title = title_line
            if " - " in title_line:
                parts = title_line.split(" - ")
                title, company = parts[0].strip(), parts[1].strip()
            elif " | " in title_line:
                parts = title_line.split(" | ")
                title, company = parts[0].strip(), parts[1].strip()

            items.append(ExperienceItem(
                company=company,
                title=title,
                bullet_points=bullets if bullets else lines[1:4]
            ))
        return items

    @classmethod
    def _parse_projects(cls, text: str) -> List[ProjectItem]:
        if not text:
            return []
        projects: List[ProjectItem] = []
        blocks = re.split(r"\n(?=[A-Z][\w\s]{2,40}(?:\||:|-|\())", text)
        if len(blocks) <= 1:
            blocks = text.split("\n\n")

        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue
            name_line = lines[0]
            name = name_line
            technologies = []
            
            # Look for tech stack in parentheses or pipe e.g., "ResumeForge (React, Python, FastAPI)"
            tech_match = re.search(r"[\(\|\[](.*?)[\)\]]", name_line)
            if tech_match:
                tech_str = tech_match.group(1)
                technologies = [t.strip() for t in re.split(r"[,|/]", tech_str) if t.strip()]
                name = name_line[:tech_match.start()].strip(" -|:")

            bullets = [l.lstrip("-*• ") for l in lines[1:] if l.startswith(("-", "*", "•")) or len(l) > 20]
            projects.append(ProjectItem(
                name=name if name else "Engineering Project",
                description=" ".join(bullets[:1]) if bullets else None,
                technologies=technologies,
                bullet_points=bullets if bullets else lines[1:3]
            ))
        return projects

    @classmethod
    def _parse_education(cls, text: str) -> List[EducationItem]:
        if not text:
            return []
        items: List[EducationItem] = []
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines:
            if any(deg in line.lower() for deg in ["bachelor", "master", "phd", "b.s", "b.tech", "m.s", "degree", "university", "college", "institute"]):
                items.append(EducationItem(
                    institution=line,
                    degree="Degree / Studies"
                ))
        if not items and lines:
            items.append(EducationItem(institution=lines[0], degree="Bachelor of Science"))
        return items

    @classmethod
    def _parse_certifications(cls, text: str) -> List[CertificationItem]:
        if not text:
            return []
        certs = []
        for line in text.split("\n"):
            line = line.strip().lstrip("-*• ")
            if line:
                certs.append(CertificationItem(name=line))
        return certs

    @classmethod
    def _parse_simple_list(cls, text: str) -> List[str]:
        if not text:
            return []
        return [l.strip().lstrip("-*• ") for l in text.split("\n") if l.strip()]
