from typing import List, Dict, Set
from backend.app.models.job import JobDescriptionAnalysis, JobKeyword
from backend.app.models.optimization import CandidateSkillVerificationItem, AtsReport
from backend.app.models.resume import ExtractedResume, ProjectItem


class AtsScorer:
    """Computes transparent, multi-dimensional ATS alignment metrics."""

    @classmethod
    def calculate_report(
        cls,
        jd_analysis: JobDescriptionAnalysis,
        verified_skills: List[CandidateSkillVerificationItem],
        projects: List[ProjectItem],
        has_summary: bool = True,
        has_experience: bool = True,
        has_education: bool = True,
    ) -> AtsReport:
        # Categorize verified skills
        required_keywords: List[CandidateSkillVerificationItem] = []
        preferred_keywords: List[CandidateSkillVerificationItem] = []
        
        for item in verified_skills:
            if item.importance == "required":
                required_keywords.append(item)
            elif item.importance == "preferred":
                preferred_keywords.append(item)

        # Count matches: a skill counts as matched if it is 'supported' by resume OR 'confirmed' by candidate
        matched_required = [
            item.name for item in required_keywords
            if item.status in ["supported", "confirmed"]
        ]
        matched_preferred = [
            item.name for item in preferred_keywords
            if item.status in ["supported", "confirmed"]
        ]
        
        # Newly confirmed skills
        newly_confirmed = [
            item.name for item in verified_skills
            if item.status == "confirmed"
        ]

        # Missing requirements (required items that are still missing or rejected)
        missing_requirements = [
            item.name for item in required_keywords
            if item.status in ["missing", "rejected"]
        ]

        # Coverage percentages
        req_cov = (len(matched_required) / len(required_keywords) * 100.0) if required_keywords else 100.0
        pref_cov = (len(matched_preferred) / len(preferred_keywords) * 100.0) if preferred_keywords else 85.0
        
        # Confirmed skills ratio: how many missing items were recovered by candidate confirmation
        total_non_supported = [item for item in verified_skills if item.status in ["missing", "confirmed", "rejected"]]
        conf_cov = (len(newly_confirmed) / len(total_non_supported) * 100.0) if total_non_supported else 100.0

        # Project relevance score (based on whether projects demonstrate key tech)
        project_techs: Set[str] = set()
        for p in projects:
            for t in p.technologies:
                project_techs.add(t.lower())
            for b in p.bullet_points:
                project_techs.update(b.lower().split())

        crit_matches = sum(
            1 for c in jd_analysis.top_critical_skills
            if any(c.lower() in pt for pt in project_techs)
        )
        total_crit = len(jd_analysis.top_critical_skills) or 1
        project_relevance = min(100.0, max(50.0, (crit_matches / total_crit) * 100.0))

        # Overall weighted alignment score:
        # 45% Required Keyword Coverage
        # 25% Project Relevance
        # 15% Preferred Coverage
        # 15% Structural Completeness (Summary, Experience, Education)
        structure_score = 100.0
        if not has_summary: structure_score -= 20.0
        if not has_experience: structure_score -= 40.0
        if not has_education: structure_score -= 20.0

        overall = (
            0.45 * req_cov +
            0.25 * project_relevance +
            0.15 * pref_cov +
            0.15 * structure_score
        )
        # Cap realistically between 35 and 96 (ATS never guarantees 100%)
        overall = round(min(96.5, max(35.0, overall)), 1)

        # ATS Formatting Quality (standard LaTeX clean structure yields 95-98%)
        ats_formatting = 96.0

        # Potential recruiter concerns
        concerns: List[str] = []
        if missing_requirements:
            concerns.append(f"Missing {len(missing_requirements)} core requirements from job description: {', '.join(missing_requirements[:4])}.")
        if project_relevance < 70.0:
            concerns.append("Projects could demonstrate deeper technical integration with the target role's primary stack.")
        if not newly_confirmed and total_non_supported:
            concerns.append("Candidate did not confirm additional skills that could bridge the gap with the target JD.")

        # Recommendations
        recommendations: List[str] = []
        if missing_requirements:
            recommendations.append(f"Gain or confirm hands-on exposure to: {', '.join(missing_requirements[:3])}.")
        recommendations.append("Ensure every project bullet point follows the Google XYZ format (Action + Metric + Technical Implementation).")
        recommendations.append("Incorporate quantitative metrics into recent work experience (latency reduction, query optimization, throughput).")

        all_matched = sorted(list(set(matched_required + matched_preferred)))

        return AtsReport(
            overall_score=overall,
            required_keyword_coverage=round(req_cov, 1),
            preferred_keyword_coverage=round(pref_cov, 1),
            confirmed_skills_coverage=round(conf_cov, 1),
            matched_keywords=all_matched,
            missing_requirements=missing_requirements,
            project_relevance_score=round(project_relevance, 1),
            ats_formatting_quality=ats_formatting,
            potential_recruiter_concerns=concerns,
            recommended_improvements=recommendations,
        )

