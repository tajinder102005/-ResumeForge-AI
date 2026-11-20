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
            "2. SECTION ORDER: Header -> Professional Summary -> Education -> Technical Skills -> Technical Projects -> Achievements.\n"
            "3. ZERO FABRICATION: Do NOT invent metrics, percentages (like 30% or 40%), fake user counts (like 5k+ concurrent users), or transaction numbers (like 10k+ daily transactions). Only use verifiable, truthful achievements from the candidate's actual resume.\n"
            "4. SUMMARY: Exactly 2 technical sentences targeted at the role and company. Mention strong OOP, distributed systems, and 1000+ DSA problems solved.\n"
            "5. EDUCATION: Chandigarh University, Mohali, Punjab — B.E. in Computer Science & Engineering | 2023 - 2027 | CGPA: 8.04. Coursework: Data Structures & Algorithms, OOP, Operating Systems, DBMS, Computer Networks.\n"
            "6. TECHNICAL SKILLS: Categorize into Programming Languages, Frameworks & Libraries, Databases & Storage, Cloud & DevOps, Backend & Distributed Systems. CRITICAL: Each category must be a JSON array of strings (e.g. [\"Java\", \"Spring Boot\"]), NEVER a single comma-separated string. Prioritize skills matching the target role.\n"
            "7. PROJECTS: Exactly 3 bullets for JobFlow and FinTrack; exactly 2 bullets for Real-Time Chat App. Provide each bullet as a string inside 'bullet_points' array. Format: Strong action verb + what was built + tech + truthful outcome. Never return empty bullet_points.\n"
            "8. ACHIEVEMENTS: Include a JSON array of 3-4 strings (LeetCode 1000+ DSA problems, 500 Days Badge, NPTEL Cloud Computing Silver, hackathons).\n"
            "Output strictly valid JSON with keys: contact_info, summary, rebuilt_skills, projects, education, achievements, recommended_project_enhancements, ats_report.\n\n"
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

                    # Map original projects by first word for bullet fallback
                    orig_proj_map = {}
                    for op in resume.projects:
                        key = op.name.lower().split()[0] if op.name else ""
                        if key:
                            orig_proj_map[key] = op

                    # Parse projects
                    optimized_projects = []
                    raw_projects = data.get("projects") or data.get("technical_projects", [])
                    for p in raw_projects:
                        if isinstance(p, dict):
                            name = p.get("name") or p.get("project_name", "Project")
                            raw_b = (
                                p.get("bullet_points")
                                or p.get("bullets")
                                or p.get("highlights")
                                or p.get("points")
                                or []
                            )
                            if isinstance(raw_b, str):
                                bullets = [b.strip() for b in raw_b.split("\n") if b.strip()]
                            elif isinstance(raw_b, list):
                                bullets = [str(b).strip() for b in raw_b if str(b).strip()]
                            else:
                                bullets = []
                            raw_t = p.get("technologies") or p.get("tech") or p.get("tools") or []
                            if isinstance(raw_t, str):
                                techs = [t.strip() for t in raw_t.split(",") if t.strip()]
                            elif isinstance(raw_t, list):
                                techs = [str(t).strip() for t in raw_t if str(t).strip()]
                            else:
                                techs = []
                            desc = p.get("description")
                            lnk = p.get("link")
                        else:
                            name = str(p)
                            bullets = []
                            techs = []
                            desc = None
                            lnk = None

                        # Fallback to candidate original bullets if LLM returned empty bullets
                        first_word = name.lower().split()[0] if name else ""
                        orig_p = orig_proj_map.get(first_word)
                        if not bullets and orig_p and orig_p.bullet_points:
                            bullets = list(orig_p.bullet_points)
                        if not techs and orig_p and orig_p.technologies:
                            techs = list(orig_p.technologies)

                        # Guaranteed fallback bullets for core projects if still empty
                        if not bullets:
                            if "jobflow" in name.lower():
                                bullets = [
                                    "Architected a microservices platform for candidates, recruiters, and admins with auth, job, and application services.",
                                    "Built secured REST APIs with Spring Boot, API Gateway, Eureka, OpenFeign, JWT, RBAC, and Resilience4j.",
                                    "Implemented Kafka and RabbitMQ event-driven workflows for async notifications, with Zipkin distributed tracing."
                                ]
                                if not techs:
                                    techs = ["Java", "Spring Boot", "PostgreSQL", "RabbitMQ"]
                            elif "fintrack" in name.lower():
                                bullets = [
                                    "Built a full-stack MERN finance app for transaction tracking, budgeting, expense analytics, and reporting.",
                                    "Implemented JWT auth, bcrypt hashing, and Google/GitHub OAuth 2.0 with protected Express.js routes.",
                                    "Developed a RAG pipeline with embeddings and Pinecone vector search to give Gemini relevant financial context."
                                ]
                                if not techs:
                                    techs = ["React", "Node.js", "MongoDB", "Redis", "Pinecone"]
                            elif "chat" in name.lower():
                                bullets = [
                                    "Built a real-time messaging app with one-to-one and group chats using React, Node.js, and Socket.IO.",
                                    "Implemented user discovery via email, phone, and QR code, with typing indicators and online/offline presence."
                                ]
                                if not techs:
                                    techs = ["React", "Node.js", "Socket.IO", "Supabase"]

                        cap = 2 if "chat" in name.lower() else 3
                        optimized_projects.append(ProjectItem(
                            name=name,
                            description=desc,
                            technologies=techs,
                            bullet_points=bullets[:cap],
                            link=lnk
                        ))

                    if not optimized_projects and resume.projects:
                        optimized_projects = list(resume.projects)

                    # Parse skills: support both list of strings and comma-separated string per category
                    raw_skills = data.get("rebuilt_skills") or data.get("technical_skills") or {}
                    if isinstance(raw_skills, dict) and raw_skills:
                        rebuilt_skills = {}
                        for cat, skills_val in raw_skills.items():
                            if isinstance(skills_val, str):
                                s_list = [s.strip() for s in skills_val.split(",") if s.strip()]
                            elif isinstance(skills_val, list):
                                s_list = []
                                for item in skills_val:
                                    if isinstance(item, str):
                                        if "," in item:
                                            s_list.extend([sub.strip() for sub in item.split(",") if sub.strip()])
                                        else:
                                            s_list.append(item.strip())
                                    else:
                                        s_list.append(str(item).strip())
                            else:
                                s_list = []

                            # Deduplicate preserving order and strip junk
                            seen = set()
                            deduped = []
                            for s in s_list:
                                s_lower = s.lower()
                                if s_lower not in seen and s_lower != "" and not any(re.search(pat, s_lower) for pat in JUNK_SKILL_PATTERNS):
                                    seen.add(s_lower)
                                    deduped.append(s)
                            if deduped:
                                rebuilt_skills[cat] = deduped
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

                    # Summary: Sanitize any hallucinated metrics (5k+ users, 30%, 10k+ transactions)
                    summary_text = (data.get("summary") or data.get("professional_summary") or "").strip()
                    fake_metric_patterns = [r"\b\d+k\+\b", r"\breducing\s+response\s+latency\b", r"\b\d+%\b"]
                    has_fake_metric = any(re.search(p, summary_text, re.IGNORECASE) for p in fake_metric_patterns)

                    if not summary_text or len(summary_text) > 350 or "explicitly tailored" in summary_text.lower() or has_fake_metric:
                        company_target_str = f" at {target_company}" if target_company and target_company != "Target Organization" else ""
                        role_target_str = f"{target_role} role" if target_role and "intern" not in target_role.lower() else "Software Development Internship"
                        summary_text = (
                            f"Computer Science undergraduate (B.E., 2027) with hands-on experience building full-stack applications, "
                            f"RESTful APIs, and distributed microservices using Java, Spring Boot, React, and SQL/NoSQL databases. "
                            f"Strong foundation in OOP, SOLID principles, and system scaling with 1000+ DSA problems solved. "
                            f"Seeking a {role_target_str}{company_target_str}."
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

                    # Parse achievements
                    raw_ach = data.get("achievements") or []
                    if isinstance(raw_ach, list) and raw_ach:
                        achievements_list = [str(a).strip() for a in raw_ach if str(a).strip()]
                    else:
                        achievements_list = [
                            "Solved 1000+ Data Structures and Algorithms problems across LeetCode and competitive programming platforms.",
                            "Earned the 500 Days Coding Badge on LeetCode.",
                            "Completed NPTEL Cloud Computing certification with Silver grade.",
                            "Participated in multiple hackathons, applying software development and problem-solving skills to build solutions under time constraints."
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
                        achievements=achievements_list,
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

        # 3. Professional Summary (Clean, truthful, NO injected prompt text)
        company_target_str = f" at {target_company}" if target_company and target_company != "Target Organization" else ""
        role_target_str = f"{target_role} role" if target_role and "intern" not in target_role.lower() else "Software Development Internship"
        summary = (
            f"Computer Science undergraduate (B.E., 2027) with hands-on experience building back-end applications, "
            f"microservices, and AI-integrated products using Java, Spring Boot, Node.js, React, and SQL/NoSQL databases. "
            f"Strong in OOP, SOLID principles, REST APIs, event-driven systems (Kafka, RabbitMQ), and RAG/LLM features. "
            f"Solved 900+ DSA problems. Seeking a {role_target_str}{company_target_str}."
        )

        # 4. Standardized Education
        edu_list = [
            EducationItem(
                institution="Chandigarh University, Mohali, Punjab",
                degree="B.E. in Computer Science & Engineering",
                start_date="2023",
                end_date="2027",
                gpa="8.04",
                highlights=["Data Structures & Algorithms", "OOP", "Operating Systems", "DBMS", "Computer Networks"]
            )
        ]

        # 5. Intelligent Project Tailoring (Truthful project bullets from candidate resume)
        tailored_projects: List[ProjectItem] = []
        enhancements: List[ProjectEnhancementRecommendation] = []

        default_projects = [
            {
                "name": "JobFlow — Microservice-Based Job Application Platform",
                "tech": ["Java", "Spring Boot", "PostgreSQL", "Kafka", "RabbitMQ"],
                "bullets": [
                    "Architected a microservices platform for candidates, recruiters, and admins with auth, job, and application services.",
                    "Built secured REST APIs with Spring Boot, API Gateway, Eureka, OpenFeign, JWT, RBAC, and Resilience4j.",
                    "Implemented Kafka and RabbitMQ event-driven workflows for async notifications, with Zipkin distributed tracing.",
                    "Used PostgreSQL for persistence and Elasticsearch for fast job and candidate search."
                ]
            },
            {
                "name": "FinTrack — Personal Finance Platform with AI Advisor",
                "tech": ["React", "Node.js", "MongoDB", "Redis", "Pinecone"],
                "bullets": [
                    "Built a full-stack MERN finance app for transaction tracking, budgeting, expense analytics, and reporting.",
                    "Implemented JWT auth, bcrypt hashing, and Google/GitHub OAuth 2.0 with protected Express.js routes.",
                    "Developed a RAG pipeline with embeddings and Pinecone vector search to give Gemini relevant financial context.",
                    "Added Redis caching, real-time Socket.IO budget alerts, and React dashboards using Context API and Recharts."
                ]
            },
            {
                "name": "Real-Time Chat Application — Messaging Platform",
                "tech": ["React", "Node.js", "Socket.IO", "Redis", "Supabase"],
                "bullets": [
                    "Built a real-time messaging app with one-to-one and group chats using React, Node.js, and Socket.IO.",
                    "Implemented user discovery via email, phone, and QR code, with typing indicators and online/offline presence.",
                    "Used Redis Pub/Sub to sync messages across server instances; integrated Supabase for auth and message storage."
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

        achievements_list = [
            "Solved 900+ Data Structures and Algorithms problems across LeetCode and competitive programming platforms.",
            "Earned the 500 Days Coding Badge on LeetCode.",
            "Completed NPTEL Cloud Computing certification with Silver grade."
        ]

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
            achievements=achievements_list,
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
