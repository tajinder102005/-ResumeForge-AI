from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from backend.app.models.resume import (
    ContactInfo,
    EducationItem,
    ExperienceItem,
    ProjectItem,
    CertificationItem,
)
from backend.app.models.job import CategorizedJobKeywords


class CandidateSkillVerificationItem(BaseModel):
    name: str
    category: str
    importance: Literal["required", "preferred", "bonus"] = "required"
    status: Literal["supported", "missing", "confirmed", "rejected"] = "missing"
    proficiency: Optional[Literal["beginner", "intermediate", "advanced", "expert"]] = "intermediate"
    practical_experience: Optional[str] = ""
    how_used: Optional[str] = ""
    evidence_in_resume: Optional[str] = None


class CandidateSkillConfirmationPayload(BaseModel):
    resume_id: str
    company_name: Optional[str] = ""
    job_title: Optional[str] = ""
    raw_job_description: str
    verified_skills: List[CandidateSkillVerificationItem]
    custom_skills: List[CandidateSkillVerificationItem] = Field(default_factory=list)
    project_notes: Dict[str, str] = Field(default_factory=dict)
    optimization_mode: Literal["aggressive", "enhancement_only"] = "aggressive"


class ProjectEnhancementRecommendation(BaseModel):
    project_name: str
    target_technologies: List[str]
    suggested_features: List[str]
    architecture_recommendation: str
    business_impact_rationale: str


class AtsReport(BaseModel):
    overall_score: float = Field(default=0.0, ge=0.0, le=100.0)
    required_keyword_coverage: float = Field(default=0.0, ge=0.0, le=100.0)
    preferred_keyword_coverage: float = Field(default=0.0, ge=0.0, le=100.0)
    confirmed_skills_coverage: float = Field(default=0.0, ge=0.0, le=100.0)
    matched_keywords: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    project_relevance_score: float = Field(default=0.0, ge=0.0, le=100.0)
    ats_formatting_quality: float = Field(default=95.0, ge=0.0, le=100.0)
    potential_recruiter_concerns: List[str] = Field(default_factory=list)
    recommended_improvements: List[str] = Field(default_factory=list)
    disclaimer: str = "ATS estimates are predictive and do not guarantee an interview or 100% universal parsing."


class OptimizedResume(BaseModel):
    resume_id: str
    company_name: str = ""
    job_title: str = ""
    contact_info: ContactInfo
    summary: str
    rebuilt_skills: Dict[str, List[str]] = Field(default_factory=dict)
    experience: List[ExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    recommended_project_enhancements: List[ProjectEnhancementRecommendation] = Field(default_factory=list)
    ats_report: AtsReport
    latex_code: str = ""
    pdf_generated: bool = False
    validation_status: Optional[str] = None
