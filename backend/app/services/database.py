import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.app.config import settings
from backend.app.models.resume import ExtractedResume
from backend.app.models.job import JobDescriptionAnalysis
from backend.app.models.optimization import OptimizedResume

logger = logging.getLogger("resumeforge.db")


class DatabaseService:
    """
    Persistent SQLite storage layer for ResumeForge AI.
    Saves extracted resumes, job descriptions, tailored resumes, and version history.
    """

    DB_PATH: Path = settings.STORAGE_DIR / "db" / "resumeforge.db"

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(cls.DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls):
        """Initializes database schema with indexing and foreign keys."""
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS resumes (
                        resume_id TEXT PRIMARY KEY,
                        filename TEXT,
                        candidate_name TEXT,
                        email TEXT,
                        phone TEXT,
                        raw_data JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS job_analyses (
                        resume_id TEXT PRIMARY KEY,
                        company_name TEXT,
                        job_title TEXT,
                        raw_data JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS optimized_resumes (
                        resume_id TEXT PRIMARY KEY,
                        company_name TEXT,
                        job_title TEXT,
                        template_name TEXT DEFAULT 'modern',
                        summary TEXT,
                        ats_score REAL,
                        latex_code TEXT,
                        raw_data JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                logger.info("Database schema verified and operational.")
        except Exception as e:
            logger.exception(f"Failed to initialize database: {e}")

    @classmethod
    def save_extracted_resume(cls, resume: ExtractedResume, filename: str):
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                data_json = resume.model_dump_json()
                cursor.execute("""
                    INSERT INTO resumes (resume_id, filename, candidate_name, email, phone, raw_data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(resume_id) DO UPDATE SET
                        filename=excluded.filename,
                        candidate_name=excluded.candidate_name,
                        email=excluded.email,
                        phone=excluded.phone,
                        raw_data=excluded.raw_data,
                        updated_at=CURRENT_TIMESTAMP;
                """, (
                    resume.resume_id,
                    filename,
                    resume.contact_info.name,
                    resume.contact_info.email,
                    resume.contact_info.phone,
                    data_json
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist extracted resume: {e}")

    @classmethod
    def get_extracted_resume(cls, resume_id: str) -> Optional[ExtractedResume]:
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT raw_data FROM resumes WHERE resume_id = ?", (resume_id,))
                row = cursor.fetchone()
                if row and row["raw_data"]:
                    return ExtractedResume.model_validate_json(row["raw_data"])
        except Exception as e:
            logger.error(f"Failed to retrieve extracted resume: {e}")
        return None

    @classmethod
    def save_jd_analysis(cls, resume_id: str, jd: JobDescriptionAnalysis):
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO job_analyses (resume_id, company_name, job_title, raw_data)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(resume_id) DO UPDATE SET
                        company_name=excluded.company_name,
                        job_title=excluded.job_title,
                        raw_data=excluded.raw_data;
                """, (
                    resume_id,
                    jd.company_name or "",
                    jd.job_title or "",
                    jd.model_dump_json()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist JD analysis: {e}")

    @classmethod
    def get_jd_analysis(cls, resume_id: str) -> Optional[JobDescriptionAnalysis]:
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT raw_data FROM job_analyses WHERE resume_id = ?", (resume_id,))
                row = cursor.fetchone()
                if row and row["raw_data"]:
                    return JobDescriptionAnalysis.model_validate_json(row["raw_data"])
        except Exception as e:
            logger.error(f"Failed to retrieve JD analysis: {e}")
        return None

    @classmethod
    def save_optimized_resume(cls, opt: OptimizedResume, template_name: str = "modern"):
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                score = opt.ats_report.overall_score if opt.ats_report else 0.0
                cursor.execute("""
                    INSERT INTO optimized_resumes (
                        resume_id, company_name, job_title, template_name,
                        summary, ats_score, latex_code, raw_data, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(resume_id) DO UPDATE SET
                        company_name=excluded.company_name,
                        job_title=excluded.job_title,
                        template_name=excluded.template_name,
                        summary=excluded.summary,
                        ats_score=excluded.ats_score,
                        latex_code=excluded.latex_code,
                        raw_data=excluded.raw_data,
                        updated_at=CURRENT_TIMESTAMP;
                """, (
                    opt.resume_id,
                    opt.company_name or "",
                    opt.job_title or "",
                    template_name,
                    opt.summary or "",
                    score,
                    opt.latex_code or "",
                    opt.model_dump_json()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist optimized resume: {e}")

    @classmethod
    def get_optimized_resume(cls, resume_id: str) -> Optional[OptimizedResume]:
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT raw_data FROM optimized_resumes WHERE resume_id = ?", (resume_id,))
                row = cursor.fetchone()
                if row and row["raw_data"]:
                    return OptimizedResume.model_validate_json(row["raw_data"])
        except Exception as e:
            logger.error(f"Failed to retrieve optimized resume: {e}")
        return None

    @classmethod
    def list_history(cls, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns recent application optimization history."""
        results = []
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        COALESCE(o.resume_id, r.resume_id) AS resume_id,
                        COALESCE(r.candidate_name, json_extract(o.raw_data, '$.contact_info.name'), 'Candidate') AS candidate_name,
                        COALESCE(r.filename, 'resume.pdf') AS filename,
                        COALESCE(o.company_name, 'Target Organization') AS company_name,
                        COALESCE(o.job_title, 'Software Engineer') AS job_title,
                        COALESCE(o.ats_score, 0.0) AS ats_score,
                        COALESCE(o.template_name, 'modern') AS template_name,
                        COALESCE(o.updated_at, r.created_at, '') AS updated_at
                    FROM optimized_resumes o
                    LEFT JOIN resumes r ON o.resume_id = r.resume_id
                    UNION
                    SELECT 
                        r.resume_id,
                        COALESCE(r.candidate_name, 'Candidate') AS candidate_name,
                        COALESCE(r.filename, 'resume.pdf') AS filename,
                        'Target Organization' AS company_name,
                        'Software Engineer' AS job_title,
                        0.0 AS ats_score,
                        'modern' AS template_name,
                        COALESCE(r.updated_at, r.created_at, '') AS updated_at
                    FROM resumes r
                    WHERE r.resume_id NOT IN (SELECT resume_id FROM optimized_resumes)
                    ORDER BY updated_at DESC
                    LIMIT ?;
                """, (limit,))
                for row in cursor.fetchall():
                    results.append({
                        "resume_id": row["resume_id"],
                        "candidate_name": row["candidate_name"] or "Candidate",
                        "filename": row["filename"] or "resume.pdf",
                        "company_name": row["company_name"] or "Target Organization",
                        "job_title": row["job_title"] or "Software Engineer",
                        "ats_score": row["ats_score"] if row["ats_score"] is not None else 0.0,
                        "template_name": row["template_name"] or "modern",
                        "updated_at": row["updated_at"] or ""
                    })
        except Exception as e:
            logger.error(f"Failed to list history: {e}")
        return results

    @classmethod
    def delete_history_entry(cls, resume_id: str) -> bool:
        """Deletes a resume and associated data from persistent storage."""
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM resumes WHERE resume_id = ?", (resume_id,))
                cursor.execute("DELETE FROM job_analyses WHERE resume_id = ?", (resume_id,))
                cursor.execute("DELETE FROM optimized_resumes WHERE resume_id = ?", (resume_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to delete history entry: {e}")
            return False
