import React from 'react';
import { Cpu, FileText, CheckCircle2, ShieldCheck, Sparkles } from 'lucide-react';
import { SystemStatus } from '../types';

interface HeaderProps {
  status: SystemStatus | null;
}

export const Header: React.FC<HeaderProps> = ({ status }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-white">
                ResumeForge <span className="text-brand-400">AI</span>
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase bg-brand-500/10 text-brand-400 border border-brand-500/20 rounded-full">
                v2.0 ATS Pro
              </span>
            </div>
            <p className="text-xs text-slate-400">Aggressive Job-Driven Resume Optimization & LaTeX Compiler</p>
          </div>
        </div>

        {/* Engine Status Badges */}
        <div className="flex items-center space-x-3">
          {status ? (
            <>
              <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1 bg-slate-900 border border-slate-800 rounded-lg text-xs">
                <Cpu className="w-3.5 h-3.5 text-brand-400" />
                <span className="text-slate-400">AI Engine:</span>
                <span className="font-medium text-slate-200">
                  {status.openai_configured ? status.openai_model || 'AI Model' : 'Local Engine'}
                </span>
                <span className="w-2 h-2 rounded-full bg-emerald-400 ml-1"></span>
              </div>

              <div className="flex items-center space-x-1.5 px-3 py-1 bg-slate-900 border border-slate-800 rounded-lg text-xs">
                <FileText className="w-3.5 h-3.5 text-indigo-400" />
                <span className="text-slate-400">Compiler:</span>
                <span className="font-medium text-slate-200">
                  {status.tectonic_available ? 'Tectonic LaTeX' : 'ATS Direct Engine'}
                </span>
                <span className="w-2 h-2 rounded-full bg-emerald-400 ml-1"></span>
              </div>
            </>
          ) : (
            <div className="text-xs text-slate-500 flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></div>
              <span>Connecting to Backend...</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

