import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { StepNavigation, StepKey } from './components/StepNavigation';
import { ResumeUploadStep } from './components/ResumeUploadStep';
import { JobDescriptionStep } from './components/JobDescriptionStep';
import { KeywordAnalysisStep } from './components/KeywordAnalysisStep';
import { SkillsVerificationStep } from './components/SkillsVerificationStep';
import { ProjectEnhancementStep } from './components/ProjectEnhancementStep';
import { ResumePreviewStep } from './components/ResumePreviewStep';
import {
  ExtractedResume,
  JobDescriptionAnalysis,
  CandidateSkillVerificationItem,
  OptimizedResume,
  SystemStatus,
} from './types';
import { fetchSystemStatus, optimizeResume } from './services/api';

const STORAGE_KEY = 'resumeforge_active_session_v1';

function loadPersistedSession() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (err) {
    console.warn('Failed to parse saved session from localStorage:', err);
    return null;
  }
}

function savePersistedSession(data: any) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (err) {
    console.warn('Failed to save session to localStorage:', err);
  }
}

export const App: React.FC = () => {
  const initialData = React.useMemo(() => loadPersistedSession(), []);

  const getInitialStep = (): StepKey => {
    try {
      const hash = window.location.hash.toLowerCase();
      if ((hash.includes('result') || hash.includes('step=result')) && initialData?.optimizedResume) {
        return 'result';
      }
      if (hash.includes('upload')) return 'upload';
    } catch (_) {}

    if (initialData?.optimizedResume) {
      return 'result';
    }
    if (initialData?.currentStep) {
      return initialData.currentStep;
    }
    return 'upload';
  };

  const [currentStep, setCurrentStep] = useState<StepKey>(getInitialStep);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  // Core App State
  const [extractedResume, setExtractedResume] = useState<ExtractedResume | null>(initialData?.extractedResume || null);
  const [companyName, setCompanyName] = useState(initialData?.companyName || '');
  const [jobTitle, setJobTitle] = useState(initialData?.jobTitle || '');
  const [jobDescription, setJobDescription] = useState(initialData?.jobDescription || '');
  const [jdAnalysis, setJdAnalysis] = useState<JobDescriptionAnalysis | null>(initialData?.jdAnalysis || null);
  const [skillsVerification, setSkillsVerification] = useState<CandidateSkillVerificationItem[]>(initialData?.skillsVerification || []);
  const [projectNotes, setProjectNotes] = useState<Record<string, string>>(initialData?.projectNotes || {});
  const [optimizationMode, setOptimizationMode] = useState<'aggressive' | 'enhancement_only'>(initialData?.optimizationMode || 'aggressive');
  const [optimizedResume, setOptimizedResume] = useState<OptimizedResume | null>(initialData?.optimizedResume || null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Sync URL hash with current step for instant browser back/forward navigation support
  useEffect(() => {
    try {
      window.location.hash = `step=${currentStep}`;
    } catch (_) {}
  }, [currentStep]);

  // Listen to browser Back/Forward arrow navigation
  useEffect(() => {
    const handlePopState = () => {
      try {
        const hash = window.location.hash.toLowerCase();
        if ((hash.includes('result') || hash.includes('step=result')) && (optimizedResume || initialData?.optimizedResume)) {
          setCurrentStep('result');
        } else if (hash.includes('job') && (extractedResume || initialData?.extractedResume)) {
          setCurrentStep('job');
        } else if (hash.includes('upload')) {
          setCurrentStep('upload');
        }
      } catch (_) {}
    };

    window.addEventListener('popstate', handlePopState);
    window.addEventListener('hashchange', handlePopState);
    return () => {
      window.removeEventListener('popstate', handlePopState);
      window.removeEventListener('hashchange', handlePopState);
    };
  }, [optimizedResume, extractedResume, initialData]);

  // Automatically save to localStorage on any state change, but do NOT wipe stored state with empty initial state
  useEffect(() => {
    if (!extractedResume && !optimizedResume && !initialData?.extractedResume) {
      return;
    }
    savePersistedSession({
      currentStep,
      extractedResume,
      companyName,
      jobTitle,
      jobDescription,
      jdAnalysis,
      skillsVerification,
      projectNotes,
      optimizationMode,
      optimizedResume,
    });
  }, [
    currentStep,
    extractedResume,
    companyName,
    jobTitle,
    jobDescription,
    jdAnalysis,
    skillsVerification,
    projectNotes,
    optimizationMode,
    optimizedResume,
    initialData,
  ]);

  useEffect(() => {
    fetchSystemStatus()
      .then(setSystemStatus)
      .catch((err) => console.warn('Could not fetch backend system status:', err));
  }, []);

  const canNavigateTo = (step: StepKey): boolean => {
    switch (step) {
      case 'upload':
        return true;
      case 'job':
        return !!extractedResume;
      case 'analysis':
        return !!extractedResume && !!jdAnalysis;
      case 'verification':
        return !!extractedResume && skillsVerification.length > 0;
      case 'projects':
        return !!extractedResume && skillsVerification.length > 0;
      case 'result':
        return !!optimizedResume;
      default:
        return false;
    }
  };

  const handleGenerate = async () => {
    if (!extractedResume || !jdAnalysis) return;
    setIsGenerating(true);

    try {
      const result = await optimizeResume({
        resume_id: extractedResume.resume_id,
        company_name: companyName,
        job_title: jobTitle,
        raw_job_description: jobDescription,
        verified_skills: skillsVerification,
        project_notes: projectNotes,
        optimization_mode: optimizationMode,
      });
      setOptimizedResume(result);
      setCurrentStep('result');
    } catch (err: any) {
      alert(`Optimization failed: ${err.message || 'Please check backend logs'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleReset = () => {
    setJdAnalysis(null);
    setSkillsVerification([]);
    setProjectNotes({});
    setOptimizedResume(null);
    setCurrentStep('job');
  };

  const handleFullReset = () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (_) {}
    setExtractedResume(null);
    setCompanyName('');
    setJobTitle('');
    setJobDescription('');
    setJdAnalysis(null);
    setSkillsVerification([]);
    setProjectNotes({});
    setOptimizedResume(null);
    setCurrentStep('upload');
  };

  const handleRegenerateWithInstructions = async (instructions: string) => {
    if (!extractedResume || !jdAnalysis) return;
    setIsGenerating(true);

    try {
      const result = await optimizeResume({
        resume_id: extractedResume.resume_id,
        company_name: companyName,
        job_title: jobTitle,
        raw_job_description: jobDescription,
        verified_skills: skillsVerification,
        project_notes: projectNotes,
        optimization_mode: optimizationMode,
        custom_instructions: instructions,
      });
      setOptimizedResume(result);
    } catch (err: any) {
      alert(`Regeneration failed: ${err.message || 'Please check backend logs'}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header status={systemStatus} />

      <StepNavigation
        currentStep={currentStep}
        onSelectStep={setCurrentStep}
        canNavigateTo={canNavigateTo}
      />

      <main className="flex-1 pb-16">
        {currentStep === 'upload' && (
          <ResumeUploadStep
            resume={extractedResume}
            onUploadSuccess={(data) => {
              setExtractedResume(data);
              setCurrentStep('job');
            }}
            onProceed={() => setCurrentStep('job')}
          />
        )}

        {currentStep === 'job' && extractedResume && (
          <JobDescriptionStep
            resumeId={extractedResume.resume_id}
            companyName={companyName}
            jobTitle={jobTitle}
            jobDescription={jobDescription}
            onUpdateParams={({ companyName: c, jobTitle: j, jobDescription: d }) => {
              setCompanyName(c);
              setJobTitle(j);
              setJobDescription(d);
            }}
            onAnalysisSuccess={(analysis, skills) => {
              setJdAnalysis(analysis);
              setSkillsVerification(skills);
              setCurrentStep('analysis');
            }}
            onProceed={() => setCurrentStep('analysis')}
          />
        )}

        {currentStep === 'analysis' && (
          <KeywordAnalysisStep
            analysis={jdAnalysis}
            onProceed={() => setCurrentStep('verification')}
          />
        )}

        {currentStep === 'verification' && (
          <SkillsVerificationStep
            skills={skillsVerification}
            onUpdateSkills={setSkillsVerification}
            onProceed={() => setCurrentStep('projects')}
          />
        )}

        {currentStep === 'projects' && extractedResume && (
          <ProjectEnhancementStep
            resume={extractedResume}
            verifiedSkills={skillsVerification}
            projectNotes={projectNotes}
            optimizationMode={optimizationMode}
            onUpdateProjectNotes={setProjectNotes}
            onUpdateMode={setOptimizationMode}
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
          />
        )}

        {currentStep === 'result' && optimizedResume && (
          <ResumePreviewStep
            optimized={optimizedResume}
            onReset={handleReset}
            onFullReset={handleFullReset}
            onRegenerateWithInstructions={handleRegenerateWithInstructions}
            onNavigateToStep={setCurrentStep}
            isRegenerating={isGenerating}
          />
        )}
      </main>

      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        <p>ResumeForge AI — Aggressive Job-Description-Driven ATS Resume Optimizer & LaTeX Compiler.</p>
        <p className="mt-1">Zero fabrication policy enforced. All confirmed skills verified by candidate.</p>
      </footer>
    </div>
  );
};

export default App;

