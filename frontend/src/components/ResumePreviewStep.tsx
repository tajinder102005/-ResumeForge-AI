import React, { useState, useEffect } from 'react';
import {
  Download,
  Copy,
  Check,
  FileCode,
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
  Eye,
  Mail,
  Phone,
  Linkedin,
  Github,
  Code2,
  Play,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Palette,
  Camera,
  Image as ImageIcon,
  User,
} from 'lucide-react';
import { OptimizedResume } from '../types';
import { getPdfDownloadUrl, getPdfViewUrl, getTexDownloadUrl, getDocxDownloadUrl, compileLatex, switchTemplate, uploadPhoto } from '../services/api';

interface ResumePreviewStepProps {
  optimized: OptimizedResume;
  onReset: () => void;
  onRegenerateWithInstructions: (instructions: string) => Promise<void>;
  onNavigateToStep: (step: 'job' | 'verification' | 'projects') => void;
  isRegenerating: boolean;
}

const QUICK_SUGGESTIONS = [
  '⚡ Emphasize C# and SQL distributed systems performance',
  '🎯 Keep strictly to 1 page with 3 bullets per project',
  '📝 Shorten Professional Summary to 2 high-impact sentences',
  '💼 Highlight microservices architecture, REST APIs, and Kafka',
  '🔧 Emphasize hands-on Docker, Kubernetes, and CI/CD pipelines',
  '🔗 Update LinkedIn, GitHub, and LeetCode in contact line',
];

export const ResumePreviewStep: React.FC<ResumePreviewStepProps> = ({
  optimized,
  onReset,
  onRegenerateWithInstructions,
  onNavigateToStep,
  isRegenerating,
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'latex' | 'overview' | 'enhancements'>('preview');
  const [copied, setCopied] = useState(false);
  const [customInstructions, setCustomInstructions] = useState('');
  
  // LaTeX Editor & Compilation States
  const [editableLatex, setEditableLatex] = useState(optimized.latex_code);
  const [isCompilingLatex, setIsCompilingLatex] = useState(false);
  const [compileError, setCompileError] = useState<string | null>(null);
  const [compileSuccess, setCompileSuccess] = useState<string | null>(null);
  const [pdfTimestamp, setPdfTimestamp] = useState<number>(Date.now());

  useEffect(() => {
    setEditableLatex(optimized.latex_code);
    setPdfTimestamp(Date.now());
  }, [optimized.latex_code, optimized.resume_id]);

  const ats = optimized.ats_report;
  const contact = optimized.contact_info;

  const handleCopyLatex = () => {
    navigator.clipboard.writeText(editableLatex);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const [selectedTemplate, setSelectedTemplate] = useState<string>('modern');
  const [isSwitchingTemplate, setIsSwitchingTemplate] = useState(false);
  const [isUploadingPhoto, setIsUploadingPhoto] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);

  const handleTemplateSwitch = async (tpl: string) => {
    if (tpl === selectedTemplate || isSwitchingTemplate) return;
    setIsSwitchingTemplate(true);
    setCompileError(null);
    setCompileSuccess(null);
    try {
      const res = await switchTemplate({
        resume_id: optimized.resume_id,
        template_name: tpl,
      });
      if (res.success) {
        setSelectedTemplate(tpl);
        setEditableLatex(res.latex_code);
        optimized.latex_code = res.latex_code;
        setPdfTimestamp(Date.now());
        setCompileSuccess(`Switched to ${tpl.toUpperCase().replace('_', ' ')} layout and compiled successfully!`);
        setActiveTab('preview');
      } else {
        setCompileError(res.error || 'Failed to switch template.');
      }
    } catch (err: any) {
      setCompileError(err.message || 'Error switching template.');
    } finally {
      setIsSwitchingTemplate(false);
    }
  };

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsUploadingPhoto(true);
    setCompileError(null);
    setCompileSuccess(null);
    try {
      const res = await uploadPhoto(optimized.resume_id, file);
      if (res.success && res.latex_code) {
        setSelectedTemplate('sidebar_photo');
        setEditableLatex(res.latex_code);
        optimized.latex_code = res.latex_code;
        setPdfTimestamp(Date.now());
        setCompileSuccess('Photo uploaded successfully! Recompiled with Executive Sidebar theme.');
        setActiveTab('preview');
      } else {
        setCompileError(res.error || 'Failed to upload photo.');
      }
    } catch (err: any) {
      setCompileError(err.message || 'Error uploading photo.');
    } finally {
      setIsUploadingPhoto(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleApplyRefinement = () => {
    if (!customInstructions.trim()) return;
    onRegenerateWithInstructions(customInstructions.trim());
  };

  const handleRecompileLatex = async () => {
    if (!editableLatex.trim()) return;
    setIsCompilingLatex(true);
    setCompileError(null);
    setCompileSuccess(null);

    try {
      const res = await compileLatex({
        resume_id: optimized.resume_id,
        latex_code: editableLatex,
      });

      if (res.success) {
        optimized.latex_code = editableLatex;
        setPdfTimestamp(Date.now());
        setCompileSuccess('LaTeX recompiled successfully! Live PDF document has been updated.');
        // Switch to preview tab so user instantly sees the newly compiled result
        setActiveTab('preview');
      } else {
        setCompileError(res.error || 'Compilation failed. Please inspect LaTeX code syntax.');
      }
    } catch (err: any) {
      setCompileError(err.message || 'Failed to connect to compilation service.');
    } finally {
      setIsCompilingLatex(false);
    }
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
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 bg-slate-900/90 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-black text-white tracking-tight">
              Optimized ATS Resume
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              1-Page Compliant
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Targeting: <strong className="text-slate-200">{optimized.job_title}</strong> at{' '}
            <strong className="text-slate-200">{optimized.company_name}</strong>
          </p>

          {/* Active Contact Links Banner */}
          <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-slate-800/80 text-xs text-slate-300">
            {contact.email && (
              <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md bg-slate-800 border border-slate-700/60">
                <Mail className="w-3 h-3 text-brand-400" />
                <span>{contact.email}</span>
              </span>
            )}
            {contact.phone && (
              <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md bg-slate-800 border border-slate-700/60">
                <Phone className="w-3 h-3 text-brand-400" />
                <span>{contact.phone}</span>
              </span>
            )}
            {contact.linkedin && (
              <a
                href={contact.linkedin}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md bg-blue-950/40 text-blue-300 border border-blue-800/50 hover:bg-blue-900/40 transition-colors"
              >
                <Linkedin className="w-3 h-3 text-blue-400" />
                <span>LinkedIn</span>
              </a>
            )}
            {contact.github && (
              <a
                href={contact.github}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md bg-slate-800 text-purple-300 border border-purple-800/50 hover:bg-slate-700 transition-colors"
              >
                <Github className="w-3 h-3 text-purple-400" />
                <span>GitHub</span>
              </a>
            )}
            {contact.leetcode && (
              <a
                href={contact.leetcode}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md bg-amber-950/40 text-amber-300 border border-amber-800/50 hover:bg-amber-900/40 transition-colors"
              >
                <Code2 className="w-3 h-3 text-amber-400" />
                <span>LeetCode</span>
              </a>
            )}
          </div>
        </div>

        {/* Action Buttons */}
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
            href={getDocxDownloadUrl(optimized.resume_id)}
            download
            className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-lg shadow-emerald-500/20 transition-all flex items-center space-x-2"
          >
            <FileText className="w-4 h-4" />
            <span>Download .DOCX</span>
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
      <div className="mb-6 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-brand-950/20 to-slate-900 border border-brand-500/30 shadow-2xl">
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
                Provide instructions to re-optimize with the AI, or directly edit LaTeX markup in the LaTeX Editor tab.
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
            placeholder="Type instructions here... (e.g. 'Shorten summary to 2 lines', 'Add microservices latency metrics', 'Focus on C# and SQL')"
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
                <span>Regenerating with Groq 120B...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Regenerate Resume with AI</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Template Theme Switcher & Headshot Upload Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 mb-4 p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div className="flex items-center space-x-2.5">
          <Palette className="w-4 h-4 text-brand-400" />
          <div>
            <span className="text-xs font-bold text-white block">Visual Themes & Formatting:</span>
            <span className="text-[11px] text-slate-400">High-contrast, colorful ATS layouts & 2-column headshot</span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Modern Minimalist */}
          <button
            onClick={() => handleTemplateSwitch('modern')}
            disabled={isSwitchingTemplate}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
              selectedTemplate === 'modern'
                ? 'bg-slate-700 text-white shadow-md ring-2 ring-slate-400'
                : 'bg-slate-800/80 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700/60'
            }`}
          >
            <span className="w-2.5 h-2.5 rounded-full bg-slate-300 inline-block shadow-sm" />
            <span>Minimalist</span>
          </button>

          {/* Golden & Onyx Luxury */}
          <button
            onClick={() => handleTemplateSwitch('gold')}
            disabled={isSwitchingTemplate}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
              selectedTemplate === 'gold' || selectedTemplate === 'golden'
                ? 'bg-amber-950/80 text-amber-200 shadow-md ring-2 ring-amber-500 border border-amber-500/50'
                : 'bg-slate-800/80 text-amber-300/80 hover:text-amber-200 hover:bg-amber-950/40 border border-amber-900/40'
            }`}
          >
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block shadow-sm shadow-amber-400/50" />
            <span>Golden & Onyx</span>
          </button>

          {/* Navy Blue Banner (Rohan Malhotra Style) */}
          <button
            onClick={() => handleTemplateSwitch('navy')}
            disabled={isSwitchingTemplate}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
              selectedTemplate === 'navy' || selectedTemplate === 'navy_blue'
                ? 'bg-blue-950/90 text-blue-200 shadow-md ring-2 ring-blue-500 border border-blue-500/50'
                : 'bg-slate-800/80 text-blue-300/80 hover:text-blue-200 hover:bg-blue-950/40 border border-blue-900/40'
            }`}
          >
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block shadow-sm shadow-blue-500/50" />
            <span>Navy Banner</span>
          </button>

          {/* Emerald Modern */}
          <button
            onClick={() => handleTemplateSwitch('emerald')}
            disabled={isSwitchingTemplate}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
              selectedTemplate === 'emerald'
                ? 'bg-emerald-950/90 text-emerald-200 shadow-md ring-2 ring-emerald-500 border border-emerald-500/50'
                : 'bg-slate-800/80 text-emerald-300/80 hover:text-emerald-200 hover:bg-emerald-950/40 border border-emerald-900/40'
            }`}
          >
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block shadow-sm shadow-emerald-400/50" />
            <span>Emerald Modern</span>
          </button>

          {/* Classic Ivy */}
          <button
            onClick={() => handleTemplateSwitch('classic')}
            disabled={isSwitchingTemplate}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
              selectedTemplate === 'classic'
                ? 'bg-stone-700 text-white shadow-md ring-2 ring-stone-400'
                : 'bg-slate-800/80 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700/60'
            }`}
          >
            <span className="w-2.5 h-2.5 rounded-full bg-stone-300 inline-block" />
            <span>Classic Ivy</span>
          </button>

          {/* Executive 2-Column Sidebar + Photo */}
          <button
            onClick={() => handleTemplateSwitch('sidebar_photo')}
            disabled={isSwitchingTemplate}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
              selectedTemplate === 'sidebar_photo' || selectedTemplate === 'sidebar'
                ? 'bg-indigo-600 text-white shadow-md ring-2 ring-indigo-400'
                : 'bg-slate-800/80 text-indigo-300 hover:text-white hover:bg-indigo-950/60 border border-indigo-800/50'
            }`}
          >
            <User className="w-3.5 h-3.5 text-indigo-300" />
            <span>Sidebar + Photo</span>
          </button>

          {/* Upload Headshot Button */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handlePhotoUpload}
            accept="image/png, image/jpeg, image/jpg"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploadingPhoto}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white shadow-md shadow-purple-500/20 flex items-center space-x-1.5 transition-all"
            title="Upload headshot to embed directly in the resume"
          >
            {isUploadingPhoto ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <Camera className="w-3.5 h-3.5" />
                <span>Upload Photo</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-3 mb-6">
        <button
          onClick={() => setActiveTab('preview')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
            activeTab === 'preview'
              ? 'bg-brand-600 text-white shadow-md'
              : 'text-slate-400 hover:text-white bg-slate-900/60'
          }`}
        >
          <Eye className="w-3.5 h-3.5" />
          <span>Live Document (PDF Preview)</span>
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
          <span>Editable LaTeX & Compiler</span>
        </button>

        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center space-x-2 ${
            activeTab === 'overview'
              ? 'bg-brand-600 text-white shadow-md'
              : 'text-slate-400 hover:text-white bg-slate-900/60'
          }`}
        >
          <TrendingUp className="w-3.5 h-3.5" />
          <span>ATS Intelligence Report</span>
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
            Mode 2: Recommended Enhancements ({optimized.recommended_project_enhancements.length})
          </span>
        </button>
      </div>

      {/* TAB 0: LIVE DOCUMENT PDF PREVIEW */}
      {activeTab === 'preview' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
            <div className="flex items-center space-x-2">
              <Eye className="w-4 h-4 text-brand-400" />
              <span className="text-xs font-bold text-white">
                Live Document Preview (Rendered 1-Page ATS PDF)
              </span>
              <span className="text-[11px] text-slate-400">
                — Inspect layout, line heights, and exact formatting.
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setActiveTab('latex')}
                className="px-3 py-1.5 rounded-lg bg-indigo-950/60 hover:bg-indigo-900/60 text-indigo-300 text-xs border border-indigo-700/50 flex items-center space-x-1.5 transition-colors"
              >
                <FileCode className="w-3.5 h-3.5 text-indigo-400" />
                <span>Edit LaTeX Source</span>
              </button>
              <a
                href={getPdfViewUrl(optimized.resume_id) + `?t=${pdfTimestamp}`}
                target="_blank"
                rel="noreferrer"
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs border border-slate-700 flex items-center space-x-1.5 transition-colors"
              >
                <ExternalLink className="w-3 h-3 text-brand-400" />
                <span>Open in Full Tab</span>
              </a>
              <a
                href={getPdfDownloadUrl(optimized.resume_id)}
                download
                className="px-3.5 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs flex items-center space-x-1.5 transition-colors"
              >
                <Download className="w-3 h-3" />
                <span>Download PDF</span>
              </a>
            </div>
          </div>

          <div className="w-full bg-slate-950 p-2 sm:p-4 rounded-2xl border border-slate-800 shadow-2xl flex justify-center">
            <iframe
              key={pdfTimestamp}
              src={getPdfViewUrl(optimized.resume_id) + `?t=${pdfTimestamp}`}
              className="w-full h-[950px] rounded-xl border border-slate-800 bg-white"
              title="Resume PDF Visual Preview"
            />
          </div>
        </div>
      )}

      {/* TAB 1: EDITABLE LATEX SOURCE CODE & ON-THE-FLY COMPILER */}
      {activeTab === 'latex' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 bg-slate-900 border border-slate-800 rounded-xl">
            <div>
              <h3 className="text-xs font-bold text-white flex items-center space-x-2">
                <FileCode className="w-4 h-4 text-brand-400" />
                <span>Interactive LaTeX Editor & Real-Time Compiler</span>
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Edit the LaTeX code directly below and click "Compile LaTeX & Update Resume" to see the newly compiled PDF instantly.
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={handleCopyLatex}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs flex items-center space-x-1.5 transition-colors border border-slate-700"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy LaTeX</span>
                  </>
                )}
              </button>

              <button
                onClick={handleRecompileLatex}
                disabled={isCompilingLatex}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white font-bold text-xs shadow-lg shadow-emerald-500/20 flex items-center space-x-2 transition-all"
              >
                {isCompilingLatex ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Compiling with Tectonic LaTeX...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Compile LaTeX & Update Resume</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Compilation Feedback Banners */}
          {compileError && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start space-x-2">
              <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
              <div>
                <strong className="block font-semibold">Compilation Error:</strong>
                <pre className="mt-1 whitespace-pre-wrap font-mono text-[11px] text-rose-200">{compileError}</pre>
              </div>
            </div>
          )}

          {compileSuccess && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>{compileSuccess}</span>
            </div>
          )}

          <div className="relative rounded-2xl border border-slate-800 bg-slate-950 overflow-hidden shadow-2xl">
            <div className="bg-slate-900/90 px-4 py-2 border-b border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
              <span className="font-mono">resume.tex</span>
              <span>UTF-8 | Tectonic LaTeX Engine</span>
            </div>
            <textarea
              value={editableLatex}
              onChange={(e) => setEditableLatex(e.target.value)}
              className="w-full h-[650px] p-5 bg-slate-950 text-slate-200 font-mono text-xs leading-relaxed focus:outline-none resize-y selection:bg-brand-900/50"
              spellCheck={false}
            />
          </div>
        </div>
      )}

      {/* TAB 2: OVERVIEW & ATS INTELLIGENCE */}
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
                      <span className="text-amber-400 font-bold">•</span>
                      <span>{c}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-500 italic">No major recruiter concerns flagged.</p>
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
                    <span className="text-brand-400 font-bold">→</span>
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
              <div className="space-y-2.5 text-xs">
                {Object.entries(optimized.rebuilt_skills).map(([category, skills]) => (
                  <div key={category} className="flex flex-col sm:flex-row sm:items-baseline">
                    <span className="w-52 font-bold text-slate-300 flex-shrink-0">{category}:</span>
                    <span className="text-slate-400">{skills.join(', ')}</span>
                  </div>
                ))}
              </div>
            </div>

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
                        <span className="text-xs text-brand-400 font-medium">
                          ({proj.technologies.join(', ')})
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

      {/* TAB 3: MODE 2 PROJECT ENHANCEMENTS */}
      {activeTab === 'enhancements' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/20">
            <h3 className="text-sm font-bold text-amber-300 flex items-center space-x-2">
              <Lightbulb className="w-4 h-4 text-amber-400" />
              <span>Mode 2: Practical Architectural Recommendations</span>
            </h3>
            <p className="text-xs text-slate-300 mt-1">
              These suggestions demonstrate high-impact technologies demanded by the target role that you can implement in your existing projects. They are strictly separated from your generated resume claims to maintain 100% integrity.
            </p>
          </div>

          <div className="space-y-4">
            {optimized.recommended_project_enhancements.map((enh, idx) => (
              <div key={idx} className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                    <Cpu className="w-4 h-4 text-indigo-400" />
                    <span>{enh.project_name}</span>
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {enh.target_technologies.map((t, tIdx) => (
                      <span
                        key={tIdx}
                        className="px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                      >
                        +{t}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-2 text-xs">
                  <strong className="text-slate-300 block">Suggested Concrete Enhancements:</strong>
                  <ul className="list-disc pl-5 space-y-1 text-slate-400">
                    {enh.suggested_features.map((f, fIdx) => (
                      <li key={fIdx}>{f}</li>
                    ))}
                  </ul>
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1.5">
                  <span className="font-bold text-slate-300 flex items-center space-x-1">
                    <Layers className="w-3.5 h-3.5 text-brand-400" />
                    <span>Architectural Impact:</span>
                  </span>
                  <p className="text-slate-400">{enh.architecture_recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
