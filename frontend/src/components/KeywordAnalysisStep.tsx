import React, { useState } from 'react';
import { ArrowRight, Layers, Tag, CheckCircle, Star, Filter, Sparkles } from 'lucide-react';
import { JobDescriptionAnalysis, JobKeyword } from '../types';

interface KeywordAnalysisStepProps {
  analysis: JobDescriptionAnalysis | null;
  onProceed: () => void;
}

export const KeywordAnalysisStep: React.FC<KeywordAnalysisStepProps> = ({
  analysis,
  onProceed,
}) => {
  const [activeCategory, setActiveCategory] = useState<string>('all');

  if (!analysis) {
    return (
      <div className="text-center py-12 text-slate-400">
        No job description analysis available. Please complete the previous step.
      </div>
    );
  }

  const categoryEntries: [string, JobKeyword[]][] = Object.entries(
    analysis.categorized_keywords
  );

  const formatCategoryName = (key: string) => {
    return key
      .split('_')
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ');
  };

  const allKeywords: JobKeyword[] = categoryEntries.flatMap(([_, list]) => list);
  const requiredCount = allKeywords.filter((k) => k.importance === 'required').length;
  const preferredCount = allKeywords.filter((k) => k.importance === 'preferred').length;

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          Deep Job Description Keyword Analysis
        </h1>
        <p className="mt-3 text-base text-slate-400 max-w-2xl mx-auto">
          Extracted {analysis.total_keywords_count} role keywords across 17 technical categories.
          Target Role Level: <span className="font-semibold text-brand-400">{analysis.target_role_level}</span>.
        </p>
      </div>

      {/* Highlights Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="block text-2xl font-extrabold text-white">{analysis.total_keywords_count}</span>
          <span className="text-xs text-slate-400">Total Keywords</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="block text-2xl font-extrabold text-rose-400">{requiredCount}</span>
          <span className="text-xs text-slate-400">Required Skills</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="block text-2xl font-extrabold text-amber-400">{preferredCount}</span>
          <span className="text-xs text-slate-400">Preferred Qualifications</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="block text-2xl font-extrabold text-brand-400">17</span>
          <span className="text-xs text-slate-400">Technical Categories</span>
        </div>
      </div>

      {/* Top Critical Skills Banner */}
      {analysis.top_critical_skills.length > 0 && (
        <div className="mb-8 p-5 rounded-2xl bg-gradient-to-r from-brand-950/70 via-slate-900 to-indigo-950/70 border border-brand-500/30">
          <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-brand-400 mb-3">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <span>Top Critical Skills Demanded by Role</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {analysis.top_critical_skills.map((skill) => (
              <span
                key={skill}
                className="px-3 py-1 bg-brand-500/20 border border-brand-500/40 text-brand-200 text-xs font-semibold rounded-lg shadow-sm"
              >
                ★ {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Category Tabs */}
      <div className="flex flex-wrap gap-1.5 border-b border-slate-800 pb-4 mb-6">
        <button
          onClick={() => setActiveCategory('all')}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            activeCategory === 'all'
              ? 'bg-brand-600 text-white shadow'
              : 'bg-slate-900 text-slate-400 hover:text-white'
          }`}
        >
          All Categories ({allKeywords.length})
        </button>
        {categoryEntries
          .filter(([_, list]) => list.length > 0)
          .map(([catKey, list]) => (
            <button
              key={catKey}
              onClick={() => setActiveCategory(catKey)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeCategory === catKey
                  ? 'bg-brand-600 text-white shadow'
                  : 'bg-slate-900 text-slate-400 hover:text-white'
              }`}
            >
              {formatCategoryName(catKey)} ({list.length})
            </button>
          ))}
      </div>

      {/* Keywords Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {categoryEntries
          .filter(([catKey, list]) => list.length > 0 && (activeCategory === 'all' || activeCategory === catKey))
          .map(([catKey, list]) => (
            <div
              key={catKey}
              className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-sm"
            >
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center justify-between border-b border-slate-800/60 pb-2">
                <span className="flex items-center space-x-2">
                  <Tag className="w-3.5 h-3.5 text-brand-400" />
                  <span>{formatCategoryName(catKey)}</span>
                </span>
                <span className="text-xs text-slate-500">{list.length} terms</span>
              </h3>

              <div className="flex flex-wrap gap-2">
                {list.map((kw) => (
                  <span
                    key={kw.name}
                    className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-medium border ${
                      kw.importance === 'required'
                        ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                        : kw.importance === 'preferred'
                        ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                        : 'bg-slate-800 border-slate-700 text-slate-300'
                    }`}
                  >
                    <span>{kw.name}</span>
                    <span
                      className={`text-[9px] uppercase px-1 py-0.2 rounded font-bold ${
                        kw.importance === 'required'
                          ? 'bg-rose-500/20 text-rose-300'
                          : kw.importance === 'preferred'
                          ? 'bg-amber-500/20 text-amber-300'
                          : 'bg-slate-700 text-slate-400'
                      }`}
                    >
                      {kw.importance}
                    </span>
                  </span>
                ))}
              </div>
            </div>
          ))}
      </div>

      {/* Proceed */}
      <div className="flex justify-end">
        <button
          onClick={onProceed}
          className="px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold shadow-lg shadow-brand-500/20 transition-all flex items-center space-x-2"
        >
          <span>Candidate Skills Verification</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

