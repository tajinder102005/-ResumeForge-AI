import React, { useState } from 'react';
import { Briefcase, Building, FileText, ArrowRight, Sparkles, RefreshCw, AlertCircle } from 'lucide-react';
import { analyzeJobDescription } from '../services/api';
import { JobDescriptionAnalysis, CandidateSkillVerificationItem } from '../types';

interface JobDescriptionStepProps {
  resumeId: string;
  companyName: string;
  jobTitle: string;
  jobDescription: string;
  onUpdateParams: (params: { companyName: string; jobTitle: string; jobDescription: string }) => void;
  onAnalysisSuccess: (analysis: JobDescriptionAnalysis, skills: CandidateSkillVerificationItem[]) => void;
  onProceed: () => void;
}

const SAMPLE_JD = `About the Role:
We are seeking a talented Senior Software Engineer to join our Core Platform Engineering team at FinTech Global. You will architect, build, and maintain high-throughput backend services and customer-facing interfaces powering mission-critical financial applications.

Core Responsibilities:
- Design and develop robust, highly available RESTful APIs and microservices using Python and FastAPI.
- Manage and optimize PostgreSQL relational databases, schema design, and Redis distributed caching for sub-millisecond latencies.
- Containerize services using Docker and orchestrate multi-node deployments with Kubernetes in Amazon Web Services (AWS).
- Build automated CI/CD deployment pipelines using GitHub Actions and implement thorough unit/integration tests with Pytest.
- Collaborate with frontend engineers using React and TypeScript on end-to-end features.
- Enforce strict security standards (OAuth2, JWT authentication, and OWASP compliance).

Requirements:
- 4+ years of professional software engineering experience with Python, FastAPI, or Django.
- Hands-on expertise with PostgreSQL, indexing, and Redis caching strategies.
- Strong knowledge of Docker, Kubernetes, and Cloud platforms (AWS / GCP).
- Proven track record with CI/CD automation, Git workflows, and Test-Driven Development (TDD).
- Solid foundation in Data Structures, Algorithms, and Distributed System Design.

Preferred Qualifications:
- Experience with Apache Kafka or RabbitMQ event-driven architectures.
- Experience with React, TypeScript, or modern frontend frameworks.
- Degree in Computer Science or equivalent practical engineering experience.`;

export const JobDescriptionStep: React.FC<JobDescriptionStepProps> = ({
  resumeId,
  companyName,
  jobTitle,
  jobDescription,
  onUpdateParams,
  onAnalysisSuccess,
  onProceed,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!jobDescription.trim()) {
      setError('Please paste a job description.');
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const data = await analyzeJobDescription({
        resume_id: resumeId,
        job_description: jobDescription,
        company_name: companyName,
        job_title: jobTitle,
      });
      onAnalysisSuccess(data.jd_analysis, data.skills_verification);
      onProceed();
    } catch (err: any) {
      setError(err.message || 'Error analyzing job description.');
    } finally {
      setLoading(false);
    }
  };

  const loadSample = () => {
    onUpdateParams({
      companyName: 'FinTech Global',
      jobTitle: 'Senior Software Engineer',
      jobDescription: SAMPLE_JD,
    });
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          Target Job Description
        </h1>
        <p className="mt-3 text-base text-slate-400 max-w-2xl mx-auto">
          The job description is your primary optimization target. ResumeForge AI will dissect the
          requirements, keywords, and technical domain qualifications.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
        <div className="flex justify-between items-center border-b border-slate-800 pb-4">
          <h2 className="text-base font-semibold text-white flex items-center space-x-2">
            <Briefcase className="w-4 h-4 text-brand-400" />
            <span>Target Role Specification</span>
          </h2>
          <button
            type="button"
            onClick={loadSample}
            className="text-xs text-brand-400 hover:text-brand-300 border border-brand-500/30 hover:border-brand-500/50 bg-brand-500/10 px-3 py-1.5 rounded-lg flex items-center space-x-1.5 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Load Sample Software Engineer JD</span>
          </button>
        </div>

        {/* Company & Title Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Target Company Name
            </label>
            <div className="relative">
              <Building className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="e.g. Google, Amazon, Stripe"
                value={companyName}
                onChange={(e) =>
                  onUpdateParams({ companyName: e.target.value, jobTitle, jobDescription })
                }
                className="w-full pl-10 pr-4 py-2.5 bg-slate-950/70 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Target Job Title
            </label>
            <div className="relative">
              <Briefcase className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="e.g. Senior Backend Engineer"
                value={jobTitle}
                onChange={(e) =>
                  onUpdateParams({ companyName, jobTitle: e.target.value, jobDescription })
                }
                className="w-full pl-10 pr-4 py-2.5 bg-slate-950/70 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors"
              />
            </div>
          </div>
        </div>

        {/* Job Description Textarea */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between">
            <span>Job Description Text</span>
            <span className="text-[11px] font-normal text-slate-500">
              {jobDescription.length} characters
            </span>
          </label>
          <textarea
            rows={12}
            placeholder="Paste the full job description here (Responsibilities, Requirements, Nice-to-haves, Tech Stack)..."
            value={jobDescription}
            onChange={(e) =>
              onUpdateParams({ companyName, jobTitle, jobDescription: e.target.value })
            }
            className="w-full p-4 bg-slate-950/70 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors resize-y leading-relaxed font-mono text-xs"
          ></textarea>
        </div>

        {/* CTA */}
        <div className="flex justify-end pt-2">
          <button
            onClick={handleAnalyze}
            disabled={loading || !jobDescription.trim()}
            className="px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold shadow-lg shadow-brand-500/20 transition-all flex items-center space-x-2"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Extracting 17 Keyword Categories...</span>
              </>
            ) : (
              <>
                <span>Extract & Analyze Keywords</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

