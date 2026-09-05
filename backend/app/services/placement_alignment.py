from typing import Dict, List, Any


# ============================================================
# PHASE 8 - PLACEMENT / JOB SKILL ALIGNMENT
# ============================================================
#
# IMPORTANT:
# These requirements intentionally use ONLY skills currently
# measured by SkillForge assessments.
#
# No score is invented for an untested skill.
# ============================================================

ROLE_REQUIREMENTS: Dict[str, Dict[str, float]] = {
    "Software Developer": {
        "DSA": 75,
        "Python": 70,
        "OOP": 70,
        "SQL": 65,
        "DBMS": 65,
        "C": 60,
        "Aptitude": 70,
    },
    "Software Engineer": {
        "DSA": 75,
        "Python": 70,
        "OOP": 70,
        "SQL": 65,
        "DBMS": 65,
        "C": 60,
        "Aptitude": 70,
    },

    "Full Stack Developer": {
        "Python": 65,
        "OOP": 70,
        "SQL": 65,
        "DBMS": 65,
        "DSA": 70,
        "Aptitude": 65,
    },

    "Data Analyst": {
        "Python": 70,
        "SQL": 80,
        "DBMS": 70,
        "Aptitude": 65,
        "DSA": 60,
    },

    "AI/ML Engineer": {
        "Python": 80,
        "DSA": 75,
        "OOP": 70,
        "SQL": 60,
        "DBMS": 60,
        "Aptitude": 65,
    },
}


def get_role_requirements(target_role: str) -> Dict[str, float]:
    return ROLE_REQUIREMENTS.get(
        target_role,
        ROLE_REQUIREMENTS["Software Developer"],
    )


def classify_gap(gap: float) -> str:
    if gap >= 0:
        return "Ready"

    if gap >= -10:
        return "Near Ready"

    if gap >= -20:
        return "Needs Improvement"

    return "Priority Gap"


def build_placement_alignment(
    target_role: str,
    skill_scores: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Compare real SkillForge assessment scores against
    the selected placement role requirements.
    """

    requirements = get_role_requirements(target_role)

    student_scores = {
        str(item["skill"]).strip().lower(): float(item["score"])
        for item in skill_scores
    }

    skills = []

    for required_skill, required_score in requirements.items():

        current_score = student_scores.get(
            required_skill.lower(),
            0.0,
        )

        gap = round(
            current_score - required_score,
            2,
        )

        skills.append({
            "skill": required_skill,
            "current_score": round(current_score, 2),
            "required_score": round(required_score, 2),
            "gap": gap,
            "status": classify_gap(gap),
        })

    skills.sort(
        key=lambda item: item["gap"]
    )

    if skills:
        alignment_score = round(
            sum(
                min(
                    (
                        item["current_score"]
                        / item["required_score"]
                    ) * 100,
                    100,
                )
                for item in skills
            ) / len(skills),
            2,
        )
    else:
        alignment_score = 0.0

    ready_count = sum(
        1
        for item in skills
        if item["status"] == "Ready"
    )

    near_ready_count = sum(
        1
        for item in skills
        if item["status"] == "Near Ready"
    )

    needs_improvement = [
        item
        for item in skills
        if item["status"] in (
            "Needs Improvement",
            "Priority Gap",
        )
    ]

    return {
        "target_role": (
            target_role
            if target_role in ROLE_REQUIREMENTS
            else "Software Developer"
        ),
        "alignment_score": alignment_score,
        "ready_count": ready_count,
        "near_ready_count": near_ready_count,
        "needs_improvement_count": len(needs_improvement),
        "priority_gaps": needs_improvement[:3],
        "skills": skills,
    }

