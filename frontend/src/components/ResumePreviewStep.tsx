import React, { useState } from 'react';
import {
  Download,
  Copy,
  Check,
  FileCode,
  FileText,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  TrendingUp,
  Cpu,
  Layers,
  Lightbulb,
  ExternalLink,
  RotateCcw,
  Wand2,
  RefreshCw,
  Sliders,
  CheckSquare,
  Briefcase,
} from 'lucide-react';
import { OptimizedResume } from '../types';
import { getPdfDownloadUrl, getTexDownloadUrl } from '../services/api';

interface ResumePreviewStepProps {
  optimized: OptimizedResume;
  onReset: () => void;
  onRegenerateWithInstructions: (instructions: string) => Promise<void>;
  onNavigateToStep: (step: 'job' | 'verification' | 'projects') => void;
  isRegenerating: boolean;
}

const QUICK_SUGGESTIONS = [
  '⚡ Emphasize C++ & Multithreading performance',
  '🎯 Make project bullet points more metric-driven with % and scale',
  '📝 Shorten Professional Summary to 2 impactful sentences',
  '💼 Highlight microservices architecture and API design',
  '🔧 Emphasize hands-on Docker and Kubernetes containerization',
];

export const ResumePreviewStep: React.FC<ResumePreviewStepProps> = ({
  optimized,
  onReset,
  onRegenerateWithInstructions,
  onNavigateToStep,
  isRegenerating,
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'latex' | 'enhancements'>('overview');
  const [copied, setCopied] = useState(false);
  const [customInstructions, setCustomInstructions] = useState('');

  const ats = optimized.ats_report;

  const handleCopyLatex = () => {
    navigator.clipboard.writeText(optimized.latex_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleApplyRefinement = () => {
    if (!customInstructions.trim()) return;
    onRegenerateWithInstructions(customInstructions.trim());
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (score >= 70) return 'text-brand-400 border-brand-500/30 bg-brand-500/10';
    if (score >= 50) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6">
      {/* Top Header & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 bg-slate-900/90 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-black text-white tracking-tight">
              Optimized ATS Resume
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Ready
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Targeting: <strong className="text-slate-200">{optimized.job_title}</strong> at{' '}
            <strong className="text-slate-200">{optimized.company_name}</strong>
          </p>
        </div>

        {/* Download Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <a
            href={getPdfDownloadUrl(optimized.resume_id)}
            download
            className="px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs shadow-lg shadow-brand-500/20 transition-all flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF</span>
          </a>

          <a
            href={getTexDownloadUrl(optimized.resume_id)}
            download
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 transition-all flex items-center space-x-2"
          >
            <FileCode className="w-4 h-4 text-brand-400" />
            <span>Download .TEX</span>
          </a>

          <button
            onClick={onReset}
            className="px-3 py-2.5 rounded-xl border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 text-xs transition-colors flex items-center space-x-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>New Role</span>
          </button>
        </div>
      </div>

      {/* Interactive AI Refinement & Custom Alterations Card */}
      <div className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-brand-950/20 to-slate-900 border border-brand-500/30 shadow-2xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3 mb-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-brand-500/20 border border-brand-500/40 flex items-center justify-center text-brand-300">
              <Wand2 className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white flex items-center space-x-2">
                <span>Refine, Alter, or Add Changes</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-brand-500/20 text-brand-300">
                  Interactive AI Iteration
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Want to alter bullet points, emphasize specific technologies, or tweak the tone? Instruct the AI to regenerate your resume.
              </p>
            </div>
          </div>

          {/* Quick jump to edit steps */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => onNavigateToStep('verification')}
              className="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700 flex items-center space-x-1 transition-colors"
            >
              <CheckSquare className="w-3.5 h-3.5 text-brand-400" />
              <span>Edit Skills</span>
            </button>
            <button
              onClick={() => onNavigateToStep('projects')}
              className="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700 flex items-center space-x-1 transition-colors"
            >
              <Sliders className="w-3.5 h-3.5 text-indigo-400" />
              <span>Edit Projects</span>
            </button>
          </div>
        </div>

        {/* Quick Suggestion Pills */}
        <div className="mb-3">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Quick Refinement Prompts:
          </span>
          <div className="flex flex-wrap gap-2">
            {QUICK_SUGGESTIONS.map((sug, sIdx) => (
              <button
                key={sIdx}
                type="button"
                onClick={() => setCustomInstructions(sug.replace(/^[^\w]+/, ''))}
                className="text-xs px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 transition-all text-left"
              >
                {sug}
              </button>
            ))}
          </div>
        </div>

        {/* Custom Instructions Input & Action */}
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            placeholder="Type your changes here... (e.g., 'Emphasize my C++ experience in JobFlow', 'Add bullet on reducing query latency', 'Make summary more concise')"
            value={customInstructions}
            onChange={(e) => setCustomInstructions(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && customInstructions.trim()) {
                handleApplyRefinement();
              }
            }}
            className="flex-1 px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
          />

          <button
            onClick={handleApplyRefinement}
            disabled={isRegenerating || !customInstructions.trim()}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-xs shadow-lg shadow-brand-500/20 transition-all flex items-center justify-center space-x-2"
          >
            {isRegenerating ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Applying Changes & Re-compiling...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Regenerate Resume with Changes</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-3 mb-6">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
            activeTab === 'overview'
              ? 'bg-brand-600 text-white shadow-md'
              : 'text-slate-400 hover:text-white bg-slate-900/60'
          }`}
        >
          <TrendingUp className="w-3.5 h-3.5" />
          <span>ATS Intelligence & Rebuilt Resume</span>
        </button>

        <button
          onClick={() => setActiveTab('latex')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
            activeTab === 'latex'
              ? 'bg-brand-600 text-white shadow-md'
              : 'text-slate-400 hover:text-white bg-slate-900/60'
          }`}
        >
          <FileCode className="w-3.5 h-3.5" />
          <span>LaTeX Source Code</span>
        </button>

        <button
          onClick={() => setActiveTab('enhancements')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
            activeTab === 'enhancements'
              ? 'bg-brand-600 text-white shadow-md'
              : 'text-slate-400 hover:text-white bg-slate-900/60'
          }`}
        >
          <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
          <span>
            Mode 2: Recommended Project Enhancements ({optimized.recommended_project_enhancements.length})
          </span>
        </button>
      </div>

      {/* TAB 1: OVERVIEW & ATS INTELLIGENCE */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          {/* ATS Scorecard Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className={`p-6 rounded-2xl border text-center ${getScoreColor(ats.overall_score)}`}>
              <span className="block text-4xl font-black">{ats.overall_score}%</span>
              <span className="text-xs font-bold uppercase tracking-wider mt-1 block">
                Overall Job Alignment
              </span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 text-center">
              <span className="block text-3xl font-extrabold text-white">
                {ats.required_keyword_coverage}%
              </span>
              <span className="text-xs text-slate-400 mt-1 block">Required Keyword Coverage</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 text-center">
              <span className="block text-3xl font-extrabold text-amber-400">
                {ats.preferred_keyword_coverage}%
              </span>
              <span className="text-xs text-slate-400 mt-1 block">Preferred Tech Coverage</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 text-center">
              <span className="block text-3xl font-extrabold text-emerald-400">
                {ats.ats_formatting_quality}%
              </span>
              <span className="text-xs text-slate-400 mt-1 block">ATS Parse Quality</span>
            </div>
          </div>

          {/* Recruiter Evaluation & Concerns */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2 mb-3">
                <ShieldAlert className="w-4 h-4 text-amber-400" />
                <span>Potential Recruiter Concerns</span>
              </h3>
              {ats.potential_recruiter_concerns.length > 0 ? (
                <ul className="space-y-2 text-xs text-slate-300">
                  {ats.potential_recruiter_concerns.map((c, i) => (
                    <li key={i} className="flex items-start space-x-2">
                      <span className="text-amber-400">•</span>
                      <span>{c}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-emerald-400">No major recruiter flags detected.</p>
              )}
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2 mb-3">
                <Sparkles className="w-4 h-4 text-brand-400" />
                <span>Recommended Improvements</span>
              </h3>
              <ul className="space-y-2 text-xs text-slate-300">
                {ats.recommended_improvements.map((rec, i) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-brand-400">→</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Rebuilt Resume Content Preview */}
          <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
            {/* Professional Summary */}
            <div className="border-b border-slate-800 pb-5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-brand-400 mb-2">
                Tailored Professional Summary
              </h3>
              <p className="text-sm text-slate-200 leading-relaxed font-sans">{optimized.summary}</p>
            </div>

            {/* Rebuilt Technical Skills */}
            <div className="border-b border-slate-800 pb-5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-brand-400 mb-3">
                Rebuilt Job-Specific Technical Skills
              </h3>
              <div className="space-y-2 text-xs">
                {Object.entries(optimized.rebuilt_skills).map(([category, skills]) => (
                  <div key={category} className="flex flex-col sm:flex-row sm:items-baseline">
                    <span className="w-48 font-bold text-slate-300 flex-shrink-0">{category}:</span>
                    <span className="text-slate-400">{skills.join(', ')}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Tailored Experience */}
            {optimized.experience && optimized.experience.length > 0 && (
              <div className="border-b border-slate-800 pb-5">
                <h3 className="text-xs font-bold uppercase tracking-wider text-brand-400 mb-4">
                  Tailored Professional Experience
                </h3>
                <div className="space-y-5">
                  {optimized.experience.map((exp, idx) => (
                    <div key={idx} className="space-y-1.5">
                      <div className="flex justify-between items-baseline">
                        <span className="font-bold text-white text-sm">
                          {exp.title} — <span className="text-slate-300 font-medium">{exp.company}</span>
                        </span>
                        <span className="text-xs text-slate-500">
                          {exp.start_date} - {exp.end_date || 'Present'}
                        </span>
                      </div>
                      <ul className="list-disc pl-5 space-y-1 text-xs text-slate-300">
                        {exp.bullet_points.map((b, bIdx) => (
                          <li key={bIdx}>{b}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tailored Technical Projects */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-brand-400 mb-4">
                Technical Projects (Google XYZ Action Formatted)
              </h3>
              <div className="space-y-5">
                {optimized.projects.map((proj, idx) => (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-white text-sm">{proj.name}</span>
                      {proj.technologies && proj.technologies.length > 0 && (
                        <span className="text-xs text-brand-300 font-mono">
                          | {proj.technologies.join(', ')}
                        </span>
                      )}
                    </div>
                    <ul className="list-disc pl-5 space-y-1 text-xs text-slate-300">
                      {proj.bullet_points.map((b, bIdx) => (
                        <li key={bIdx}>{b}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: LATEX CODE VIEWER */}
      {activeTab === 'latex' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div>
              <h3 className="text-sm font-bold text-white">Generated LaTeX Document</h3>
              <p className="text-xs text-slate-400">
                100% compliant with standard Tectonic / XeLaTeX / pdfLaTeX compilers.
              </p>
            </div>
            <button
              onClick={handleCopyLatex}
              className="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-300" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? 'Copied to Clipboard!' : 'Copy LaTeX'}</span>
            </button>
          </div>

          <pre className="p-6 rounded-2xl bg-slate-950 border border-slate-800 text-xs text-slate-300 font-mono overflow-x-auto max-h-[600px] leading-relaxed select-all">
            {optimized.latex_code}
          </pre>
        </div>
      )}

      {/* TAB 3: RECOMMENDED PROJECT ENHANCEMENTS (MODE 2) */}
      {activeTab === 'enhancements' && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex items-center space-x-2">
            <Lightbulb className="w-4 h-4 flex-shrink-0" />
            <span>
              <strong>Mode 2 Architecture Directive:</strong> These suggested features represent
              practical improvements you can implement to dramatically boost your competitive match for
              this role. They are kept strictly separate from your current resume claims.
            </span>
          </div>

          <div className="space-y-6">
            {optimized.recommended_project_enhancements.map((enh, idx) => (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl space-y-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 gap-2">
                  <h3 className="text-base font-bold text-white flex items-center space-x-2">
                    <span className="text-brand-400">Target Project:</span>
                    <span>{enh.project_name}</span>
                  </h3>
                  <div className="flex flex-wrap gap-1.5">
                    {enh.target_technologies.map((t) => (
                      <span
                        key={t}
                        className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-brand-500/10 text-brand-300 border border-brand-500/20"
                      >
                        +{t}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 block">
                    Suggested Practical Features:
                  </span>
                  <ul className="space-y-1.5 text-xs text-slate-300 pl-4 list-disc">
                    {enh.suggested_features.map((f, fIdx) => (
                      <li key={fIdx}>{f}</li>
                    ))}
                  </ul>
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 text-xs space-y-2">
                  <div>
                    <span className="font-bold text-brand-400">Architectural Recommendation: </span>
                    <span className="text-slate-300">{enh.architecture_recommendation}</span>
                  </div>
                  <div>
                    <span className="font-bold text-emerald-400">Recruiter Rationale: </span>
                    <span className="text-slate-400">{enh.business_impact_rationale}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
