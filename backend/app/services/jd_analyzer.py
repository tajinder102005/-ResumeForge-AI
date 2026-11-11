import re
from typing import Dict, List, Set, Tuple
from backend.app.models.job import JobKeyword, CategorizedJobKeywords, JobDescriptionAnalysis


class JobDescriptionAnalyzer:
    """Performs deep keyword extraction and categorization across 17 technical domains."""

    TECH_CATALOG: Dict[str, Dict[str, List[str]]] = {
        "programming_languages": {
            "Python": ["python", "python3", "py"],
            "TypeScript": ["typescript", "ts"],
            "JavaScript": ["javascript", "js", "es6", "ecmascript"],
            "Java": ["java", "core java", "j2ee"],
            "Go / Golang": ["golang", "go language", r"\bgo\b"],
            "C++": [r"c\+\+", "cpp"],
            "C#": [r"c\#", "csharp", r"\.net"],
            "Rust": [r"\brust\b"],
            "SQL": [r"\bsql\b", "t-sql", "pl/sql"],
            "Kotlin": ["kotlin"],
            "Swift": ["swift"],
            "Ruby": ["ruby"],
            "PHP": ["php"],
            "Scala": ["scala"],
            "R": [r"\br\b(?:\s+programming|\s+language)"],
            "Bash / Shell": ["bash", "shell scripting", "powershell", "sh"],
        },
        "frameworks_and_libraries": {
            "React": ["react", "react.js", "reactjs"],
            "Next.js": ["next.js", "nextjs"],
            "FastAPI": ["fastapi"],
            "Django": ["django", "django rest framework", "drf"],
            "Flask": ["flask"],
            "Express.js": ["express", "express.js", "expressjs"],
            "Spring Boot": ["spring boot", "spring framework", "spring"],
            "PyTorch": ["pytorch"],
            "TensorFlow": ["tensorflow", "keras"],
            "Vue.js": ["vue", "vue.js", "vuejs"],
            "Angular": ["angular", "angularjs"],
            "Tailwind CSS": ["tailwind", "tailwindcss"],
            "Pandas": ["pandas"],
            "NumPy": ["numpy"],
            "Scikit-learn": ["scikit-learn", "sklearn"],
        },
        "backend_technologies": {
            "RESTful APIs": ["rest", "restful", "rest api", "rest apis", "restful api"],
            "GraphQL": ["graphql"],
            "gRPC": ["grpc", "protocol buffers", "protobuf"],
            "Node.js": ["node", "node.js", "nodejs"],
            "Microservices": ["microservices", "microservice architecture", "micro-services"],
            "WebSockets": ["websockets", "websocket"],
            "Celery": ["celery"],
            "AsyncIO": ["asyncio", "asynchronous programming"],
            "Event-Driven Architecture": ["event-driven", "event driven architecture", "eda"],
        },
        "frontend_technologies": {
            "HTML5": ["html", "html5"],
            "CSS3": ["css", "css3", "sass", "scss"],
            "Redux / Zustand": ["redux", "zustand", "state management"],
            "Vite": ["vite"],
            "Webpack": ["webpack", "vite", "bundler"],
            "Responsive Web Design": ["responsive design", "mobile-first", "responsive ui"],
            "Single Page Applications": ["spa", "single page application"],
        },
        "databases": {
            "PostgreSQL": ["postgresql", "postgres"],
            "MySQL": ["mysql"],
            "MongoDB": ["mongodb", "mongo"],
            "Redis": ["redis"],
            "Elasticsearch": ["elasticsearch", "elastic search", "opensearch"],
            "Cassandra": ["cassandra"],
            "DynamoDB": ["dynamodb"],
            "SQLite": ["sqlite"],
            "Database Indexing & Optimization": ["indexing", "query optimization", "schema design", "db normalization"],
        },
        "cloud_platforms": {
            "Amazon Web Services (AWS)": ["aws", "amazon web services", "ec2", "s3", "lambda", "rds", "sqs", "sns", "ecs", "eks"],
            "Google Cloud Platform (GCP)": ["gcp", "google cloud", "google cloud platform", "bigquery", "cloud run"],
            "Microsoft Azure": ["azure", "azure devops", "azure functions"],
            "Cloudflare": ["cloudflare"],
        },
        "devops_and_infrastructure": {
            "Docker": ["docker", "containerization", "containers"],
            "Kubernetes": ["kubernetes", "k8s"],
            "CI/CD Pipelines": ["ci/cd", "ci cd", "continuous integration", "continuous deployment", "github actions", "gitlab ci", "jenkins"],
            "Terraform": ["terraform", "infrastructure as code", "iac"],
            "Linux": ["linux", "unix", "ubuntu"],
            "Nginx": ["nginx", "reverse proxy"],
            "Prometheus & Grafana": ["prometheus", "grafana", "monitoring", "observability", "datadog"],
        },
        "data_structures_and_algorithms": {
            "Data Structures & Algorithms": ["data structures", "algorithms", "dsa"],
            "Algorithmic Complexity (Big-O)": ["time complexity", "space complexity", "big-o", "big o"],
            "Graph & Tree Traversal": ["graphs", "trees", "dfs", "bfs", "dynamic programming"],
        },
        "system_design": {
            "System Design": ["system design", "systems design"],
            "High Availability & Scalability": ["scalability", "high availability", "horizontal scaling", "fault tolerance"],
            "Caching Strategies": ["caching", "cache invalidation", "cdn", "write-through", "redis caching"],
            "Load Balancing": ["load balancing", "load balancers", "reverse proxy"],
            "Rate Limiting": ["rate limiting", "throttling"],
            "Message Brokers": ["message broker", "message queuing", "pub/sub"],
        },
        "distributed_systems": {
            "Apache Kafka": ["kafka", "apache kafka"],
            "RabbitMQ": ["rabbitmq"],
            "Distributed Systems": ["distributed systems", "distributed computing", "consensus", "cap theorem", "eventual consistency"],
        },
        "security_and_authentication": {
            "OAuth2 & JWT": ["oauth", "oauth2", "jwt", "json web tokens", "authentication", "authorization"],
            "RBAC": ["rbac", "role-based access control"],
            "Web Security (OWASP)": ["owasp", "cors", "csrf", "xss", "sql injection"],
            "HTTPS & Encryption": ["https", "tls", "ssl", "data encryption", "pki"],
        },
        "testing": {
            "Unit Testing": ["unit testing", "unit tests"],
            "Integration Testing": ["integration testing", "end-to-end testing", "e2e"],
            "Pytest": ["pytest"],
            "Jest / Vitest": ["jest", "vitest"],
            "Cypress / Playwright": ["cypress", "playwright", "selenium"],
            "Test-Driven Development (TDD)": ["tdd", "test driven development"],
        },
        "development_tools": {
            "Git & GitHub": ["git", "github", "gitlab", "version control"],
            "Postman": ["postman", "insomnia", "api testing"],
            "VS Code": ["vs code", "vscode"],
            "Jira / Agile Boards": ["jira", "confluence", "trello", "linear"],
        },
        "methodologies": {
            "Agile / Scrum": ["agile", "scrum", "kanban", "sprints", "standups"],
            "Code Reviews": ["code review", "peer reviews", "pull requests"],
            "Clean Code & SOLID": ["clean code", "solid principles", "design patterns"],
        },
        "required_qualifications": {
            "Bachelor's Degree in Computer Science or related": [
                "bachelor", "bs in computer science", "degree in computer science", "b.s.", "b.tech", "undergraduate degree"
            ],
            "3+ Years of Software Engineering Experience": [
                "3+ years", "3-5 years", "2+ years", "5+ years", "professional experience", "years of experience"
            ],
            "Strong Problem Solving Skills": ["problem solving", "analytical thinking", "critical thinking"],
        },
        "preferred_qualifications": {
            "Master's Degree in Computer Science": ["master", "master's degree", "ms in computer science", "m.s."],
            "Cloud Certifications (AWS / GCP)": ["aws certified", "cloud practitioner", "gcp certified"],
            "Open Source Contributions": ["open source", "github contributions"],
        },
        "domain_specific_terminology": {
            "Artificial Intelligence & LLMs": ["llm", "large language models", "generative ai", "ai", "rag", "embeddings"],
            "Fintech & Payment Processing": ["fintech", "payment gateway", "stripe", "financial services"],
            "ATS Optimization": ["ats", "applicant tracking system", "resume parsing"],
            "Data Pipelines": ["etl", "data pipeline", "data ingestion", "batch processing"],
        }
    }

    @classmethod
    def analyze_job_description(
        cls,
        job_description: str,
        company_name: str = "",
        job_title: str = ""
    ) -> JobDescriptionAnalysis:
        jd_lower = " " + job_description.lower() + " "
        
        # Determine sections if JD has explicit "Requirements" vs "Nice to have"
        req_section, pref_section = cls._split_requirements_and_preferred(jd_lower)

        categorized = CategorizedJobKeywords()
        total_count = 0
        all_found_skills: List[Tuple[str, str, str]] = [] # (name, category, importance)

        for category_name, skills_dict in cls.TECH_CATALOG.items():
            category_keywords: List[JobKeyword] = []
            
            for standard_name, pattern_list in skills_dict.items():
                found, matched_pattern = cls._check_presence(pattern_list, jd_lower)
                if found:
                    # Determine importance based on where it appears in JD
                    importance = "required"
                    if pref_section and matched_pattern in pref_section and matched_pattern not in req_section:
                        importance = "preferred"
                    elif category_name in ["preferred_qualifications", "domain_specific_terminology"]:
                        importance = "preferred"
                    elif category_name in ["development_tools", "methodologies"]:
                        importance = "bonus"

                    kw = JobKeyword(
                        name=standard_name,
                        category=category_name,
                        importance=importance,
                        context=f"Mentioned in job description ({matched_pattern})"
                    )
                    category_keywords.append(kw)
                    all_found_skills.append((standard_name, category_name, importance))
                    total_count += 1

            setattr(categorized, category_name, category_keywords)

        # Derive target role level
        level = "Mid-Senior"
        if any(w in jd_lower for w in ["lead", "staff", "principal", "architect", "director", "manager"]):
            level = "Senior / Staff"
        elif any(w in jd_lower for w in ["junior", "entry", "associate", "graduate", "intern"]):
            level = "Entry / Junior"

        # Determine top critical skills (required programming languages, frameworks, backend, databases, cloud)
        critical_skills = [
            name for name, cat, imp in all_found_skills
            if imp == "required" and cat in [
                "programming_languages",
                "frameworks_and_libraries",
                "backend_technologies",
                "databases",
                "cloud_platforms"
            ]
        ][:8]

        return JobDescriptionAnalysis(
            company_name=company_name,
            job_title=job_title,
            raw_job_description=job_description,
            target_role_level=level,
            categorized_keywords=categorized,
            total_keywords_count=total_count,
            top_critical_skills=critical_skills,
        )

    @classmethod
    def _check_presence(cls, patterns: List[str], text: str) -> Tuple[bool, str]:
        for pat in patterns:
            # If pattern already has regex boundary, use directly
            if "\\" in pat:
                if re.search(pat, text, re.IGNORECASE):
                    return True, pat
            else:
                # Word boundary check
                boundary_regex = r"(?<!\w)" + re.escape(pat) + r"(?!\w)"
                if re.search(boundary_regex, text, re.IGNORECASE):
                    return True, pat
        return False, ""

    @classmethod
    def _split_requirements_and_preferred(cls, text: str) -> Tuple[str, str]:
        req_start = -1
        pref_start = -1

        req_patterns = ["requirements", "what you need", "what you'll need", "qualifications", "must have", "minimum requirements"]
        for p in req_patterns:
            pos = text.find(p)
            if pos != -1 and (req_start == -1 or pos < req_start):
                req_start = pos

        pref_patterns = ["preferred", "nice to have", "plus", "bonus", "good to have", "desired"]
        for p in pref_patterns:
            pos = text.find(p)
            if pos != -1 and (pref_start == -1 or pos < pref_start):
                pref_start = pos

        req_section = ""
        pref_section = ""

        if req_start != -1 and pref_start != -1:
            if req_start < pref_start:
                req_section = text[req_start:pref_start]
                pref_section = text[pref_start:]
            else:
                pref_section = text[pref_start:req_start]
                req_section = text[req_start:]
        elif req_start != -1:
            req_section = text[req_start:]
        elif pref_start != -1:
            pref_section = text[pref_start:]

        return req_section, pref_section
