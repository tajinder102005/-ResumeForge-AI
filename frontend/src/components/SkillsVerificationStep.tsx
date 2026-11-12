import React, { useState } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ArrowRight,
  Plus,
  ShieldCheck,
  Search,
  Filter,
} from 'lucide-react';
import { CandidateSkillVerificationItem } from '../types';

interface SkillsVerificationStepProps {
  skills: CandidateSkillVerificationItem[];
  onUpdateSkills: (updated: CandidateSkillVerificationItem[]) => void;
  onProceed: () => void;
}

export const SkillsVerificationStep: React.FC<SkillsVerificationStepProps> = ({
  skills,
  onUpdateSkills,
  onProceed,
}) => {
  const [filterTab, setFilterTab] = useState<'missing' | 'supported' | 'all'>('missing');
  const [searchTerm, setSearchTerm] = useState('');
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillCategory, setNewSkillCategory] = useState('Frameworks & Libraries');

  const updateSkill = (name: string, updates: Partial<CandidateSkillVerificationItem>) => {
    const next = skills.map((s) => (s.name === name ? { ...s, ...updates } : s));
    onUpdateSkills(next);
  };

  const handleAddCustomSkill = () => {
    if (!newSkillName.trim()) return;
    const exists = skills.some((s) => s.name.toLowerCase() === newSkillName.trim().toLowerCase());
    if (exists) return;

    const newItem: CandidateSkillVerificationItem = {
      name: newSkillName.trim(),
      category: newSkillCategory,
      importance: 'preferred',
      status: 'confirmed',
      proficiency: 'advanced',
      practical_experience: 'Candidate confirmed custom skill',
      how_used: '',
    };
    onUpdateSkills([newItem, ...skills]);
    setNewSkillName('');
  };

  const missingList = skills.filter((s) => s.status === 'missing');
  const supportedList = skills.filter((s) => s.status === 'supported');
  const confirmedList = skills.filter((s) => s.status === 'confirmed');
  const rejectedList = skills.filter((s) => s.status === 'rejected');

  const displayedList = skills.filter((s) => {
    const matchesSearch = s.name.toLowerCase().includes(searchTerm.toLowerCase());
    if (!matchesSearch) return false;

    if (filterTab === 'missing') {
      return s.status === 'missing' || s.status === 'confirmed' || s.status === 'rejected';
    }
    if (filterTab === 'supported') {
      return s.status === 'supported';
    }
    return true;
  });

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          Candidate Skills Verification
        </h1>
        <p className="mt-3 text-base text-slate-400 max-w-2xl mx-auto">
          Missing skills are not assumed unknown! Confirm any additional technologies you possess so
          ResumeForge AI can incorporate them into your new targeted resume without fabrication.
        </p>
      </div>

      {/* Summary Status Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="block text-xl font-bold text-emerald-400">{supportedList.length}</span>
          <span className="text-xs text-slate-400">Supported by Resume</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="block text-xl font-bold text-amber-400">{missingList.length}</span>
          <span className="text-xs text-slate-400">Needs Confirmation</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="block text-xl font-bold text-brand-400">{confirmedList.length}</span>
          <span className="text-xs text-slate-400">Newly Confirmed</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
          <span className="block text-xl font-bold text-rose-400">{rejectedList.length}</span>
          <span className="text-xs text-slate-400">Rejected (Don't Know)</span>
        </div>
      </div>

      {/* Controls Bar: Tabs & Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div className="flex items-center space-x-2 bg-slate-900 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setFilterTab('missing')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              filterTab === 'missing'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Needs Confirmation ({missingList.length + confirmedList.length + rejectedList.length})
          </button>
          <button
            onClick={() => setFilterTab('supported')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              filterTab === 'supported'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Already Supported ({supportedList.length})
          </button>
          <button
            onClick={() => setFilterTab('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              filterTab === 'all'
                ? 'bg-brand-500/20 text-brand-300 border border-brand-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            All Skills ({skills.length})
          </button>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search skill..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-950/70 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>
      </div>

      {/* Add Custom Skill Box */}
      <div className="mb-6 p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col sm:flex-row items-center gap-3">
        <div className="flex-1 flex gap-2 w-full">
          <input
            type="text"
            placeholder="Add unlisted skill (e.g., GraphQL, Celery, Terraform)..."
            value={newSkillName}
            onChange={(e) => setNewSkillName(e.target.value)}
            className="flex-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
          <select
            value={newSkillCategory}
            onChange={(e) => setNewSkillCategory(e.target.value)}
            className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-brand-500"
          >
            <option value="Languages">Languages</option>
            <option value="Frameworks & Libraries">Frameworks & Libraries</option>
            <option value="Backend & APIs">Backend & APIs</option>
            <option value="Cloud & DevOps">Cloud & DevOps</option>
            <option value="Databases & Storage">Databases & Storage</option>
            <option value="Testing & QA">Testing & QA</option>
            <option value="Tools & Methodologies">Tools & Methodologies</option>
          </select>
        </div>
        <button
          onClick={handleAddCustomSkill}
          disabled={!newSkillName.trim()}
          className="w-full sm:w-auto px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center justify-center space-x-1.5 transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Custom Skill</span>
        </button>
      </div>

      {/* Skills Card List */}
      <div className="space-y-3 mb-8">
        {displayedList.map((skill) => {
          const isSupported = skill.status === 'supported';
          const isConfirmed = skill.status === 'confirmed';
          const isRejected = skill.status === 'rejected';

          return (
            <div
              key={skill.name}
              className={`p-4 rounded-xl border transition-all ${
                isConfirmed
                  ? 'bg-brand-950/30 border-brand-500/40 shadow-sm'
                  : isSupported
                  ? 'bg-slate-900/60 border-slate-800'
                  : isRejected
                  ? 'bg-rose-950/20 border-rose-900/40 opacity-70'
                  : 'bg-slate-900/90 border-amber-500/30 shadow-md shadow-amber-500/5'
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="flex items-start space-x-3">
                  <div className="mt-0.5">
                    {isSupported ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    ) : isConfirmed ? (
                      <CheckCircle2 className="w-5 h-5 text-brand-400" />
                    ) : isRejected ? (
                      <XCircle className="w-5 h-5 text-rose-400" />
                    ) : (
                      <AlertTriangle className="w-5 h-5 text-amber-400 animate-pulse" />
                    )}
                  </div>

                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-white text-sm">{skill.name}</span>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${
                          skill.importance === 'required'
                            ? 'bg-rose-500/20 text-rose-300'
                            : 'bg-amber-500/20 text-amber-300'
                        }`}
                      >
                        {skill.importance}
                      </span>
                      <span className="text-xs text-slate-500">({skill.category})</span>
                    </div>

                    {isSupported && skill.evidence_in_resume && (
                      <p className="text-xs text-emerald-400/90 mt-1">
                        Resume Evidence: {skill.evidence_in_resume}
                      </p>
                    )}

                    {!isSupported && (
                      <p className="text-xs text-slate-400 mt-1">
                        {isConfirmed
                          ? '✓ Confirmed by candidate for inclusion in rebuilt skills section.'
                          : isRejected
                          ? '✗ Excluded from generated resume (truth-in-recruitment).'
                          : 'Not mentioned in original resume. Do you possess experience with this?'}
                      </p>
                    )}
                  </div>
                </div>

                {/* Interactive Toggles & Controls */}
                {!isSupported && (
                  <div className="flex items-center space-x-2 self-end md:self-center">
                    <button
                      type="button"
                      onClick={() => updateSkill(skill.name, { status: 'confirmed' })}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        isConfirmed
                          ? 'bg-brand-600 text-white shadow'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      Confirm I Know This
                    </button>

                    <button
                      type="button"
                      onClick={() => updateSkill(skill.name, { status: 'rejected' })}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        isRejected
                          ? 'bg-rose-600 text-white shadow'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>

              {/* Extra input fields when Confirmed */}
              {isConfirmed && !isSupported && (
                <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Proficiency Level</label>
                    <select
                      value={skill.proficiency || 'intermediate'}
                      onChange={(e) =>
                        updateSkill(skill.name, {
                          proficiency: e.target.value as any,
                        })
                      }
                      className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-white"
                    >
                      <option value="beginner">Beginner (Foundational)</option>
                      <option value="intermediate">Intermediate (Production Exposure)</option>
                      <option value="advanced">Advanced (Hands-on Expert)</option>
                      <option value="expert">Expert (Lead / Architect)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">
                      Practical Context / How You Used It
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Built redis cache layer, deployed k8s pods..."
                      value={skill.practical_experience || ''}
                      onChange={(e) =>
                        updateSkill(skill.name, {
                          practical_experience: e.target.value,
                          how_used: e.target.value,
                        })
                      }
                      className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-white placeholder-slate-600"
                    />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Proceed Button */}
      <div className="flex justify-end">
        <button
          onClick={onProceed}
          className="px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold shadow-lg shadow-brand-500/20 transition-all flex items-center space-x-2"
        >
          <span>Intelligent Project Tailoring</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

