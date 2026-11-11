import re
from typing import List, Dict, Tuple, Optional
from backend.app.models.resume import ExtractedResume
from backend.app.models.job import JobDescriptionAnalysis, JobKeyword
from backend.app.models.optimization import CandidateSkillVerificationItem
from backend.app.services.jd_analyzer import JobDescriptionAnalyzer


class ResumeAnalyzer:
    """
    Compares extracted Job Description skills against candidate resume evidence.
    Identifies Supported skills vs Missing skills requiring interactive candidate confirmation.
    """

    @classmethod
    def compare_skills_against_resume(
        cls,
        resume: ExtractedResume,
        jd_analysis: JobDescriptionAnalysis,
    ) -> List[CandidateSkillVerificationItem]:
        verification_items: List[CandidateSkillVerificationItem] = []
        resume_text_lower = " " + resume.raw_text.lower() + " "

        # Collect all keywords across all 17 categories
        all_jd_keywords: List[JobKeyword] = []
        for field_name in jd_analysis.categorized_keywords.__dict__:
            kws = getattr(jd_analysis.categorized_keywords, field_name, [])
            if isinstance(kws, list):
                all_jd_keywords.extend(kws)

        # Check each keyword against resume text and sections
        for kw in all_jd_keywords:
            evidence = cls._find_evidence_in_resume(kw.name, resume, resume_text_lower)
            if evidence:
                verification_items.append(CandidateSkillVerificationItem(
                    name=kw.name,
                    category=kw.category,
                    importance=kw.importance,
                    status="supported",
                    proficiency="advanced",
                    evidence_in_resume=evidence,
                    practical_experience="Demonstrated in resume",
                    how_used=evidence,
                ))
            else:
                verification_items.append(CandidateSkillVerificationItem(
                    name=kw.name,
                    category=kw.category,
                    importance=kw.importance,
                    status="missing",
                    proficiency="intermediate",
                    evidence_in_resume=None,
                    practical_experience="",
                    how_used="",
                ))

        # Sort: Missing required skills first (so candidate can easily confirm them), then missing preferred, then supported
        def sort_key(item: CandidateSkillVerificationItem):
            status_order = {"missing": 0, "supported": 1, "confirmed": 0, "rejected": 2}
            importance_order = {"required": 0, "preferred": 1, "bonus": 2}
            return (status_order.get(item.status, 1), importance_order.get(item.importance, 1), item.name)

        verification_items.sort(key=sort_key)
        return verification_items

    @classmethod
    def _find_evidence_in_resume(
        cls,
        skill_name: str,
        resume: ExtractedResume,
        resume_text_lower: str,
    ) -> Optional[str]:
        # Get matching patterns for this skill from the tech catalog
        patterns = [skill_name.lower()]
        for category_dict in JobDescriptionAnalyzer.TECH_CATALOG.values():
            if skill_name in category_dict:
                patterns = category_dict[skill_name]
                break

        # Check skills section list
        for user_skill in resume.skills:
            for pat in patterns:
                if "\\" not in pat and pat in user_skill.lower():
                    return f"Listed in skills section: '{user_skill}'"
                elif "\\" in pat and re.search(pat, user_skill, re.IGNORECASE):
                    return f"Listed in skills section: '{user_skill}'"

        # Check projects
        for p in resume.projects:
            # Check project technologies
            for t in p.technologies:
                for pat in patterns:
                    if "\\" not in pat and pat in t.lower():
                        return f"Used in project '{p.name}': {t}"
                    elif "\\" in pat and re.search(pat, t, re.IGNORECASE):
                        return f"Used in project '{p.name}': {t}"
            # Check project bullet points
            for b in p.bullet_points:
                found, matched = JobDescriptionAnalyzer._check_presence(patterns, " " + b.lower() + " ")
                if found:
                    return f"Referenced in project '{p.name}': \"{b[:100]}...\""

        # Check experience bullet points
        for exp in resume.experience:
            for b in exp.bullet_points:
                found, matched = JobDescriptionAnalyzer._check_presence(patterns, " " + b.lower() + " ")
                if found:
                    return f"Referenced in role '{exp.title} at {exp.company}': \"{b[:100]}...\""

        # General check in raw text
        found, matched = JobDescriptionAnalyzer._check_presence(patterns, resume_text_lower)
        if found:
            return f"Found in resume text (matching term: '{matched}')"

        return None
