import {
  ExtractedResume,
  JobDescriptionAnalysis,
  CandidateSkillVerificationItem,
  OptimizedResume,
  SystemStatus,
} from '../types';

const API_BASE = '';

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const res = await fetch(`${API_BASE}/api/status`);
  if (!res.ok) throw new Error('Failed to fetch system status');
  return res.json();
}

export async function uploadResume(file: File): Promise<ExtractedResume> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/resume/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload resume file.');
  }
  return res.json();
}

export async function analyzeJobDescription(params: {
  resume_id: string;
  job_description: string;
  company_name?: string;
  job_title?: string;
}): Promise<{
  jd_analysis: JobDescriptionAnalysis;
  skills_verification: CandidateSkillVerificationItem[];
  resume_id: string;
}> {
  const res = await fetch(`${API_BASE}/api/jd/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to analyze job description.');
  }
  return res.json();
}

export async function optimizeResume(params: {
  resume_id: string;
  company_name?: string;
  job_title?: string;
  raw_job_description: string;
  verified_skills: CandidateSkillVerificationItem[];
  custom_skills?: CandidateSkillVerificationItem[];
  project_notes?: Record<string, string>;
  optimization_mode?: 'aggressive' | 'enhancement_only';
  custom_instructions?: string;
}): Promise<OptimizedResume> {
  const res = await fetch(`${API_BASE}/api/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to optimize resume.');
  }
  return res.json();
}

export async function compileLatex(params: {
  resume_id: string;
  latex_code: string;
}): Promise<{
  success: boolean;
  pdf_url?: string;
  tex_url?: string;
  validation?: any;
  error?: string;
}> {
  const res = await fetch(`${API_BASE}/api/compile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  return res.json();
}

export function getPdfDownloadUrl(resume_id: string): string {
  return `${API_BASE}/api/download/pdf/${resume_id}`;
}

export function getPdfViewUrl(resume_id: string): string {
  return `${API_BASE}/api/view/pdf/${resume_id}`;
}

export function getTexDownloadUrl(resume_id: string): string {
  return `${API_BASE}/api/download/tex/${resume_id}`;
}

