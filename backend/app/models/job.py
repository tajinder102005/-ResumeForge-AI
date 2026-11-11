from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


class JobKeyword(BaseModel):
    name: str
    category: str
    importance: Literal["required", "preferred", "bonus"] = "required"
    context: Optional[str] = None


class CategorizedJobKeywords(BaseModel):
    programming_languages: List[JobKeyword] = Field(default_factory=list)
    frameworks_and_libraries: List[JobKeyword] = Field(default_factory=list)
    backend_technologies: List[JobKeyword] = Field(default_factory=list)
    frontend_technologies: List[JobKeyword] = Field(default_factory=list)
    databases: List[JobKeyword] = Field(default_factory=list)
    cloud_platforms: List[JobKeyword] = Field(default_factory=list)
    devops_and_infrastructure: List[JobKeyword] = Field(default_factory=list)
    data_structures_and_algorithms: List[JobKeyword] = Field(default_factory=list)
    system_design: List[JobKeyword] = Field(default_factory=list)
    distributed_systems: List[JobKeyword] = Field(default_factory=list)
    security_and_authentication: List[JobKeyword] = Field(default_factory=list)
    testing: List[JobKeyword] = Field(default_factory=list)
    development_tools: List[JobKeyword] = Field(default_factory=list)
    methodologies: List[JobKeyword] = Field(default_factory=list)
    required_qualifications: List[JobKeyword] = Field(default_factory=list)
    preferred_qualifications: List[JobKeyword] = Field(default_factory=list)
    domain_specific_terminology: List[JobKeyword] = Field(default_factory=list)


class JobDescriptionAnalysis(BaseModel):
    company_name: Optional[str] = ""
    job_title: Optional[str] = ""
    raw_job_description: str
    target_role_level: str = "Mid-Senior"
    categorized_keywords: CategorizedJobKeywords
    total_keywords_count: int = 0
    top_critical_skills: List[str] = Field(default_factory=list)
