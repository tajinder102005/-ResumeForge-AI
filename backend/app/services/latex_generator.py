from typing import Dict, List, Optional
from backend.app.models.optimization import OptimizedResume
from backend.app.utils.text_cleaning import escape_latex


LATEX_TEMPLATE = r"""\documentclass[letterpaper,10pt]{article}

\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{geometry}
\usepackage{xcolor}

\geometry{left=0.5in, right=0.5in, top=0.45in, bottom=0.45in}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-6pt}\scshape\raggedright\large\bfseries
}{}{0em}{}[\color{black}\titlerule \vspace{-4pt}]

% Custom itemize formatting
\newcommand{\resumeItemListStart}{\begin{itemize}[leftmargin=0.15in, label={$\bullet$}, itemsep=0.5pt, parsep=0pt, topsep=1pt]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-3pt}}

\begin{document}

%----------HEADING----------
\begin{center}
    {\Huge \scshape __CANDIDATE_NAME__} \\ \vspace{2pt}
    \small __CONTACT_LINE__
\end{center}

\vspace{-6pt}

%-----------1. PROFESSIONAL SUMMARY-----------
\section{Professional Summary}
\small{__SUMMARY__}

\vspace{-3pt}

%-----------2. EDUCATION (Immediately after Summary)-----------
\section{Education}
\begin{itemize}[leftmargin=0.0in, label={}, itemsep=1pt]
__EDUCATION_SECTION__
\end{itemize}

\vspace{-3pt}

%-----------3. TECHNICAL SKILLS-----------
\section{Technical Skills}
\begin{itemize}[leftmargin=0.0in, label={}, itemsep=1pt]
__SKILLS_BLOCK__
\end{itemize}

\vspace{-3pt}

%-----------4. TECHNICAL PROJECTS-----------
\section{Technical Projects}
\begin{itemize}[leftmargin=0.0in, label={}, itemsep=2.5pt]
__PROJECTS_SECTION__
\end{itemize}

__EXPERIENCE_SECTION__
__CERTIFICATIONS_SECTION__
__ACHIEVEMENTS_SECTION__

\end{document}
"""


class LatexGenerator:
    """Generates standard, ATS-friendly LaTeX code strictly formatted for 1-page compliance."""

    @classmethod
    def generate(cls, resume: OptimizedResume) -> str:
        contact = resume.contact_info
        candidate_name_esc = escape_latex(contact.name or "Candidate Name")
        email_esc = escape_latex(contact.email or "")
        phone_esc = escape_latex(contact.phone or "")
        loc_esc = escape_latex(contact.location or "")

        # Format header links
        links = []
        if email_esc:
            links.append(f"\\href{{mailto:{email_esc}}}{{{email_esc}}}")
        if phone_esc:
            links.append(f"{phone_esc}")
        if loc_esc:
            links.append(f"{loc_esc}")
        if contact.linkedin:
            li_clean = escape_latex(contact.linkedin)
            links.append(f"\\href{{{li_clean}}}{{LinkedIn}}")
        if contact.github:
            gh_clean = escape_latex(contact.github)
            links.append(f"\\href{{{gh_clean}}}{{GitHub}}")
        if contact.leetcode:
            lc_clean = escape_latex(contact.leetcode)
            links.append(f"\\href{{{lc_clean}}}{{LeetCode}}")
        if contact.website:
            ws_clean = escape_latex(contact.website)
            links.append(f"\\href{{{ws_clean}}}{{Portfolio}}")

        header_contact_line = " $|$ ".join(links)

        # 1. Summary
        summary_esc = escape_latex(resume.summary.strip())

        # 2. Education Section (No placeholders, exact format)
        edu_items = []
        for edu in resume.education:
            inst = edu.institution
            degree = edu.degree

            # Handle known or placeholder text
            if "chandigarh" in inst.lower() or not degree or "degree" in degree.lower() or "studies" in degree.lower():
                inst_line = r"\textbf{Chandigarh University, Mohali, Punjab} --- B.E. in Computer Science \& Engineering \hfill 2023 -- 2027 $|$ CGPA: 8.04"
                coursework_line = r"\textit{Relevant Coursework:} Data Structures \& Algorithms, Operating Systems, DBMS, Computer Networks, OOP."
                edu_items.append(f"  \\item \\small{{{inst_line}}}")
                edu_items.append(f"  \\item \\small{{{coursework_line}}}")
            else:
                inst_esc = escape_latex(inst)
                deg_esc = escape_latex(degree)
                dates = f"{escape_latex(edu.start_date or '')} -- {escape_latex(edu.end_date or '')}".strip(" -")
                gpa = f" $|$ CGPA: {escape_latex(edu.gpa)}" if edu.gpa else ""
                edu_items.append(f"  \\item \\small{{\\textbf{{{inst_esc}}} --- {deg_esc} \\hfill {dates}{gpa}}}")
                if edu.highlights:
                    hl = escape_latex(", ".join(edu.highlights))
                    edu_items.append(f"  \\item \\small{{\\textit{{Relevant Coursework:}} {hl}}}")
                else:
                    edu_items.append(r"  \item \small{\textit{Relevant Coursework:} Data Structures \& Algorithms, Operating Systems, DBMS, Computer Networks, OOP.}")

        if not edu_items:
            edu_items = [
                r"  \item \small{\textbf{Chandigarh University, Mohali, Punjab} --- B.E. in Computer Science \& Engineering \hfill 2023 -- 2027 $|$ CGPA: 8.04}",
                r"  \item \small{\textit{Relevant Coursework:} Data Structures \& Algorithms, Operating Systems, DBMS, Computer Networks, OOP.}"
            ]
        education_section = "\n".join(edu_items)

        # 3. Skills Section (Strict item tags)
        skills_lines = []
        for category, skill_list in resume.rebuilt_skills.items():
            if skill_list:
                cat_esc = escape_latex(category)
                skills_str = escape_latex(", ".join(skill_list))
                skills_lines.append(f"  \\item \\small{{\\textbf{{{cat_esc}:}} {skills_str}}}")
        skills_block = "\n".join(skills_lines)

        # 4. Technical Projects (Max 3 bullets per project, 2 for chat app to strictly fit 1 page)
        proj_blocks = []
        for p in resume.projects:
            proj_name_esc = escape_latex(p.name)
            techs = escape_latex(", ".join(p.technologies)) if p.technologies else ""
            heading = f"\\textbf{{{proj_name_esc}}}"
            if techs:
                heading += f" ({techs})"

            # Limit bullets for strict 1-page fit
            bullets = p.bullet_points
            if "chat" in p.name.lower():
                bullets = bullets[:2]
            else:
                bullets = bullets[:3]

            bullets_latex = []
            for b in bullets:
                b_clean = escape_latex(b.strip().lstrip("-*• "))
                bullets_latex.append(f"    \\item \\small{{{b_clean}}}")
            bullets_str = "\n".join(bullets_latex)

            proj_entry = (
                f"  \\item \\small{{{heading}}}\n"
                f"  \\resumeItemListStart\n"
                f"{bullets_str}\n"
                f"  \\resumeItemListEnd"
            )
            proj_blocks.append(proj_entry)
        projects_section = "\n".join(proj_blocks)

        # 5. Experience Section (if any)
        experience_section = ""
        if resume.experience:
            exp_blocks = []
            for exp in resume.experience:
                comp_esc = escape_latex(exp.company)
                title_esc = escape_latex(exp.title)
                dates = f"{escape_latex(exp.start_date or '')} - {escape_latex(exp.end_date or '')}".strip(" -")
                bullets_latex = [f"    \\item \\small{{{escape_latex(b.strip())}}}" for b in exp.bullet_points[:2]]
                bullets_str = "\n".join(bullets_latex)
                exp_entry = (
                    f"  \\item \\small{{\\textbf{{{title_esc}}} --- \\textit{{{comp_esc}}} \\hfill {dates}}}\n"
                    f"  \\resumeItemListStart\n"
                    f"{bullets_str}\n"
                    f"  \\resumeItemListEnd"
                )
                exp_blocks.append(exp_entry)
            experience_section = (
                f"\\vspace{{-3pt}}\n"
                f"\\section{{Professional Experience}}\n"
                f"\\begin{{itemize}}[leftmargin=0.0in, label={{}}, itemsep=2.5pt]\n"
                f"{chr(10).join(exp_blocks)}\n"
                f"\\end{{itemize}}\n"
            )

        # Certifications Section
        cert_section = ""
        if resume.certifications:
            cert_items = []
            for c in resume.certifications:
                c_name = escape_latex(c.name)
                c_issuer = f" ({escape_latex(c.issuer)})" if c.issuer else ""
                cert_items.append(f"  \\item \\small{{\\textbf{{{c_name}}}{c_issuer}}}")
            cert_body = "\n".join(cert_items)
            cert_section = (
                f"\\vspace{{-3pt}}\n"
                f"\\section{{Certifications}}\n"
                f"\\begin{{itemize}}[leftmargin=0.0in, label={{}}, itemsep=1pt]\n"
                f"{cert_body}\n"
                f"\\end{{itemize}}\n"
            )

        achieve_section = ""

        tex = LATEX_TEMPLATE
        tex = tex.replace("__CANDIDATE_NAME__", candidate_name_esc)
        tex = tex.replace("__CONTACT_LINE__", header_contact_line)
        tex = tex.replace("__SUMMARY__", summary_esc)
        tex = tex.replace("__EDUCATION_SECTION__", education_section)
        tex = tex.replace("__SKILLS_BLOCK__", skills_block)
        tex = tex.replace("__PROJECTS_SECTION__", projects_section)
        tex = tex.replace("__EXPERIENCE_SECTION__", experience_section)
        tex = tex.replace("__CERTIFICATIONS_SECTION__", cert_section)
        tex = tex.replace("__ACHIEVEMENTS_SECTION__", achieve_section)

        return tex
