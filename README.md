# ResumeForge AI — Aggressive Job-Description-Driven ATS Resume Optimizer

**ResumeForge AI** is an enterprise-grade ATS resume optimization system and LaTeX compiler that turns existing candidate resumes into aggressively tailored, role-specific, ATS-aligned resumes.

The application adheres strictly to a **zero-fabrication policy**: it treats the uploaded resume as a source of verified candidate background, discovers relevant qualifications demanded by the target Job Description (JD), allows interactive candidate skill confirmation, and generates high-fidelity ATS resumes in both LaTeX source (`.tex`) and compiled PDF formats.

---

## Key Highlights & Architectural Directives

1. **Job Description as the Primary Target**:
   - The Job Description dictates resume structure, keyword prioritization, and technical hierarchy.
   - Discards outdated or irrelevant skills that dilute focus from the target opening.
2. **Deep 17-Category Keyword Analysis**:
   - Classifies JD terminology into: Programming Languages, Frameworks & Libraries, Backend Technologies, Frontend Technologies, Databases, Cloud Platforms, DevOps & Infrastructure, Data Structures & Algorithms, System Design, Distributed Systems, Security & Authentication, Testing, Development Tools, Methodologies, Required Qualifications, Preferred Qualifications, and Domain-Specific Terminology.
3. **Interactive Candidate Skills Verification System**:
   - Skills absent from the old resume are **not** assumed unknown.
   - Compares JD requirements against resume evidence:
     - **Supported**: Found directly in resume bullet points, skills, or projects.
     - **Needs Confirmation**: Missing from resume text; candidate can confirm proficiency, provide context, or reject.
     - **Custom Skills**: Candidate can introduce additional verified technologies.
4. **Intelligent Project Tailoring & Recommendations (Two Modes)**:
   - **Mode 1 (Aggressive Resume Optimization)**: Rewrites project bullet points using the Google XYZ action-impact formula (*Accomplished [X] measured by [Y] by doing [Z]*).
   - **Mode 2 (Project Enhancement Recommendations)**: Recommends practical future features (e.g., adding Redis caching, Dockerizing, or CI/CD) that candidate could implement to strengthen competitiveness, cleanly segregated from resume claims.
5. **High-Fidelity PDF & LaTeX Generation**:
   - Generates clean, standard, ATS-compliant LaTeX (`.tex`) templates with `hyperref`, `titlesec`, and `enumitem`.
   - Compiles directly to PDF via **Tectonic** with automatic fallback to **PyMuPDF Direct ATS Engine**.
   - Validates text searchability, word count, and section integrity using PyMuPDF.
6. **Modular AI Engine**:
   - Loads system prompts from `backend/prompts/resume_optimizer.txt`.
   - Supports **Groq API** (`llama-3.3-70b-versatile`) and **OpenAI API** (`gpt-4o`, `gpt-4o-mini`).
   - Includes a deterministic, offline-capable **Intelligent Local Optimization Engine** as a reliable fallback.

---

## Project Structure

```
ResumeForge-AI/
├── .gitignore
├── README.md
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── prompts/
│   │   └── resume_optimizer.txt        # Core ATS optimization instructions
│   ├── app/
│   │   ├── config.py                   # Pydantic settings & environment configuration
│   │   ├── main.py                     # FastAPI REST API & static file serving
│   │   ├── models/
│   │   │   ├── resume.py               # Extracted resume data structures
│   │   │   ├── job.py                  # 17-category JD keyword models
│   │   │   └── optimization.py         # Skill verification & ATS report models
│   │   ├── services/
│   │   │   ├── extractor.py            # PDF (PyMuPDF) and DOCX text extraction
│   │   │   ├── jd_analyzer.py          # 17-domain keyword extractor
│   │   │   ├── resume_analyzer.py      # Resume evidence vs JD comparison
│   │   │   ├── ats_scorer.py           # Multi-dimensional ATS scoring
│   │   │   ├── ai_service.py           # Groq/OpenAI integration & local engine
│   │   │   ├── latex_generator.py      # Standard ATS LaTeX generator
│   │   │   └── compiler.py             # Tectonic & PyMuPDF PDF rendering
│   │   └── utils/
│   │       └── text_cleaning.py        # Unicode cleanup & LaTeX escaping
│   └── tests/
│       ├── test_extractor.py
│       ├── test_jd_analyzer.py
│       ├── test_resume_analyzer.py
│       ├── test_ats_scorer.py
│       ├── test_compiler.py
│       ├── test_ai_service.py
│       └── test_api.py
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx                     # Single-page multi-step coordinator
        ├── types/                      # TypeScript schemas
        ├── services/api.ts             # Backend API client
        └── components/
            ├── Header.tsx              # Engine & compiler live badges
            ├── StepNavigation.tsx      # Step wizard navigation
            ├── ResumeUploadStep.tsx    # Drag & drop upload & parsed overview
            ├── JobDescriptionStep.tsx  # Company, job title, and JD input
            ├── KeywordAnalysisStep.tsx # 17-category keyword inspector
            ├── SkillsVerificationStep.tsx # Interactive candidate skill verification
            ├── ProjectEnhancementStep.tsx # Project tailoring & Mode 2 recommendations
            └── ResumePreviewStep.tsx   # ATS report, LaTeX viewer, PDF download
```

---

## Quick Start & Installation

### Prerequisites
- Python 3.11+
- Node.js LTS (v20+) & npm
- Tectonic (optional for local LaTeX compilation; built-in PyMuPDF fallback included)

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

Configure your environment variables:
```bash
cp .env.example .env
```
Edit `backend/.env` with your API credentials (or leave empty to use the built-in Intelligent Local Engine):
```env
OPENAI_API_KEY=gsk_your_groq_or_openai_key
OPENAI_API_BASE=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.3-70b-versatile
HOST=127.0.0.1
PORT=8000
```

Start the backend:
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API docs available at: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run build
npm run dev
```
Open `http://localhost:5173` in your browser.

*(Note: Since the backend also serves `frontend/dist` statically, running the backend alone and opening `http://127.0.0.1:8000/` will also load the complete full-stack application!)*

---

## Running the Automated Test Suite

Run all backend unit, integration, and compilation tests with `pytest`:
```bash
python -m pytest -p no:asyncio backend/tests -v
```

Expected result:
```
============================== 7 passed in 9.40s ==============================
```

---

## Git Workflow
Developed on the `developer` branch using professional conventional commits. Never commits sensitive user documents, `.env` files, or generated resumes.
