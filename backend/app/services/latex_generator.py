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

\geometry{left=0.55in, right=0.55in, top=0.5in, bottom=0.5in}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.15in}
\addtolength{\evensidemargin}{-0.15in}
\addtolength{\textwidth}{0.3in}
\addtolength{\topmargin}{-0.15in}
\addtolength{\textheight}{0.3in}

\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large\bfseries
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.98\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-6pt}
}

\newcommand{\resumeProjectHeading}[2]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.98\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-6pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}
\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.0in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}[leftmargin=0.15in, label={$\bullet$}, itemsep=1.5pt, parsep=0pt]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

%----------HEADING----------
\begin{center}
    {\Huge \scshape __CANDIDATE_NAME__} \\ \vspace{3pt}
    \small __CONTACT_LINE__
\end{center}

%-----------SUMMARY-----------
\section{Professional Summary}
\small{__SUMMARY__}

%-----------TECHNICAL SKILLS-----------
\section{Technical Skills}
\begin{itemize}[leftmargin=0.0in, label={}, itemsep=1pt]
  \small{
__SKILLS_BLOCK__
  }
\end{itemize}

%-----------EXPERIENCE-----------
\section{Professional Experience}
\resumeSubHeadingListStart
__EXPERIENCE_SECTION__
\resumeSubHeadingListEnd

%-----------PROJECTS-----------
\section{Technical Projects}
\resumeSubHeadingListStart
__PROJECTS_SECTION__
\resumeSubHeadingListEnd

%-----------EDUCATION-----------
\section{Education}
\resumeSubHeadingListStart
__EDUCATION_SECTION__
\resumeSubHeadingListEnd

__CERTIFICATIONS_SECTION__
__ACHIEVEMENTS_SECTION__

\end{document}
"""


class LatexGenerator:
    """Generates standard, ATS-friendly LaTeX code optimized for high parsing accuracy and Tectonic compilation."""

    @classmethod
    def generate(cls, resume: OptimizedResume) -> str:
        contact = resume.contact_info
        name_esc = escape_latex(contact.name or "Candidate Name")
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
        if contact.website:
            ws_clean = escape_latex(contact.website)
            links.append(f"\\href{{{ws_clean}}}{{Portfolio}}")

        header_contact_line = " $|$ ".join(links)

        # Build Skills Section
        skills_lines = []
        for category, skill_list in resume.rebuilt_skills.items():
            if skill_list:
                cat_esc = escape_latex(category)
                skills_str = escape_latex(", ".join(skill_list))
                skills_lines.append(f"  \\textbf{{{cat_esc}:}} {skills_str} \\\\")
        skills_block = "\n".join(skills_lines)

        # Build Experience Section
        exp_blocks = []
        for exp in resume.experience:
            comp_esc = escape_latex(exp.company)
            title_esc = escape_latex(exp.title)
            loc_exp = escape_latex(exp.location or "")
            dates = f"{escape_latex(exp.start_date or '')} - {escape_latex(exp.end_date or ('Present' if exp.current else ''))}".strip(" -")
            
            bullets_latex = []
            for b in exp.bullet_points:
                b_esc = escape_latex(b)
                bullets_latex.append(f"    \\item {b_esc}")
            bullets_str = "\n".join(bullets_latex)

            exp_entry = (
                f"  \\resumeSubheading\n"
                f"    {{{title_esc}}}{{{dates}}}\n"
                f"    {{{comp_esc}}}{{{loc_exp}}}\n"
                f"  \\resumeItemListStart\n"
                f"{bullets_str}\n"
                f"  \\resumeItemListEnd"
            )
            exp_blocks.append(exp_entry)
        experience_section = "\n".join(exp_blocks)

        # Build Projects Section
        proj_blocks = []
        for p in resume.projects:
            name_proj = escape_latex(p.name)
            techs = escape_latex(" | ".join(p.technologies)) if p.technologies else ""
            link_str = f" $|$ \\href{{{escape_latex(p.link)}}}{{Link}}" if p.link else ""
            
            bullets_latex = []
            for b in p.bullet_points:
                b_esc = escape_latex(b)
                bullets_latex.append(f"    \\item {b_esc}")
            bullets_str = "\n".join(bullets_latex)

            proj_entry = (
                f"  \\resumeProjectHeading\n"
                f"    {{\\textbf{{{name_proj}}} $|$ \\emph{{{techs}}}{link_str}}}{{}}\n"
                f"  \\resumeItemListStart\n"
                f"{bullets_str}\n"
                f"  \\resumeItemListEnd"
            )
            proj_blocks.append(proj_entry)
        projects_section = "\n".join(proj_blocks)

        # Build Education Section
        edu_blocks = []
        for edu in resume.education:
            inst_esc = escape_latex(edu.institution)
            deg_esc = escape_latex(edu.degree)
            field_esc = f" in {escape_latex(edu.field_of_study)}" if edu.field_of_study else ""
            dates_edu = f"{escape_latex(edu.start_date or '')} - {escape_latex(edu.end_date or '')}".strip(" -")
            gpa_str = f" (GPA: {escape_latex(edu.gpa)})" if edu.gpa else ""

            edu_entry = (
                f"  \\resumeSubheading\n"
                f"    {{{inst_esc}}}{{{dates_edu}}}\n"
                f"    {{{deg_esc}{field_esc}{gpa_str}}}{{}}"
            )
            edu_blocks.append(edu_entry)
        education_section = "\n".join(edu_blocks)

        summary_esc = escape_latex(resume.summary)

        # Certifications Section
        cert_section = ""
        if resume.certifications:
            cert_items = []
            for c in resume.certifications:
                c_name = escape_latex(c.name)
                c_issuer = f" ({escape_latex(c.issuer)})" if c.issuer else ""
                cert_items.append(f"  \\item \\textbf{{{c_name}}}{c_issuer}")
            cert_body = "\n".join(cert_items)
            cert_section = (
                f"\\section{{Certifications}}\n"
                f"\\resumeItemListStart\n"
                f"{cert_body}\n"
                f"\\resumeItemListEnd\n"
            )

        # Achievements Section
        achieve_section = ""
        if resume.achievements:
            ach_items = []
            for a in resume.achievements:
                ach_items.append(f"  \\item {escape_latex(a)}")
            ach_body = "\n".join(ach_items)
            achieve_section = (
                f"\\section{{Achievements \\& Honors}}\n"
                f"\\resumeItemListStart\n"
                f"{ach_body}\n"
                f"\\resumeItemListEnd\n"
            )

        tex = LATEX_TEMPLATE
        tex = tex.replace("__CANDIDATE_NAME__", name_esc)
        tex = tex.replace("__CONTACT_LINE__", header_contact_line)
        tex = tex.replace("__SUMMARY__", summary_esc)
        tex = tex.replace("__SKILLS_BLOCK__", skills_block)
        tex = tex.replace("__EXPERIENCE_SECTION__", experience_section)
        tex = tex.replace("__PROJECTS_SECTION__", projects_section)
        tex = tex.replace("__EDUCATION_SECTION__", education_section)
        tex = tex.replace("__CERTIFICATIONS_SECTION__", cert_section)
        tex = tex.replace("__ACHIEVEMENTS_SECTION__", achieve_section)

        return tex
