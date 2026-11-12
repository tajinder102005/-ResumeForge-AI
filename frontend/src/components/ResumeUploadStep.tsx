import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, ArrowRight, RefreshCw, User, Mail, Phone, Code, Briefcase } from 'lucide-react';
import { ExtractedResume } from '../types';
import { uploadResume } from '../services/api';

interface ResumeUploadStepProps {
  resume: ExtractedResume | null;
  onUploadSuccess: (resume: ExtractedResume) => void;
  onProceed: () => void;
}

export const ResumeUploadStep: React.FC<ResumeUploadStepProps> = ({
  resume,
  onUploadSuccess,
  onProceed,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setError(null);
    setLoading(true);
    try {
      const data = await uploadResume(file);
      onUploadSuccess(data);
    } catch (err: any) {
      setError(err.message || 'Error uploading resume.');
    } finally {
      setLoading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          Upload Your Existing Resume
        </h1>
        <p className="mt-3 text-base text-slate-400 max-w-2xl mx-auto">
          ResumeForge AI treats your resume as a rich source of verified background information.
          Upload your PDF or DOCX file to extract your experience, skills, and projects.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Zone */}
      {!resume || loading ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-200 ${
            dragOver
              ? 'border-brand-400 bg-brand-500/10 scale-[1.01]'
              : 'border-slate-700/80 bg-slate-900/60 hover:border-slate-600 hover:bg-slate-900'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.doc,.txt"
            className="hidden"
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFile(e.target.files[0]);
              }
            }}
          />

          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center text-brand-400 shadow-lg">
            {loading ? (
              <RefreshCw className="w-8 h-8 animate-spin text-brand-400" />
            ) : (
              <Upload className="w-8 h-8" />
            )}
          </div>

          <h3 className="text-lg font-semibold text-white">
            {loading ? 'Analyzing and Extracting Document...' : 'Drag and drop your resume here'}
          </h3>
          <p className="mt-2 text-sm text-slate-400">
            Supports PDF, DOCX, and TXT (PyMuPDF & python-docx powered parsing)
          </p>

          <button
            type="button"
            disabled={loading}
            className="mt-6 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-medium shadow-md shadow-brand-500/20 transition-all inline-flex items-center space-x-2"
          >
            <FileText className="w-4 h-4" />
            <span>Select File from Computer</span>
          </button>
        </div>
      ) : (
        /* Parsed Resume Confirmation Card */
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl">
          <div className="flex items-start justify-between border-b border-slate-800 pb-5">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                  <span>{resume.filename}</span>
                  <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Parsed Successfully
                  </span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">Resume ID: {resume.resume_id}</p>
              </div>
            </div>

            <button
              onClick={() => fileInputRef.current?.click()}
              className="text-xs text-slate-400 hover:text-slate-200 border border-slate-700 hover:border-slate-600 px-3 py-1.5 rounded-lg flex items-center space-x-1.5 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Replace File</span>
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.doc,.txt"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFile(e.target.files[0]);
                }
              }}
            />
          </div>

          {/* Candidate Snapshot Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-6">
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="flex items-center space-x-2 text-xs text-slate-400 mb-1">
                <User className="w-3.5 h-3.5 text-brand-400" />
                <span>Candidate Name</span>
              </div>
              <p className="font-semibold text-white truncate">{resume.contact_info.name || 'Not Detected'}</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="flex items-center space-x-2 text-xs text-slate-400 mb-1">
                <Mail className="w-3.5 h-3.5 text-brand-400" />
                <span>Contact Email</span>
              </div>
              <p className="font-semibold text-white truncate">{resume.contact_info.email || 'Not Detected'}</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="flex items-center space-x-2 text-xs text-slate-400 mb-1">
                <Phone className="w-3.5 h-3.5 text-brand-400" />
                <span>Phone / Location</span>
              </div>
              <p className="font-semibold text-white truncate">{resume.contact_info.phone || 'Location in Document'}</p>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-3 gap-3 p-4 bg-slate-950/40 border border-slate-800/50 rounded-xl text-center text-xs mb-6">
            <div>
              <span className="block text-xl font-bold text-brand-400">{resume.skills.length}</span>
              <span className="text-slate-400">Extracted Skills</span>
            </div>
            <div>
              <span className="block text-xl font-bold text-indigo-400">{resume.experience.length}</span>
              <span className="text-slate-400">Work Roles</span>
            </div>
            <div>
              <span className="block text-xl font-bold text-emerald-400">{resume.projects.length}</span>
              <span className="text-slate-400">Projects Detected</span>
            </div>
          </div>

          {/* Action button */}
          <div className="flex justify-end">
            <button
              onClick={onProceed}
              className="px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold shadow-lg shadow-brand-500/20 transition-all flex items-center space-x-2"
            >
              <span>Target Job Description</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

