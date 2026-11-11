import React from 'react';
import { Upload, Briefcase, Search, CheckSquare, Layers, FileDown } from 'lucide-react';

export type StepKey = 'upload' | 'job' | 'analysis' | 'verification' | 'projects' | 'result';

interface StepNavigationProps {
  currentStep: StepKey;
  onSelectStep: (step: StepKey) => void;
  canNavigateTo: (step: StepKey) => boolean;
}

const STEPS: { key: StepKey; label: string; icon: React.FC<{ className?: string }> }[] = [
  { key: 'upload', label: 'Resume Upload', icon: Upload },
  { key: 'job', label: 'Target Job', icon: Briefcase },
  { key: 'analysis', label: 'JD Keywords', icon: Search },
  { key: 'verification', label: 'Skills Verification', icon: CheckSquare },
  { key: 'projects', label: 'Project Tailoring', icon: Layers },
  { key: 'result', label: 'ATS Resume & PDF', icon: FileDown },
];

export const StepNavigation: React.FC<StepNavigationProps> = ({
  currentStep,
  onSelectStep,
  canNavigateTo,
}) => {
  return (
    <nav className="bg-slate-950/40 border-b border-slate-800/80 px-4 py-3 overflow-x-auto">
      <div className="max-w-6xl mx-auto flex items-center justify-between min-w-[680px]">
        {STEPS.map((step, idx) => {
          const Icon = step.icon;
          const isActive = currentStep === step.key;
          const isAllowed = canNavigateTo(step.key);

          return (
            <React.Fragment key={step.key}>
              <button
                disabled={!isAllowed}
                onClick={() => onSelectStep(step.key)}
                className={`flex items-center space-x-2.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-brand-500 text-white shadow-md shadow-brand-500/25 ring-2 ring-brand-400/30'
                    : isAllowed
                    ? 'text-slate-300 hover:text-white hover:bg-slate-800/80'
                    : 'text-slate-600 cursor-not-allowed'
                }`}
              >
                <div
                  className={`w-6 h-6 rounded-lg flex items-center justify-center text-[11px] font-bold ${
                    isActive
                      ? 'bg-white/20 text-white'
                      : isAllowed
                      ? 'bg-slate-800 text-slate-300'
                      : 'bg-slate-900 text-slate-700'
                  }`}
                >
                  {idx + 1}
                </div>
                <span>{step.label}</span>
              </button>

              {idx < STEPS.length - 1 && (
                <div className="flex-1 h-[1px] mx-2 bg-slate-800 max-w-[40px]"></div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </nav>
  );
};
