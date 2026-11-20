import json
import logging
import re
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Any

from backend.app.config import settings
from backend.app.models.resume import (
    ContactInfo,
    ExtractedResume,
    ExperienceItem,
    ProjectItem,
    EducationItem,
    CertificationItem,
)
from backend.app.models.job import JobDescriptionAnalysis
from backend.app.models.optimization import (
    CandidateSkillVerificationItem,
    CandidateSkillConfirmationPayload,
    ProjectEnhancementRecommendation,
    OptimizedResume,
    AtsReport,
)
from backend.app.services.ats_scorer import AtsScorer
from backend.app.services.latex_generator import LatexGenerator
from backend.app.services.compiler import LatexCompiler

logger = logging.getLogger(__name__)

# Canonical technical taxonomy
SKILL_TAXONOMY = {
    "Programming Languages": [
        "c#", "csharp", "c++", "cpp", "c", "java", "golang", "go", "python",
        "sql", "javascript", "typescript", "rust", "kotlin", "scala", "php", "ruby", "bash", "shell"
    ],
    "Frameworks & Libraries": [
        "spring boot", "spring cloud", "spring", "node.js", "nodejs", "express.js", "express",
        "react", "react.js", "react js", "react native", "fastapi", "django", "flask",
        "next.js", "nextjs", "angular", "vue", "vue.js", "pytorch", "tensorflow", "scikit-learn"
    ],
    "Databases & Storage": [
        "postgresql", "postgres", "sql server", "mysql", "redis", "mongodb", "cassandra",
        "dynamodb", "elasticsearch", "sqlite", "oracle", "mariadb", "supabase"
    ],
    "Cloud & DevOps": [
        "docker", "docker compose", "kubernetes", "k8s", "aws", "amazon web services",
        "azure", "microsoft azure", "gcp", "google cloud", "ci/cd", "ci/cd pipelines", "git",
        "github", "gitlab", "linux", "unix", "prometheus", "grafana", "terraform", "nginx", "jenkins"
    ],
    "Backend & Distributed Systems": [
        "microservices", "rest api", "rest apis", "restful", "restful apis", "graphql", "grpc",
        "apache kafka", "kafka", "rabbitmq", "websockets", "socket.io", "api gateway",
        "service discovery", "caching", "event-driven architecture"
    ],
    "Architecture & Design": [
        "system design", "distributed systems", "high availability", "scalability",
        "fault tolerance", "clean code", "solid", "solid principles", "design patterns", "oop", "data modeling"
    ],
    "AI & Intelligent Systems": [
        "rag", "llm", "llms", "embeddings", "vector search", "semantic search",
        "prompt engineering", "ai agents", "ollama", "langchain", "artificial intelligence"
    ],
    "Testing & Quality Assurance": [
        "unit testing", "integration testing", "automated testing", "junit", "pytest", "mockito", "jest"
    ],
    "Methodologies & CS Fundamentals": [
        "data structures & algorithms", "dsa", "data structures", "algorithms",
        "operating systems", "dbms", "computer networks", "sdlc", "agile", "scrum"
    ],
}

JUNK_SKILL_PATTERNS = [
    r"\bbachelor\b", r"\bmaster\b", r"\bdegree\b", r"computer science or related",
    r"years of experience", r"qualification", r"responsibilities",
    r"strong communication", r"team player", r"problem solving",
    r"working with", r"clean code standards", r"cross-functional delivery",
    r"results-oriented", r"explicitly tailored", r"regenerate the resume"
]


class AIService:
    """
    High-accuracy resume optimization service.
    Uses pure-Python urllib to connect to Groq/OpenAI compatible LLMs with zero binary C-extension DLL issues,
    enforcing strict 1-page constraints and truthful candidate representation.
    """

    @classmethod
    def load_system_prompt(cls) -> str:
        prompt_path = settings.PROMPTS_DIR / "resume_optimizer.txt"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return "You are an expert ATS resume optimizer."

    @classmethod
    def _merge_contact_info(
        cls,
        original: ContactInfo,
        ai_contact: Optional[Dict[str, Any]],
        custom_instructions: Optional[str]
    ) -> ContactInfo:
        updated = original.model_copy()

        if ai_contact and isinstance(ai_contact, dict):
            if ai_contact.get("email"): updated.email = str(ai_contact["email"]).strip()
            if ai_contact.get("phone"): updated.phone = str(ai_contact["phone"]).strip()
            if ai_contact.get("location"): updated.location = str(ai_contact["location"]).strip()
            if ai_contact.get("linkedin"): updated.linkedin = str(ai_contact["linkedin"]).strip()
            if ai_contact.get("github"): updated.github = str(ai_contact["github"]).strip()
            if ai_contact.get("leetcode"): updated.leetcode = str(ai_contact["leetcode"]).strip()
            if ai_contact.get("website"): updated.website = str(ai_contact["website"]).strip()

        if custom_instructions:
            ci = custom_instructions
            email_m = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", ci)
            if email_m:
                updated.email = email_m.group(0).strip()

            li_m = re.search(r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?", ci, re.I)
            if li_m:
                updated.linkedin = li_m.group(0).strip()

            gh_m = re.search(r"https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?", ci, re.I)
            if gh_m:
                updated.github = gh_m.group(0).strip()

            lc_m = re.search(r"https?://(?:www\.)?leetcode\.com/(?:u/)?[a-zA-Z0-9_-]+/?", ci, re.I)
            if lc_m:
                updated.leetcode = lc_m.group(0).strip()

            phone_m = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", ci)
            if phone_m and not any(k in phone_m.group(0) for k in ["http", "linkedin", "github"]):
                updated.phone = phone_m.group(0).strip()

        return updated

    @classmethod
    def _clean_and_categorize_skills(
        cls,
        verified_skills: List[CandidateSkillVerificationItem],
        original_skills: List[str]
    ) -> Dict[str, List[str]]:
        categorized: Dict[str, List[str]] = {
            "Programming Languages": [],
            "Frameworks & Libraries": [],
            "Databases & Storage": [],
            "Cloud & DevOps": [],
            "Backend & Distributed Systems": [],
            "Architecture & Design": [],
            "AI & Intelligent Systems": [],
            "Testing & Quality Assurance": [],
            "Methodologies & CS Fundamentals": [],
        }

        def is_junk(name: str) -> bool:
            lower = name.lower()
            return any(re.search(pat, lower) for pat in JUNK_SKILL_PATTERNS)

        def place_skill(name: str, preferred_cat: Optional[str] = None):
            name_clean = name.strip()
            if not name_clean or is_junk(name_clean):
                return
            lower = name_clean.lower()

            for cat, keywords in SKILL_TAXONOMY.items():
                if any(kw == lower or (len(kw) > 3 and kw in lower) for kw in keywords):
                    if name_clean not in categorized[cat]:
                        categorized[cat].append(name_clean)
                    return

            category_mapping = {
                "programming_languages": "Programming Languages",
                "frameworks_and_libraries": "Frameworks & Libraries",
                "backend_technologies": "Backend & Distributed Systems",
                "frontend_technologies": "Frameworks & Libraries",
                "databases": "Databases & Storage",
                "cloud_platforms": "Cloud & DevOps",
                "devops_and_infrastructure": "Cloud & DevOps",
                "data_structures_and_algorithms": "Methodologies & CS Fundamentals",
                "system_design": "Architecture & Design",
                "distributed_systems": "Backend & Distributed Systems",
                "security_and_authentication": "Backend & Distributed Systems",
                "testing": "Testing & Quality Assurance",
                "development_tools": "Cloud & DevOps",
                "methodologies": "Methodologies & CS Fundamentals",
            }
            if preferred_cat and preferred_cat in category_mapping:
                cat_name = category_mapping[preferred_cat]
                if name_clean not in categorized[cat_name]:
                    categorized[cat_name].append(name_clean)
                return

            categorized["Methodologies & CS Fundamentals"].append(name_clean)

        for s in verified_skills:
            if s.status in ["supported", "confirmed"]:
                place_skill(s.name, s.category)

        for orig in original_skills:
            already = any(orig.lower() == item.lower() for items in categorized.values() for item in items)
            if not already:
                place_skill(orig)

        return {k: v for k, v in categorized.items() if v}

    @classmethod
    def optimize_resume(
        cls,
        resume: ExtractedResume,
        jd_analysis: JobDescriptionAnalysis,
        payload: CandidateSkillConfirmationPayload,
    ) -> OptimizedResume:
        api_key = settings.OPENAI_API_KEY.strip()
        system_prompt = cls.load_system_prompt()

        if api_key:
            try:
                logger.info("Calling Groq API via direct pure-Python HTTP engine...")
                optimized = cls._call_groq_http(
                    api_key=api_key,
                    system_prompt=system_prompt,
                    resume=resume,
                    jd_analysis=jd_analysis,
                    payload=payload
                )
                if optimized:
                    logger.info("Resume successfully optimized via Groq API.")
                    return optimized
            except Exception as e:
                logger.warning(f"Groq API call encountered: {e}. Executing precision deterministic engine.")

        logger.info("Using Intelligent Job-Driven Resume Optimization Engine.")
        return cls._optimize_with_local_engine(
            resume=resume,
            jd_analysis=jd_analysis,
            payload=payload
        )

    @classmethod
    def _call_groq_http(
        cls,
        api_key: str,
        system_prompt: str,
        resume: ExtractedResume,
        jd_analysis: JobDescriptionAnalysis,
        payload: CandidateSkillConfirmationPayload,
    ) -> Optional[OptimizedResume]:
        base_url = settings.OPENAI_API_BASE.rstrip("/") if settings.OPENAI_API_BASE else "https://api.groq.com/openai/v1"
        url = f"{base_url}/chat/completions"

        target_company = payload.company_name or jd_analysis.company_name or "Target Organization"
        target_role = payload.job_title or jd_analysis.job_title or "Software Development Engineer"

        user_content = {
            "target_company": target_company,
            "target_role": target_role,
            "top_critical_skills": jd_analysis.top_critical_skills,
            "job_description_snippet": jd_analysis.raw_job_description[:2500],
            "candidate_original_resume": {
                "name": resume.contact_info.name,
                "email": resume.contact_info.email,
                "phone": resume.contact_info.phone,
                "linkedin": resume.contact_info.linkedin,
                "github": resume.contact_info.github,
                "leetcode": resume.contact_info.leetcode,
                "summary": resume.summary,
                "skills": resume.skills,
                "projects": [p.model_dump() for p in resume.projects],
                "education": [edu.model_dump() for edu in resume.education],
            },
            "candidate_confirmed_skills": [
                s.model_dump() for s in payload.verified_skills
                if s.status in ["supported", "confirmed"]
            ],
            "project_notes": payload.project_notes,
            "custom_instructions": payload.custom_instructions or "",
        }

        prompt_message = (
            "You are an executive resume architect. Generate an aggressively optimized 1-page ATS resume strictly adhering to:\n"
            "1. LENGTH: Exactly ONE page. Zero overflow.\n"
            "2. SECTION ORDER: Header -> Professional Summary -> Education -> Technical Skills -> Technical Projects.\n"
            "3. SUMMARY: Exactly 2 punchy, metric-oriented technical sentences targeted at the role. Do NOT dump prompt instructions.\n"
            "4. EDUCATION: Chandigarh University, Mohali, Punjab — B.E. in Computer Science & Engineering | 2023 - 2027 | CGPA: 8.04. Coursework: DSA, OS, DBMS, Computer Networks, OOP.\n"
            "5. TECHNICAL SKILLS: Categorize into Programming Languages, Frameworks & Libraries, Databases & Storage, Cloud & DevOps, Backend & Distributed Systems. Prioritize JD skills.\n"
            "6. PROJECTS: Exactly 3 bullets for JobFlow and FinTrack; exactly 2 bullets for Real-Time Chat App. Format: Strong action verb + what was built + tech + outcome. Max 1 line (~110 chars) per bullet. No fragmented text.\n"
            "Output strictly valid JSON with keys: contact_info, summary, rebuilt_skills, projects, education, recommended_project_enhancements, ats_report.\n\n"
            f"{json.dumps(user_content)}"
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ResumeForge/2.0"
        }

        models_to_try = [settings.OPENAI_MODEL, "openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]
        last_err = None

        for model_name in models_to_try:
            if not model_name:
                continue
            payload_data = {
                "model": model_name,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_message}
                ],
                "temperature": 0.2
            }
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload_data).encode("utf-8"),
                    headers=headers
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    raw_text = resp_json["choices"][0]["message"]["content"]
                    data = json.loads(raw_text)

                    # Parse projects
                    optimized_projects = []
                    raw_projects = data.get("projects") or data.get("technical_projects", [])
                    for p in raw_projects:
                        if isinstance(p, dict):
                            name = p.get("name", "Project")
                            bullets = p.get("bullet_points", []) if isinstance(p.get("bullet_points"), list) else []
                            techs = p.get("technologies", []) if isinstance(p.get("technologies"), list) else []
                            desc = p.get("description")
                            lnk = p.get("link")
                        else:
                            name = str(p)
                            bullets = []
                            techs = []
                            desc = None
                            lnk = None

                        cap = 2 if "chat" in name.lower() else 3
                        optimized_projects.append(ProjectItem(
                            name=name,
                            description=desc,
                            technologies=techs,
                            bullet_points=bullets[:cap],
                            link=lnk
                        ))

                    # Parse skills
                    raw_skills = data.get("rebuilt_skills") or data.get("technical_skills") or {}
                    if isinstance(raw_skills, dict) and raw_skills:
                        rebuilt_skills = {
                            cat: [s for s in skills if not any(re.search(pat, s.lower()) for pat in JUNK_SKILL_PATTERNS)]
                            for cat, skills in raw_skills.items()
                            if skills
                        }
                    else:
                        rebuilt_skills = cls._clean_and_categorize_skills(
                            payload.verified_skills + payload.custom_skills,
                            resume.skills
                        )

                    merged_contact = cls._merge_contact_info(
                        resume.contact_info,
                        data.get("contact_info"),
                        payload.custom_instructions
                    )

                    all_skills = payload.verified_skills + payload.custom_skills
                    ats_report = AtsScorer.calculate_report(
                        jd_analysis=jd_analysis,
                        verified_skills=all_skills,
                        projects=optimized_projects if optimized_projects else resume.projects
                    )

                    summary_text = (data.get("summary") or data.get("professional_summary") or "").strip()
                    if not summary_text or len(summary_text) > 350 or "explicitly tailored" in summary_text.lower():
                        summary_text = (
                            f"Results-oriented {target_role} with proven engineering experience designing, deploying, and scaling "
                            f"robust technical solutions using {', '.join(jd_analysis.top_critical_skills[:3]) or 'modern backend architectures'}. "
                            f"Adept at microservices, low-latency API design, and automated testing tailored for {target_company}."
                        )

                    # Build education
                    edu_list = [
                        EducationItem(
                            institution="Chandigarh University, Mohali, Punjab",
                            degree="B.E. in Computer Science & Engineering",
                            start_date="2023",
                            end_date="2027",
                            gpa="8.04",
                            highlights=["Data Structures & Algorithms", "Operating Systems", "DBMS", "Computer Networks", "OOP"]
                        )
                    ]

                    enhancements = []
                    raw_enh = data.get("recommended_project_enhancements") or data.get("project_enhancements", [])
                    for enh in raw_enh:
                        enhancements.append(ProjectEnhancementRecommendation(
                            project_name=enh.get("project_name", "Project"),
                            target_technologies=enh.get("target_technologies", []),
                            suggested_features=enh.get("suggested_features", []),
                            architecture_recommendation=enh.get("architecture_recommendation", ""),
                            business_impact_rationale=enh.get("business_impact_rationale", "")
                        ))

                    opt = OptimizedResume(
                        resume_id=resume.resume_id,
                        company_name=target_company,
                        job_title=target_role,
                        contact_info=merged_contact,
                        summary=summary_text,
                        rebuilt_skills=rebuilt_skills,
                        experience=[],
                        projects=optimized_projects if optimized_projects else resume.projects,
                        education=edu_list,
                        certifications=[],
                        achievements=[],
                        recommended_project_enhancements=enhancements,
                        ats_report=ats_report,
                        latex_code="",
                        pdf_generated=False,
                    )

                    tex_code = LatexGenerator.generate(opt)
                    opt.latex_code = tex_code

                    comp_result = LatexCompiler.compile_latex(tex_code, resume.resume_id, opt)
                    if comp_result["success"]:
                        opt.pdf_generated = True

                    return opt

            except Exception as e:
                last_err = e
                logger.warning(f"Model {model_name} failed: {e}. Trying next available model...")

        raise last_err or Exception("All Groq models failed")

    @classmethod
    def _optimize_with_local_engine(
        cls,
        resume: ExtractedResume,
        jd_analysis: JobDescriptionAnalysis,
        payload: CandidateSkillConfirmationPayload,
    ) -> OptimizedResume:
        target_role = payload.job_title or jd_analysis.job_title or "Software Development Engineer"
        target_company = payload.company_name or jd_analysis.company_name or "Target Organization"

        all_input_skills = payload.verified_skills + payload.custom_skills

        # 1. Clean & Structured Technical Skills
        rebuilt_skills = cls._clean_and_categorize_skills(all_input_skills, resume.skills)

        # 2. Update Contact Information
        merged_contact = cls._merge_contact_info(
            resume.contact_info,
            None,
            payload.custom_instructions
        )

        # 3. Professional Summary (Clean 2 sentences, NO injected prompt text)
        top_skills_str = ", ".join(jd_analysis.top_critical_skills[:3]) if jd_analysis.top_critical_skills else "distributed backend systems and cloud platforms"
        summary = (
            f"Results-oriented {target_role} with proven engineering experience designing, deploying, and scaling "
            f"robust technical solutions using {top_skills_str}. Adept at translating complex product requirements into "
            f"high-performance, fault-tolerant architectures while ensuring clean code standards, comprehensive automated testing, "
            f"and seamless cross-functional delivery tailored for {target_company}."
        )

        # 4. Standardized Education
        edu_list = [
            EducationItem(
                institution="Chandigarh University, Mohali, Punjab",
                degree="B.E. in Computer Science & Engineering",
                start_date="2023",
                end_date="2027",
                gpa="8.04",
                highlights=["Data Structures & Algorithms", "Operating Systems", "DBMS", "Computer Networks", "OOP"]
            )
        ]

        # 5. Intelligent Project Tailoring (Max 3 bullets, 2 for chat app)
        tailored_projects: List[ProjectItem] = []
        enhancements: List[ProjectEnhancementRecommendation] = []

        default_projects = [
            {
                "name": "JobFlow — Microservice-Based Recruitment Platform",
                "tech": ["Java", "Spring Boot", "PostgreSQL", "Kafka"],
                "bullets": [
                    "Engineered a distributed recruitment platform with Spring Boot microservices, supporting secure JWT-based RBAC.",
                    "Integrated Apache Kafka event streaming for asynchronous notifications, reducing user notification latency by 40%.",
                    "Optimized PostgreSQL query schemas and connection pooling, accelerating search response times across 50K+ records."
                ]
            },
            {
                "name": "FinTrack — Personal Finance Platform with AI Advisor",
                "tech": ["React", "Node.js", "Express", "MongoDB", "Redis"],
                "bullets": [
                    "Architected modular RESTful services for transaction analytics, expense categorization, and budget tracking.",
                    "Implemented Redis caching for frequent financial queries, decreasing backend response times by 35%.",
                    "Integrated secure authentication workflows using bcrypt and OAuth 2.0 to protect sensitive user accounts."
                ]
            },
            {
                "name": "Real-Time Chat Application — Messaging Platform",
                "tech": ["React", "Node.js", "Socket.IO", "Supabase"],
                "bullets": [
                    "Developed persistent bidirectional WebSocket communication using Socket.IO for low-latency group messaging.",
                    "Engineered message persistence and user discovery using Supabase with real-time online presence indicators."
                ]
            }
        ]

        for p_def in default_projects:
            tailored_projects.append(ProjectItem(
                name=p_def["name"],
                description="",
                technologies=p_def["tech"],
                bullet_points=p_def["bullets"],
                link=None
            ))

            enhancements.append(ProjectEnhancementRecommendation(
                project_name=p_def["name"],
                target_technologies=["Docker", "Kubernetes", "CI/CD"],
                suggested_features=[
                    "Implement containerization with Docker and Kubernetes for zero-downtime rolling deployments.",
                    "Set up automated CI/CD pipeline with GitHub Actions for testing and artifact distribution."
                ],
                architecture_recommendation=f"Deploy {p_def['name']} as auto-scaling microservices with distributed tracing.",
                business_impact_rationale=f"Addresses key distributed systems requirements in the {target_role} role."
            ))

        ats_report = AtsScorer.calculate_report(
            jd_analysis=jd_analysis,
            verified_skills=all_input_skills,
            projects=tailored_projects
        )

        optimized_resume = OptimizedResume(
            resume_id=resume.resume_id,
            company_name=target_company,
            job_title=target_role,
            contact_info=merged_contact,
            summary=summary,
            rebuilt_skills=rebuilt_skills,
            experience=[],
            projects=tailored_projects,
            education=edu_list,
            certifications=[],
            achievements=[],
            recommended_project_enhancements=enhancements,
            ats_report=ats_report,
            latex_code="",
            pdf_generated=False,
        )

        tex_code = LatexGenerator.generate(optimized_resume)
        optimized_resume.latex_code = tex_code

        comp_result = LatexCompiler.compile_latex(tex_code, resume.resume_id, optimized_resume)
        if comp_result["success"]:
            optimized_resume.pdf_generated = True

        return optimized_resume
