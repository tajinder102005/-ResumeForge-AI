export interface ContactInfo {
  name: string;
  email: string;
  phone: string;
  location: string;
  linkedin?: string | null;
  github?: string | null;
  leetcode?: string | null;
  website?: string | null;
}

export interface ExperienceItem {
  company: string;
  title: string;
  location?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  current?: boolean;
  bullet_points: string[];
}

export interface ProjectItem {
  name: string;
  description?: string | null;
  technologies: string[];
  bullet_points: string[];
  link?: string | null;
}

export interface EducationItem {
  institution: string;
  degree: string;
  field_of_study?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  gpa?: string | null;
  highlights?: string[];
}

export interface ExtractedResume {
  resume_id: string;
  filename: string;
  contact_info: ContactInfo;
  summary: string;
  skills: string[];
  experience: ExperienceItem[];
  education: EducationItem[];
  projects: ProjectItem[];
  raw_text: string;
}

export interface JobKeyword {
  name: string;
  category: string;
  importance: 'required' | 'preferred' | 'bonus';
  context?: string | null;
}

export interface CategorizedJobKeywords {
  programming_languages: JobKeyword[];
  frameworks_and_libraries: JobKeyword[];
  backend_technologies: JobKeyword[];
  frontend_technologies: JobKeyword[];
  databases: JobKeyword[];
  cloud_platforms: JobKeyword[];
  devops_and_infrastructure: JobKeyword[];
  data_structures_and_algorithms: JobKeyword[];
  system_design: JobKeyword[];
  distributed_systems: JobKeyword[];
  security_and_authentication: JobKeyword[];
  testing: JobKeyword[];
  development_tools: JobKeyword[];
  methodologies: JobKeyword[];
  required_qualifications: JobKeyword[];
  preferred_qualifications: JobKeyword[];
  domain_specific_terminology: JobKeyword[];
}

export interface JobDescriptionAnalysis {
  company_name?: string;
  job_title?: string;
  raw_job_description: string;
  target_role_level: string;
  categorized_keywords: CategorizedJobKeywords;
  total_keywords_count: number;
  top_critical_skills: string[];
}

export interface CandidateSkillVerificationItem {
  name: string;
  category: string;
  importance: 'required' | 'preferred' | 'bonus';
  status: 'supported' | 'missing' | 'confirmed' | 'rejected';
  proficiency?: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  practical_experience?: string;
  how_used?: string;
  evidence_in_resume?: string | null;
}

export interface ProjectEnhancementRecommendation {
  project_name: string;
  target_technologies: string[];
  suggested_features: string[];
  architecture_recommendation: string;
  business_impact_rationale: string;
}

export interface AtsReport {
  overall_score: number;
  required_keyword_coverage: number;
  preferred_keyword_coverage: number;
  confirmed_skills_coverage: number;
  matched_keywords: string[];
  missing_requirements: string[];
  project_relevance_score: number;
  ats_formatting_quality: number;
  potential_recruiter_concerns: string[];
  recommended_improvements: string[];
  disclaimer: string;
}

export interface OptimizedResume {
  resume_id: string;
  company_name: string;
  job_title: string;
  contact_info: ContactInfo;
  summary: string;
  rebuilt_skills: Record<string, string[]>;
  experience: ExperienceItem[];
  projects: ProjectItem[];
  education: EducationItem[];
  recommended_project_enhancements: ProjectEnhancementRecommendation[];
  ats_report: AtsReport;
  latex_code: string;
  pdf_generated: boolean;
  validation_status?: string | null;
}

export interface SystemStatus {
  status: string;
  openai_configured: boolean;
  ai_mode: string;
  openai_model: string;
  tectonic_available: boolean;
  tectonic_path?: string | null;
}

