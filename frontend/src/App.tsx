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

export const App: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<StepKey>('upload');
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  // Core App State
  const [extractedResume, setExtractedResume] = useState<ExtractedResume | null>(null);
  const [companyName, setCompanyName] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jdAnalysis, setJdAnalysis] = useState<JobDescriptionAnalysis | null>(null);
  const [skillsVerification, setSkillsVerification] = useState<CandidateSkillVerificationItem[]>([]);
  const [projectNotes, setProjectNotes] = useState<Record<string, string>>({});
  const [optimizationMode, setOptimizationMode] = useState<'aggressive' | 'enhancement_only'>('aggressive');
  const [optimizedResume, setOptimizedResume] = useState<OptimizedResume | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

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

