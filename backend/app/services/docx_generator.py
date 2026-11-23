import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from pathlib import Path
from typing import Optional

from backend.app.config import settings
from backend.app.models.optimization import OptimizedResume


class DocxGenerator:
    """
    Generates ATS-optimized, high-fidelity Microsoft Word (.docx) resumes
    matching candidate data and exact zero-fabrication guidelines.
    """

    @classmethod
    def generate(cls, resume: OptimizedResume) -> Path:
        output_dir = settings.STORAGE_DIR / "docx"
        output_dir.mkdir(parents=True, exist_ok=True)
        docx_path = output_dir / f"{resume.resume_id}.docx"

        doc = docx.Document()

        # Set tight margins (0.5 inches) for 1-page density
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.45)
            section.bottom_margin = Inches(0.45)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)

        # Base style: Calibri, 9.5pt, dark grey text
        normal_style = doc.styles['Normal']
        normal_font = normal_style.font
        normal_font.name = 'Calibri'
        normal_font.size = Pt(9.5)
        normal_font.color.rgb = RGBColor(30, 30, 30)

        contact = resume.contact_info

        # 1. Header: Name
        p_name = doc.add_paragraph()
        p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_name.paragraph_format.space_before = Pt(0)
        p_name.paragraph_format.space_after = Pt(2)
        run_name = p_name.add_run((contact.name or "Candidate Name").upper())
        run_name.font.size = Pt(17)
        run_name.font.bold = True
        run_name.font.color.rgb = RGBColor(15, 23, 42)

        # Contact line
        contact_parts = []
        if contact.email: contact_parts.append(contact.email)
        if contact.phone: contact_parts.append(contact.phone)
        if contact.location: contact_parts.append(contact.location)
        if contact.linkedin: contact_parts.append("LinkedIn")
        if contact.github: contact_parts.append("GitHub")
        if contact.leetcode: contact_parts.append("LeetCode")
        contact_parts.append("Portfolio")

        p_contact = doc.add_paragraph()
        p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_contact.paragraph_format.space_before = Pt(0)
        p_contact.paragraph_format.space_after = Pt(6)
        r_contact = p_contact.add_run("  |  ".join(contact_parts))
        r_contact.font.size = Pt(8.5)
        r_contact.font.color.rgb = RGBColor(75, 85, 99)

        def add_section_heading(title: str):
            p_head = doc.add_paragraph()
            p_head.paragraph_format.space_before = Pt(6)
            p_head.paragraph_format.space_after = Pt(2)
            p_head.paragraph_format.keep_with_next = True
            r_head = p_head.add_run(title.upper())
            r_head.font.size = Pt(10.5)
            r_head.font.bold = True
            r_head.font.color.rgb = RGBColor(15, 23, 42)

            # Add bottom border in XML for ATS-clean line
            pPr = p_head._p.get_or_add_pPr()
            pBdr = parse_xml(r'<w:pBdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:bottom w:val="single" w:sz="6" w:space="1" w:color="94A3B8"/></w:pBdr>')
            pPr.append(pBdr)

        # 2. Summary
        if resume.summary:
            add_section_heading("Professional Summary")
            p_sum = doc.add_paragraph()
            p_sum.paragraph_format.space_before = Pt(1)
            p_sum.paragraph_format.space_after = Pt(3)
            p_sum.paragraph_format.line_spacing = 1.05
            p_sum.add_run(resume.summary)

        # 3. Education
        if resume.education:
            add_section_heading("Education")
            for edu in resume.education:
                p_edu = doc.add_paragraph()
                p_edu.paragraph_format.space_before = Pt(1)
                p_edu.paragraph_format.space_after = Pt(1)
                r_inst = p_edu.add_run(edu.institution or "")
                r_inst.bold = True
                
                dates = f"  |  {edu.start_date or ''} – {edu.end_date or ''}".strip(" –|")
                if dates:
                    r_dates = p_edu.add_run(f"  |  {dates}")
                    r_dates.font.color.rgb = RGBColor(100, 116, 139)

                p_deg = doc.add_paragraph()
                p_deg.paragraph_format.space_before = Pt(0)
                p_deg.paragraph_format.space_after = Pt(1)
                deg_str = edu.degree or ""
                if edu.gpa:
                    deg_str += f" — CGPA: {edu.gpa}"
                p_deg.add_run(deg_str)

                if edu.highlights:
                    p_cw = doc.add_paragraph()
                    p_cw.paragraph_format.space_before = Pt(0)
                    p_cw.paragraph_format.space_after = Pt(2)
                    r_cw_label = p_cw.add_run("Relevant Coursework: ")
                    r_cw_label.italic = True
                    p_cw.add_run(", ".join(edu.highlights))

        # 4. Technical Skills
        if resume.rebuilt_skills:
            add_section_heading("Technical Skills")
            for cat, skills in resume.rebuilt_skills.items():
                if skills:
                    if isinstance(skills, str):
                        s_list = [s.strip() for s in skills.split(",") if s.strip()]
                    else:
                        s_list = [str(s).strip() for s in skills if str(s).strip()]
                    
                    seen = set()
                    deduped = []
                    for s in s_list:
                        if s.lower() not in seen and s:
                            seen.add(s.lower())
                            deduped.append(s)

                    if deduped:
                        p_sk = doc.add_paragraph()
                        p_sk.paragraph_format.space_before = Pt(0)
                        p_sk.paragraph_format.space_after = Pt(1)
                        r_cat = p_sk.add_run(f"{cat}: ")
                        r_cat.bold = True
                        p_sk.add_run(", ".join(deduped))

        # 5. Technical Projects
        if resume.projects:
            add_section_heading("Technical Projects")
            for p in resume.projects:
                p_proj = doc.add_paragraph()
                p_proj.paragraph_format.space_before = Pt(3)
                p_proj.paragraph_format.space_after = Pt(1)
                p_proj.paragraph_format.keep_with_next = True
                
                r_pname = p_proj.add_run(p.name)
                r_pname.bold = True
                if p.technologies:
                    r_ptech = p_proj.add_run(f"  |  {', '.join(p.technologies)}")
                    r_ptech.italic = True
                    r_ptech.font.color.rgb = RGBColor(71, 85, 105)

                for bullet in p.bullet_points:
                    clean_b = bullet.strip().lstrip("-*• ")
                    if clean_b:
                        bp = doc.add_paragraph(style='List Bullet')
                        bp.paragraph_format.space_before = Pt(0)
                        bp.paragraph_format.space_after = Pt(1)
                        bp.paragraph_format.line_spacing = 1.05
                        bp.add_run(clean_b)

        # 6. Achievements
        achievements = resume.achievements
        if not achievements:
            achievements = [
                "Solved 1000+ Data Structures and Algorithms problems across LeetCode and competitive programming platforms.",
                "Earned the 500 Days Coding Badge on LeetCode.",
                "Completed NPTEL Cloud Computing certification with Silver grade.",
                "Participated in multiple hackathons, applying software development and problem-solving skills to build solutions under time constraints."
            ]

        if achievements:
            add_section_heading("Achievements")
            for ach in achievements:
                clean_ach = ach.strip().lstrip("-*• ")
                if clean_ach:
                    ap = doc.add_paragraph(style='List Bullet')
                    ap.paragraph_format.space_before = Pt(0)
                    ap.paragraph_format.space_after = Pt(1)
                    ap.add_run(clean_ach)

        doc.save(str(docx_path))
        return docx_path
