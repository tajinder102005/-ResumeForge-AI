from pathlib import Path
from typing import Dict, List, Optional
from backend.app.config import settings
from backend.app.models.optimization import OptimizedResume
from backend.app.utils.text_cleaning import escape_latex

# Common Preamble Snippets
FA_COMMON = r"""\usepackage{fontawesome5}
\definecolor{navy}{RGB}{15, 43, 92}
\definecolor{iconblue}{RGB}{2, 111, 199}
\newcommand{\iconlink}[3]{{\color{iconblue}#1}\,\href{#2}{#3}}
"""

# -------------------------------------------------------------
# 1. TEMPLATE: MODERN MINIMALIST (Clean Crisp ATS Monochrome)
# -------------------------------------------------------------
TEMPLATE_MODERN = r"""\documentclass[letterpaper,10pt]{article}

\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[left=0.5in,right=0.5in,top=0.42in,bottom=0.42in]{geometry}
\usepackage[hidelinks]{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{fontawesome5}

\definecolor{navy}{RGB}{20, 20, 20}
\definecolor{iconblue}{RGB}{2, 111, 199}
\newcommand{\iconlink}[3]{{\color{iconblue}#1}\,\href{#2}{#3}}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\raggedright
\raggedbottom
\urlstyle{same}
\linespread{1.04}

% Modern minimalist heading: bold caps, clean rule
\titleformat{\section}{\large\bfseries\uppercase}{}{0em}{}[\titlerule]
\titlespacing*{\section}{0pt}{8pt}{3pt}

\setlist[itemize]{leftmargin=0.18in, itemsep=1.5pt, parsep=0pt, topsep=2pt}

\begin{document}

__HEADER_BLOCK__

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

# -------------------------------------------------------------
# 2. TEMPLATE: CLASSIC IVY LEAGUE (Academic Serif Elegance)
# -------------------------------------------------------------
TEMPLATE_CLASSIC = r"""\documentclass[letterpaper,10pt]{article}

\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage[left=0.52in,right=0.52in,top=0.42in,bottom=0.42in]{geometry}
\usepackage[hidelinks]{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{fontawesome5}

\definecolor{navy}{RGB}{15, 43, 92}
\definecolor{iconblue}{RGB}{15, 43, 92}
\newcommand{\iconlink}[3]{{\color{iconblue}#1}\,\href{#2}{#3}}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\raggedright
\raggedbottom
\urlstyle{same}
\linespread{1.04}

% Classic Ivy League heading: small-caps, traditional rule
\titleformat{\section}{\large\scshape\bfseries}{}{0em}{}[\titlerule]
\titlespacing*{\section}{0pt}{8pt}{3pt}

\setlist[itemize]{leftmargin=0.18in, itemsep=1.5pt, parsep=0pt, topsep=2pt}

\begin{document}

__HEADER_BLOCK__

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

# -------------------------------------------------------------
# 3. TEMPLATE: TECH MODERN ACCENT (Crisp Sans-Serif Navy Accent)
# -------------------------------------------------------------
TEMPLATE_TECH = r"""\documentclass[letterpaper,10pt]{article}

\usepackage[T1]{fontenc}
\usepackage[scaled=0.92]{helvet}
\renewcommand\familydefault{\sfdefault}
\usepackage[left=0.5in,right=0.5in,top=0.42in,bottom=0.42in]{geometry}
\usepackage[hidelinks]{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{fontawesome5}

\definecolor{techblue}{RGB}{15, 60, 120}
\definecolor{navy}{RGB}{15, 60, 120}
\definecolor{iconblue}{RGB}{2, 111, 199}
\newcommand{\iconlink}[3]{{\color{iconblue}#1}\,\href{#2}{#3}}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\raggedright
\raggedbottom
\urlstyle{same}
\linespread{1.04}

% Modern Tech Accent heading: navy colored rule & uppercase
\titleformat{\section}{\color{techblue}\large\bfseries}{}{0em}{\uppercase}[\color{techblue}\titlerule]
\titlespacing*{\section}{0pt}{8pt}{3pt}

\setlist[itemize]{leftmargin=0.18in, itemsep=1.5pt, parsep=0pt, topsep=2pt}

\begin{document}

__HEADER_BLOCK__

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

# -------------------------------------------------------------
# 4. TEMPLATE: GOLDEN & ONYX LUXURY (Metallic Gold & Charcoal)
# -------------------------------------------------------------
TEMPLATE_GOLD = r"""\documentclass[letterpaper,10pt]{article}

\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[left=0.5in,right=0.5in,top=0.42in,bottom=0.42in]{geometry}
\usepackage[hidelinks]{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{fontawesome5}

\definecolor{goldaccent}{RGB}{184, 134, 11}
\definecolor{onyxblack}{RGB}{18, 18, 18}
\definecolor{navy}{RGB}{18, 18, 18}
\definecolor{iconblue}{RGB}{184, 134, 11}
\newcommand{\iconlink}[3]{{\color{iconblue}#1}\,\href{#2}{#3}}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\raggedright
\raggedbottom
\urlstyle{same}
\linespread{1.04}

% Luxury Gold & Onyx heading: gold thick rule
\titleformat{\section}
  {\large\bfseries\color{onyxblack}}
  {}{0em}
  {\uppercase}
  [{\color{goldaccent}\titlerule[1.5pt]}]
\titlespacing*{\section}{0pt}{8pt}{4pt}

\setlist[itemize]{leftmargin=0.18in, itemsep=1.5pt, parsep=0pt, topsep=2pt}

\begin{document}

__HEADER_BLOCK__

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

# -------------------------------------------------------------
# 5. TEMPLATE: NAVY BLUE BANNER (Shaded Full-Width Section Boxes)
# Matches Rohan Malhotra style from user screenshot
# -------------------------------------------------------------
TEMPLATE_NAVY = r"""\documentclass[letterpaper,10pt]{article}

\usepackage[T1]{fontenc}
\usepackage[scaled=0.92]{helvet}
\renewcommand\familydefault{\sfdefault}
\usepackage[left=0.5in,right=0.5in,top=0.42in,bottom=0.42in]{geometry}
\usepackage[hidelinks]{hyperref}
\usepackage{enumitem}
\usepackage[explicit]{titlesec}
\usepackage{xcolor}
\usepackage{fontawesome5}

\definecolor{navyaccent}{RGB}{15, 43, 92}
\definecolor{navybanner}{RGB}{230, 238, 248}
\definecolor{navy}{RGB}{15, 43, 92}
\definecolor{iconblue}{RGB}{2, 111, 199}
\newcommand{\iconlink}[3]{{\color{iconblue}#1}\,\href{#2}{#3}}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\raggedright
\raggedbottom
\urlstyle{same}
\linespread{1.04}

% Shaded full-width banner heading
\titleformat{\section}
  {\normalfont\large\bfseries\color{navyaccent}}
  {}{0em}
  {\colorbox{navybanner}{\parbox{\dimexpr\linewidth-2\fboxsep}{\strut\uppercase{#1}}}}
\titlespacing*{\section}{0pt}{8pt}{4pt}

\setlist[itemize]{leftmargin=0.18in, itemsep=1.5pt, parsep=0pt, topsep=2pt}

\begin{document}

__HEADER_BLOCK__

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

# -------------------------------------------------------------
# 6. TEMPLATE: EMERALD MODERN BANNER (Deep Forest Emerald & Mint)
# -------------------------------------------------------------
TEMPLATE_EMERALD = r"""\documentclass[letterpaper,10pt]{article}

\usepackage[T1]{fontenc}
\usepackage[scaled=0.92]{helvet}
\renewcommand\familydefault{\sfdefault}
\usepackage[left=0.5in,right=0.5in,top=0.42in,bottom=0.42in]{geometry}
\usepackage[hidelinks]{hyperref}
\usepackage{enumitem}
\usepackage[explicit]{titlesec}
\usepackage{xcolor}
\usepackage{fontawesome5}

\definecolor{emeraldaccent}{RGB}{13, 92, 58}
\definecolor{emeraldbanner}{RGB}{233, 246, 239}
\definecolor{navy}{RGB}{13, 92, 58}
\definecolor{iconblue}{RGB}{13, 92, 58}
\newcommand{\iconlink}[3]{{\color{iconblue}#1}\,\href{#2}{#3}}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\raggedright
\raggedbottom
\urlstyle{same}
\linespread{1.04}

% Shaded emerald banner heading
\titleformat{\section}
  {\normalfont\large\bfseries\color{emeraldaccent}}
  {}{0em}
  {\colorbox{emeraldbanner}{\parbox{\dimexpr\linewidth-2\fboxsep}{\strut\uppercase{#1}}}}
\titlespacing*{\section}{0pt}{8pt}{4pt}

\setlist[itemize]{leftmargin=0.18in, itemsep=1.5pt, parsep=0pt, topsep=2pt}

\begin{document}

__HEADER_BLOCK__

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

# -------------------------------------------------------------
# 7. TEMPLATE: SIDEBAR WITH PHOTO AVATAR (2-Column Executive)
# Matches Michael Johnson style from user screenshot
# -------------------------------------------------------------
# 7. TEMPLATE: EXECUTIVE SQUARE PHOTO (Clean Modern Banner with Square Headshot)
# Matches Catherine Bale style from user screenshot (Image 4)
# -------------------------------------------------------------
TEMPLATE_SIDEBAR_PHOTO = r"""\documentclass[letterpaper,10pt]{article}

\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[left=0.55in,right=0.55in,top=0.42in,bottom=0.42in]{geometry}
\usepackage[hidelinks]{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{tikz}
\usepackage{fontawesome5}

\definecolor{headerdark}{RGB}{20, 25, 35}
\definecolor{accentgreen}{RGB}{35, 95, 65}
\definecolor{accentstrip}{RGB}{35, 95, 65}
\definecolor{lightgray}{RGB}{210, 218, 226}
\definecolor{iconblue}{RGB}{2, 111, 199}
\definecolor{slate}{RGB}{100, 115, 130}

\newcommand{\iconlink}[3]{{\color{iconblue}#1}\,\href{#2}{#3}}

\pagestyle{empty}
\setlength{\parindent}{0pt}
\raggedright
\raggedbottom
\urlstyle{same}
\linespread{1.04}

% Clean modern section heading with rule
\titleformat{\section}{\large\bfseries\color{headerdark}}{}{0em}{}[\color{headerdark}\titlerule]
\titlespacing*{\section}{0pt}{7pt}{3pt}

\setlist[itemize]{leftmargin=0.18in, itemsep=1.5pt, parsep=0pt, topsep=2pt}

\begin{document}

% Left accent vertical strip (Catherine Bale style)
\begin{tikzpicture}[remember picture,overlay]
  \fill[accentstrip] (current page.north west) rectangle ([xshift=0.18in]current page.south west);
\end{tikzpicture}

% Header: Candidate Details on Left, Square Photo on Right
\noindent
\begin{minipage}[t]{0.74\linewidth}
  \vspace{0pt}
  {\Huge\bfseries\color{headerdark} __CANDIDATE_NAME__}\\[3pt]
  {\large\itshape\color{accentgreen} __TARGET_ROLE__}\\[6pt]
  \small
  {\color{iconblue}\faMapMarker*}\, __LOCATION__
  \quad{\color{iconblue}\textbar}\quad
  {\color{iconblue}\faPhone*}\, __PHONE__
  \quad{\color{iconblue}\textbar}\quad
  \iconlink{\faEnvelope}{mailto:__EMAIL__}{__EMAIL__}\\[4pt]
  \iconlink{\faLinkedin}{__LINKEDIN_URL__}{tajinderasingh}
  \quad{\color{iconblue}\textbar}\quad
  \iconlink{\faGithub}{__GITHUB_URL__}{tajinder102005}
  \quad{\color{iconblue}\textbar}\quad
  \iconlink{\faCode}{__LEETCODE_URL__}{Rednijat123}
  \quad{\color{iconblue}\textbar}\quad
  \iconlink{\faGlobe}{__PORTFOLIO_URL__}{Portfolio}
\end{minipage}%
\hfill
\begin{minipage}[t]{0.23\linewidth}
  \vspace{0pt}
  \raggedleft
  __AVATAR_BLOCK__
\end{minipage}

\vspace{6pt}
\hrule height 0.6pt
\vspace{4pt}

\section{Profile}
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
    """Generates standard, ATS-friendly LaTeX code supporting multiple visually striking themes."""

    TEMPLATES = {
        "modern": TEMPLATE_MODERN,
        "classic": TEMPLATE_CLASSIC,
        "tech": TEMPLATE_TECH,
        "gold": TEMPLATE_GOLD,
        "golden": TEMPLATE_GOLD,
        "navy": TEMPLATE_NAVY,
        "navy_blue": TEMPLATE_NAVY,
        "emerald": TEMPLATE_EMERALD,
        "sidebar_photo": TEMPLATE_SIDEBAR_PHOTO,
        "sidebar": TEMPLATE_SIDEBAR_PHOTO,
        "photo": TEMPLATE_SIDEBAR_PHOTO,
        "executive_photo": TEMPLATE_SIDEBAR_PHOTO,
        "square_photo": TEMPLATE_SIDEBAR_PHOTO,
    }

    @classmethod
    def generate(
        cls,
        resume: OptimizedResume,
        template_name: str = "modern",
        photo_filename: Optional[str] = None
    ) -> str:
        tpl_key = template_name.lower().strip() if template_name else "modern"
        base_template = cls.TEMPLATES.get(tpl_key, TEMPLATE_MODERN)

        contact = resume.contact_info
        raw_name = contact.name or "Tajinder Singh"
        if raw_name.isupper():
            raw_name = raw_name.title()
        candidate_name_esc = escape_latex(raw_name)
        email_esc = escape_latex(contact.email or "tajinder.swe@gmail.com")
        phone_esc = escape_latex(contact.phone or "+91-9518671610")
        loc_esc = escape_latex(contact.location or "Yamuna Nagar, Haryana, India")

        linkedin_url = contact.linkedin or "https://linkedin.com/in/tajinderasingh"
        github_url = contact.github or "https://github.com/tajinder102005"
        leetcode_url = contact.leetcode or "https://leetcode.com/u/Rednijat123/"
        portfolio_url = contact.portfolio or contact.website or "https://portfolio-website1-n47b.vercel.app/"

        target_role_esc = escape_latex(resume.job_title or "Software Engineer")

        # -----------------------------------------------------------------
        # 2-Line Header Block with FontAwesome 5 Icons & Portfolio Website
        # Exactly matching user's requested layout:
        # Line 1: MapMarker, Phone, Envelope
        # Line 2: LinkedIn, GitHub, LeetCode, Globe (Portfolio)
        # -----------------------------------------------------------------
        header_block = (
            "\\begin{center}\n"
            f"    {{\\Huge\\bfseries\\color{{navy}} {candidate_name_esc}}}\\\\[7pt]\n"
            "    \\small\n"
            f"    {{\\color{{iconblue}}\\faMapMarker*}}\\, {loc_esc}\n"
            "    \\quad{\\color{iconblue}\\textbar}\\quad\n"
            f"    {{\\color{{iconblue}}\\faPhone*}}\\, {phone_esc}\n"
            "    \\quad{\\color{iconblue}\\textbar}\\quad\n"
            f"    \\iconlink{{\\faEnvelope}}{{mailto:{email_esc}}}{{{email_esc}}}\\\\[5pt]\n"
            f"    \\iconlink{{\\faLinkedin}}{{{escape_latex(linkedin_url)}}}{{tajinderasingh}}\n"
            "    \\quad{\\color{iconblue}\\textbar}\\quad\n"
            f"    \\iconlink{{\\faGithub}}{{{escape_latex(github_url)}}}{{tajinder102005}}\n"
            "    \\quad{\\color{iconblue}\\textbar}\\quad\n"
            f"    \\iconlink{{\\faCode}}{{{escape_latex(leetcode_url)}}}{{Rednijat123}}\n"
            "    \\quad{\\color{iconblue}\\textbar}\\quad\n"
            f"    \\iconlink{{\\faGlobe}}{{{escape_latex(portfolio_url)}}}{{Portfolio}}\n"
            "\\end{center}\n"
            "\\vspace{-6pt}"
        )

        # Summary
        summary_esc = escape_latex(resume.summary.strip())

        # Education (1-column standard)
        edu_lines = []
        for edu in resume.education:
            inst = edu.institution or "Chandigarh University, Mohali, Punjab"
            deg = edu.degree or "B.E. in Computer Science & Engineering"
            dates = f"{edu.start_date or '2023'} -- {edu.end_date or '2027'}"
            gpa = f"CGPA: {edu.gpa}" if edu.gpa else "CGPA: 8.04"
            cw = ", ".join(edu.highlights) if edu.highlights else "Data Structures & Algorithms, OOP, Operating Systems, DBMS, Computer Networks, Multithreading"

            edu_lines.append(f"\\textbf{{{escape_latex(inst)}}} \\hfill {dates}\\\\")
            edu_lines.append(f"{escape_latex(deg)} \\hfill {gpa}\\\\")
            edu_lines.append(f"\\textit{{Relevant Coursework:}} {escape_latex(cw)}")

        if not edu_lines:
            edu_lines = [
                r"\textbf{Chandigarh University, Mohali, Punjab} \hfill 2023 -- 2027\\",
                r"B.E. in Computer Science \& Engineering \hfill CGPA: 8.04\\",
                r"\textit{Relevant Coursework:} Data Structures \& Algorithms, OOP, Operating Systems, DBMS, Computer Networks, Multithreading"
            ]
        education_section = "\n".join(edu_lines)

        # Education (Sidebar compact)
        sidebar_edu_lines = []
        for edu in resume.education:
            inst = edu.institution or "Chandigarh University"
            deg = edu.degree or "B.E. Computer Science"
            dates = f"{edu.start_date or '2023'} -- {edu.end_date or '2027'}"
            gpa = f"CGPA: {edu.gpa}" if edu.gpa else "CGPA: 8.04"
            sidebar_edu_lines.append(f"\\textbf{{{escape_latex(inst)}}}\\\\[2pt]")
            sidebar_edu_lines.append(f"{escape_latex(deg)}\\\\[2pt]")
            sidebar_edu_lines.append(f"{dates} $|$ {gpa}\\\\[6pt]")
        if not sidebar_edu_lines:
            sidebar_edu_lines = [
                r"\textbf{Chandigarh University}\\[2pt]",
                r"B.E. Computer Science\\[2pt]",
                r"2023 -- 2027 $|$ CGPA: 8.04\\[6pt]"
            ]
        sidebar_education = "\n".join(sidebar_edu_lines)

        # Skills Block (1-column standard)
        skills_lines = []
        sidebar_skills_lines = []
        for cat, skills in resume.rebuilt_skills.items():
            if not skills:
                continue
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(",") if s.strip()]
            seen = set()
            deduped = []
            for s in skills:
                s_str = str(s).strip()
                s_lower = s_str.lower()
                if s_lower not in seen and s_lower != "":
                    seen.add(s_lower)
                    deduped.append(s_str)
            if deduped:
                cat_esc = escape_latex(cat)
                skills_str = escape_latex(", ".join(deduped))
                skills_lines.append(f"\\textbf{{{cat_esc}:}} {skills_str}\\\\")
                sidebar_skills_lines.append(f"\\textbf{{{cat_esc}:}}\\\\ {skills_str}\\\\[4pt]")

        skills_block = "\n".join(skills_lines)
        sidebar_skills = "\n".join(sidebar_skills_lines)

        # Sidebar Contact Block with FontAwesome Icons
        sb_contacts = [
            f"{{\\color{{accentgold}}\\faMapMarker*}}\\, {loc_esc}\\\\[4pt]",
            f"{{\\color{{accentgold}}\\faPhone*}}\\, {phone_esc}\\\\[4pt]",
            f"{{\\color{{accentgold}}\\faEnvelope}}\\, \\href{{mailto:{email_esc}}}{{{email_esc}}}\\\\[4pt]",
            f"{{\\color{{accentgold}}\\faLinkedin}}\\, \\href{{{escape_latex(linkedin_url)}}}{{LinkedIn Profile}}\\\\[4pt]",
            f"{{\\color{{accentgold}}\\faGithub}}\\, \\href{{{escape_latex(github_url)}}}{{GitHub Profile}}\\\\[4pt]",
            f"{{\\color{{accentgold}}\\faCode}}\\, \\href{{{escape_latex(leetcode_url)}}}{{LeetCode Profile}}\\\\[4pt]",
            f"{{\\color{{accentgold}}\\faGlobe}}\\, \\href{{{escape_latex(portfolio_url)}}}{{Portfolio Website}}\\\\[4pt]",
        ]
        sidebar_contact = "\n".join(sb_contacts)

        # Avatar Block (for sidebar_photo)
        tex_dir = settings.STORAGE_DIR / "tex"
        photos_dir = settings.STORAGE_DIR / "photos"
        photo_found = None

        if photo_filename:
            for d in [tex_dir, photos_dir]:
                p = d / photo_filename
                if p.exists():
                    photo_found = p.resolve().as_posix()
                    break

        if not photo_found:
            for ext in [".png", ".jpg", ".jpeg"]:
                for d in [tex_dir, photos_dir]:
                    candidate = d / f"photo_{resume.resume_id}{ext}"
                    if candidate.exists():
                        photo_found = candidate.resolve().as_posix()
                        break
                if photo_found:
                    break

        if photo_found:
            avatar_block = (
                r"\begin{tikzpicture}"
                r"\draw[lightgray, line width=0.8pt, rounded corners=3pt] (-0.02in,-0.02in) rectangle (1.27in, 1.27in);"
                r"\clip[rounded corners=2pt] (0,0) rectangle (1.25in, 1.25in);"
                f"\\node[anchor=south west, inner sep=0pt] at (0,0) {{\\includegraphics[width=1.25in,height=1.25in]{{{photo_found}}}}};"
                r"\end{tikzpicture}"
            )
        else:
            avatar_block = (
                r"\begin{tikzpicture}"
                r"\draw[lightgray, fill=slate!8, line width=0.8pt, rounded corners=2pt] (0,0) rectangle (1.25in, 1.25in);"
                r"\node at (0.625in, 0.625in) {\color{accentgreen}\Huge\faUser};"
                r"\end{tikzpicture}"
            )

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
                if b_clean:
                    bullets_latex.append(f"  \\item {b_clean}")
            
            if not bullets_latex:
                continue

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
                "Solved 1000+ Data Structures and Algorithms problems across LeetCode and competitive programming platforms.",
                "Earned the 500 Days Coding Badge on LeetCode.",
                "Completed NPTEL Cloud Computing certification with Silver grade.",
                "Participated in multiple hackathons, applying software development and problem-solving skills to build solutions under time constraints."
            ]

        ach_bullets = "\n".join([f"  \\item {escape_latex(a)}" for a in achievements_list])
        
        achieve_section = (
            f"\\section{{Achievements}}\n"
            f"\\begin{{itemize}}\n"
            f"{ach_bullets}\n"
            f"\\end{{itemize}}"
        )

        tex = base_template
        tex = tex.replace("__HEADER_BLOCK__", header_block)
        tex = tex.replace("__CANDIDATE_NAME__", candidate_name_esc)
        tex = tex.replace("__TARGET_ROLE__", target_role_esc)
        tex = tex.replace("__LOCATION__", loc_esc)
        tex = tex.replace("__PHONE__", phone_esc)
        tex = tex.replace("__EMAIL__", email_esc)
        tex = tex.replace("__LINKEDIN_URL__", escape_latex(linkedin_url))
        tex = tex.replace("__GITHUB_URL__", escape_latex(github_url))
        tex = tex.replace("__LEETCODE_URL__", escape_latex(leetcode_url))
        tex = tex.replace("__PORTFOLIO_URL__", escape_latex(portfolio_url))
        tex = tex.replace("__AVATAR_BLOCK__", avatar_block)
        tex = tex.replace("__SUMMARY__", summary_esc)
        tex = tex.replace("__EDUCATION_SECTION__", education_section)
        tex = tex.replace("__SKILLS_BLOCK__", skills_block)
        tex = tex.replace("__PROJECTS_SECTION__", projects_section)
        tex = tex.replace("__ACHIEVEMENTS_SECTION__", achieve_section)
        
        # Legacy sidebar placeholders (if any)
        tex = tex.replace("__SIDEBAR_CONTACT__", sidebar_contact)
        tex = tex.replace("__SIDEBAR_SKILLS__", sidebar_skills)
        tex = tex.replace("__SIDEBAR_EDUCATION__", sidebar_education)

        return tex
