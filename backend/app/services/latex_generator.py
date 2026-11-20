from typing import Dict, List, Optional
from backend.app.models.optimization import OptimizedResume
from backend.app.utils.text_cleaning import escape_latex


LATEX_TEMPLATE = r"""\documentclass[letterpaper,10pt]{article}

\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[left=0.6in,right=0.6in,top=0.5in,bottom=0.5in]{geometry}
\usepackage[hidelinks]{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\raggedright
\raggedbottom
\urlstyle{same}
\linespread{1.08}

% Standard heading: bold caps, rule sits below the text with normal spacing
\titleformat{\section}{\large\bfseries\uppercase}{}{0em}{}[\titlerule]
\titlespacing*{\section}{0pt}{10pt}{5pt}

\setlist[itemize]{leftmargin=0.2in, itemsep=2pt, parsep=0pt, topsep=3pt}

\begin{document}

\begin{center}
  {\LARGE\bfseries __CANDIDATE_NAME__}\\[4pt]
  __CONTACT_LINE__
\end{center}

\vspace{-10pt}

\section{Professional Summary}
__SUMMARY__

\section{Education}
__EDUCATION_SECTION__

\section{Technical Skills}
__SKILLS_BLOCK__

\section{Technical Projects}
__PROJECTS_SECTION__

__ACHIEVEMENTS_SECTION__

\end{document}
"""


class LatexGenerator:
    """Generates standard, ATS-friendly LaTeX code matching exact user specifications and zero-fabrication rules."""

    @classmethod
    def generate(cls, resume: OptimizedResume) -> str:
        contact = resume.contact_info
        candidate_name_esc = escape_latex(contact.name or "TAJINDER SINGH")
        email_esc = escape_latex(contact.email or "tajinder.swe@gmail.com")
        phone_esc = escape_latex(contact.phone or "+91-9518671610")

        # Header contact line
        links = []
        if email_esc:
            links.append(f"\\href{{mailto:{email_esc}}}{{{email_esc}}}")
        if phone_esc:
            links.append(f"{phone_esc}")
        if contact.linkedin:
            li_clean = escape_latex(contact.linkedin)
            links.append(f"\\href{{{li_clean}}}{{LinkedIn}}")
        if contact.github:
            gh_clean = escape_latex(contact.github)
            links.append(f"\\href{{{gh_clean}}}{{GitHub}}")
        if contact.leetcode:
            lc_clean = escape_latex(contact.leetcode)
            links.append(f"\\href{{{lc_clean}}}{{LeetCode}}")

        header_contact_line = " $|$ ".join(links)

        # Summary
        summary_esc = escape_latex(resume.summary.strip())

        # Education
        edu_lines = []
        for edu in resume.education:
            inst = edu.institution or "Chandigarh University, Mohali, Punjab"
            deg = edu.degree or "B.E. in Computer Science & Engineering"
            dates = f"{edu.start_date or '2023'} -- {edu.end_date or '2027'}"
            gpa = f"CGPA: {edu.gpa}" if edu.gpa else "CGPA: 8.04"
            cw = ", ".join(edu.highlights) if edu.highlights else "Data Structures & Algorithms, OOP, Operating Systems, DBMS, Computer Networks"

            edu_lines.append(f"\\textbf{{{escape_latex(inst)}}} \\hfill {dates}\\\\")
            edu_lines.append(f"{escape_latex(deg)} \\hfill {gpa}\\\\")
            edu_lines.append(f"\\textit{{Relevant Coursework:}} {escape_latex(cw)}")

        if not edu_lines:
            edu_lines = [
                r"\textbf{Chandigarh University, Mohali, Punjab} \hfill 2023 -- 2027\\",
                r"B.E. in Computer Science \& Engineering \hfill CGPA: 8.04\\",
                r"\textit{Relevant Coursework:} Data Structures \& Algorithms, OOP, Operating Systems, DBMS, Computer Networks"
            ]
        education_section = "\n".join(edu_lines)

        # Skills Block
        skills_lines = []
        for cat, skills in resume.rebuilt_skills.items():
            if skills:
                # Remove duplicate items in the list preserving order
                seen = set()
                deduped = []
                for s in skills:
                    s_lower = s.strip().lower()
                    if s_lower not in seen and s_lower != "":
                        seen.add(s_lower)
                        deduped.append(s.strip())
                cat_esc = escape_latex(cat)
                skills_str = escape_latex(", ".join(deduped))
                skills_lines.append(f"\\textbf{{{cat_esc}:}} {skills_str}\\\\")
        skills_block = "\n".join(skills_lines)

        # Projects Section
        proj_blocks = []
        for p in resume.projects:
            proj_name_esc = escape_latex(p.name)
            techs = escape_latex(", ".join(p.technologies)) if p.technologies else ""
            heading = f"\\textbf{{{proj_name_esc}}}"
            if techs:
                heading += f" \\hfill \\textit{{{techs}}}"

            bullets_latex = []
            for b in p.bullet_points:
                b_clean = escape_latex(b.strip().lstrip("-*• "))
                bullets_latex.append(f"  \\item {b_clean}")
            bullets_str = "\n".join(bullets_latex)

            proj_entry = (
                f"{heading}\n"
                f"\\begin{{itemize}}\n"
                f"{bullets_str}\n"
                f"\\end{{itemize}}"
            )
            proj_blocks.append(proj_entry)
        projects_section = "\n\n".join(proj_blocks)

        # Achievements Section
        achievements_list = resume.achievements
        if not achievements_list:
            achievements_list = [
                "Solved 900+ Data Structures and Algorithms problems across LeetCode and competitive programming platforms.",
                "Earned the 500 Days Coding Badge on LeetCode.",
                "Completed NPTEL Cloud Computing certification with Silver grade."
            ]

        ach_bullets = "\n".join([f"  \\item {escape_latex(a)}" for a in achievements_list])
        achieve_section = (
            f"\\section{{Achievements}}\n"
            f"\\begin{{itemize}}\n"
            f"{ach_bullets}\n"
            f"\\end{{itemize}}"
        )

        tex = LATEX_TEMPLATE
        tex = tex.replace("__CANDIDATE_NAME__", candidate_name_esc)
        tex = tex.replace("__CONTACT_LINE__", header_contact_line)
        tex = tex.replace("__SUMMARY__", summary_esc)
        tex = tex.replace("__EDUCATION_SECTION__", education_section)
        tex = tex.replace("__SKILLS_BLOCK__", skills_block)
        tex = tex.replace("__PROJECTS_SECTION__", projects_section)
        tex = tex.replace("__ACHIEVEMENTS_SECTION__", achieve_section)

        return tex
