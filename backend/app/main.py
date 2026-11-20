import logging
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.models.resume import ExtractedResume
from backend.app.models.job import JobDescriptionAnalysis
from backend.app.models.optimization import (
    CandidateSkillVerificationItem,
    CandidateSkillConfirmationPayload,
    OptimizedResume,
)
from backend.app.services.extractor import ResumeExtractor
from backend.app.services.jd_analyzer import JobDescriptionAnalyzer
from backend.app.services.resume_analyzer import ResumeAnalyzer
from backend.app.services.ai_service import AIService
from backend.app.services.compiler import LatexCompiler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("resumeforge")

app = FastAPI(
    title="ResumeForge AI API",
    description="Aggressive Job-Description-Driven ATS Resume Optimizer Engine",
    version="2.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session stores (per resume_id)
RESUME_STORE: Dict[str, ExtractedResume] = {}
JD_ANALYSIS_STORE: Dict[str, JobDescriptionAnalysis] = {}
OPTIMIZED_RESUME_STORE: Dict[str, OptimizedResume] = {}


class JobAnalysisRequest(BaseModel):
    resume_id: str
    job_description: str
    company_name: Optional[str] = ""
    job_title: Optional[str] = ""


class CompileRequest(BaseModel):
    resume_id: str
    latex_code: str


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ResumeForge AI Backend", "version": "2.0.0"}


@app.get("/api/status")
def system_status():
    tectonic_bin = LatexCompiler.find_tectonic()
    has_openai = bool(settings.OPENAI_API_KEY.strip())
    return {
        "status": "operational",
        "openai_configured": has_openai,
        "ai_mode": "OpenAI API" if has_openai else "Mock / Deterministic Local Engine",
        "openai_model": settings.OPENAI_MODEL if has_openai else "N/A",
        "tectonic_available": tectonic_bin is not None,
        "tectonic_path": tectonic_bin,
    }


@app.post("/api/resume/upload", response_model=ExtractedResume)
async def upload_resume(file: UploadFile = File(...)):
    """
    Accepts PDF or DOCX resume, extracts contact info, sections, skills, experience, and projects.
    """
    filename = file.filename or "uploaded_resume.pdf"
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        extracted = ResumeExtractor.extract_from_bytes(content, filename)
        RESUME_STORE[extracted.resume_id] = extracted
        logger.info(f"Successfully parsed resume: {extracted.resume_id} ({filename})")
        return extracted
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to parse resume file")
        raise HTTPException(status_code=500, detail=f"Failed to process resume file: {str(e)}")


@app.post("/api/jd/analyze")
def analyze_job_description(payload: JobAnalysisRequest):
    """
    Performs deep keyword extraction across 17 technical categories,
    then compares against the uploaded resume to identify Supported vs Missing skills.
    """
    resume = RESUME_STORE.get(payload.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found. Please upload your resume first.")

    if not payload.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    # Deep JD Analysis
    jd_analysis = JobDescriptionAnalyzer.analyze_job_description(
        job_description=payload.job_description,
        company_name=payload.company_name or "",
        job_title=payload.job_title or ""
    )
    JD_ANALYSIS_STORE[payload.resume_id] = jd_analysis

    # Skills comparison
    verification_items = ResumeAnalyzer.compare_skills_against_resume(
        resume=resume,
        jd_analysis=jd_analysis
    )

    return {
        "jd_analysis": jd_analysis,
        "skills_verification": verification_items,
        "resume_id": payload.resume_id,
    }


@app.post("/api/optimize", response_model=OptimizedResume)
def optimize_resume(payload: CandidateSkillConfirmationPayload):
    """
    Executes Aggressive Resume Optimization incorporating candidate-confirmed skills,
    deep project tailoring, and project enhancement recommendations.
    """
    resume = RESUME_STORE.get(payload.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found. Please upload your resume first.")

    jd_analysis = JD_ANALYSIS_STORE.get(payload.resume_id)
    if not jd_analysis:
        jd_analysis = JobDescriptionAnalyzer.analyze_job_description(
            job_description=payload.raw_job_description,
            company_name=payload.company_name or "",
            job_title=payload.job_title or ""
        )
        JD_ANALYSIS_STORE[payload.resume_id] = jd_analysis

    optimized = AIService.optimize_resume(
        resume=resume,
        jd_analysis=jd_analysis,
        payload=payload
    )
    OPTIMIZED_RESUME_STORE[payload.resume_id] = optimized
    return optimized


@app.post("/api/compile")
def compile_latex(req: CompileRequest):
    """
    Compiles LaTeX code into PDF and performs text validation.
    Updates the in-memory resume store so user edits persist.
    """
    optimized = OPTIMIZED_RESUME_STORE.get(req.resume_id)
    result = LatexCompiler.compile_latex(req.latex_code, req.resume_id, optimized)
    if not result["success"]:
        return JSONResponse(status_code=400, content=result)
    
    if optimized:
        optimized.latex_code = req.latex_code
        optimized.pdf_generated = True

    return {
        "success": True,
        "pdf_url": f"/api/download/pdf/{req.resume_id}",
        "tex_url": f"/api/download/tex/{req.resume_id}",
        "validation": result.get("validation"),
    }


@app.get("/api/view/pdf/{resume_id}")
async def view_pdf(resume_id: str):
    """
    Streams PDF directly for in-browser visual preview (inline display with no-cache headers).
    """
    pdf_path = settings.STORAGE_DIR / "pdfs" / f"{resume_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found. Please generate the resume first.")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/api/download/pdf/{resume_id}")
async def download_pdf(resume_id: str):
    """
    Downloads compiled PDF resume.
    """
    pdf_path = settings.STORAGE_DIR / "pdfs" / f"{resume_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found. Please generate the resume first.")

    return FileResponse(
        path=str(pdf_path),
        filename=f"ResumeForge_{resume_id[:8]}.pdf",
        media_type="application/pdf"
    )


@app.get("/api/download/tex/{resume_id}")
async def download_tex(resume_id: str):
    """
    Downloads raw LaTeX (.tex) resume.
    """
    tex_path = settings.STORAGE_DIR / "tex" / f"{resume_id}.tex"
    if not tex_path.exists():
        raise HTTPException(status_code=404, detail="LaTeX source file not found.")

    return FileResponse(
        path=str(tex_path),
        filename=f"ResumeForge_{resume_id[:8]}.tex",
        media_type="text/x-tex"
    )

# Mount Frontend static files for single-command full-stack execution
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


