import React, { useState } from 'react';
import {
  Layers,
  Sparkles,
  ArrowRight,
  Code,
  Lightbulb,
  CheckCircle2,
  Cpu,
  RefreshCw,
  Zap,
} from 'lucide-react';
import { ExtractedResume, CandidateSkillVerificationItem } from '../types';

interface ProjectEnhancementStepProps {
  resume: ExtractedResume;
  verifiedSkills: CandidateSkillVerificationItem[];
  projectNotes: Record<string, string>;
  optimizationMode: 'aggressive' | 'enhancement_only';
  onUpdateProjectNotes: (notes: Record<string, string>) => void;
  onUpdateMode: (mode: 'aggressive' | 'enhancement_only') => void;
  onGenerate: () => void;
  isGenerating: boolean;
}

export const ProjectEnhancementStep: React.FC<ProjectEnhancementStepProps> = ({
  resume,
  verifiedSkills,
  projectNotes,
  optimizationMode,
  onUpdateProjectNotes,
  onUpdateMode,
  onGenerate,
  isGenerating,
}) => {
  const handleNoteChange = (projectName: string, note: string) => {
    onUpdateProjectNotes({
      ...projectNotes,
      [projectName]: note,
    });
  };

  const confirmedSkills = verifiedSkills.filter(
    (s) => s.status === 'confirmed' || s.status === 'supported'
  );

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          Project Tailoring & Architectural Recommendations
        </h1>
        <p className="mt-3 text-base text-slate-400 max-w-2xl mx-auto">
          We rewrite your project descriptions using the Google XYZ action-impact formula,
          highlighting real technical architecture without fabricating.
        </p>
      </div>

      {/* Mode Selector */}
      <div className="mb-8 p-4 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-brand-400 block mb-1">
            Optimization Strategy
          </span>
          <p className="text-xs text-slate-400">
            Choose whether to maximize job keyword coverage on your resume or view recommended
            feature additions.
          </p>
        </div>

        <div className="flex items-center space-x-2 bg-slate-950 p-1 rounded-xl border border-slate-800 self-stretch sm:self-auto">
          <button
            type="button"
            onClick={() => onUpdateMode('aggressive')}
            className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center justify-center space-x-1.5 ${
              optimizationMode === 'aggressive'
                ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Zap className="w-3.5 h-3.5" />
            <span>Mode 1: Aggressive Resume Optimization</span>
          </button>

          <button
            type="button"
            onClick={() => onUpdateMode('enhancement_only')}
            className={`flex-1 sm:flex-none px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center justify-center space-x-1.5 ${
              optimizationMode === 'enhancement_only'
                ? 'bg-brand-600 text-white shadow-md shadow-brand-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Lightbulb className="w-3.5 h-3.5" />
            <span>Mode 2: Enhancement Recommendations</span>
          </button>
        </div>
      </div>

      {/* Projects List */}
      <div className="space-y-6 mb-8">
        {resume.projects.map((proj, idx) => {
          return (
            <div
              key={proj.name || idx}
              className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4 mb-4">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                    <Code className="w-4 h-4 text-brand-400" />
                    <span>{proj.name}</span>
                  </h3>
                  {proj.technologies && proj.technologies.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {proj.technologies.map((t) => (
                        <span
                          key={t}
                          className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="text-right">
                  <span className="text-[11px] px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-lg font-semibold">
                    Source Verified
                  </span>
                </div>
              </div>

              {/* Original Bullet Points */}
              <div className="mb-4">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 block">
                  Original Implementation Highlights:
                </span>
                <ul className="space-y-1.5 text-xs text-slate-300 pl-4 list-disc">
                  {proj.bullet_points.map((b, bIdx) => (
                    <li key={bIdx} className="leading-relaxed">
                      {b}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Candidate Clarifications & Notes Input */}
              <div className="mt-4 pt-4 border-t border-slate-800/80">
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center space-x-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-brand-400" />
                  <span>
                    Additional Technical Details or Metrics for this project (Optional)
                  </span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. Handled 5,000 req/sec, cut latency by 40%, used Redis pub/sub..."
                  value={projectNotes[proj.name] || ''}
                  onChange={(e) => handleNoteChange(proj.name, e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-600 focus:outline-none focus:border-brand-500"
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* CTA Button */}
      <div className="flex justify-end">
        <button
          onClick={onGenerate}
          disabled={isGenerating}
          className="px-8 py-4 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-bold text-base shadow-xl shadow-brand-500/25 transition-all flex items-center space-x-3 disabled:opacity-50"
        >
          {isGenerating ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" />
              <span>Synthesizing ATS Resume & Compiling LaTeX...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              <span>Generate Optimized Resume & LaTeX</span>
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};
