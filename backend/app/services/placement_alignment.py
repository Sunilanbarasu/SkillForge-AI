

from app.services.role_profiles import ROLE_PROFILES, DEFAULT_ROLE
from app.services.career_skill_profiles import get_career_skill_profile

# Backward-compatible export used by existing placement endpoints.
# Requirements are derived from the central role profiles so each
# detailed role keeps its own skill requirements.
ROLE_REQUIREMENTS = {
    role: {
        skill: (
            75 if float(weight) >= 0.95 else
            70 if float(weight) >= 0.85 else
            65 if float(weight) >= 0.75 else
            60 if float(weight) >= 0.65 else
            55 if float(weight) >= 0.55 else
            50
        )
        for skill, weight in profile["skills"].items()
    }
    for role, profile in ROLE_PROFILES.items()
}

def get_role_requirements(target_role):
    """
    Build placement requirements from the authoritative career profile.

    Supports both the original detailed roles and the expanded 91-career
    catalog without silently converting an expanded career to Software Engineer.
    """
    career_profile = get_career_skill_profile(target_role)

    if career_profile:
        role_skills = career_profile.get("skills", {})
    elif target_role in ROLE_PROFILES:
        role_skills = ROLE_PROFILES[target_role]["skills"]
    else:
        role_skills = ROLE_PROFILES[DEFAULT_ROLE]["skills"]

    weight_to_target = {
        1.00: 75,
        0.95: 75,
        0.90: 70,
        0.85: 70,
        0.80: 65,
        0.75: 65,
        0.70: 60,
        0.65: 60,
        0.60: 55,
        0.55: 55,
        0.50: 50,
        0.45: 50,
        0.40: 50,
        0.35: 50,
        0.30: 50,
    }

    return {
        skill: weight_to_target.get(round(float(weight), 2), 60)
        for skill, weight in role_skills.items()
    }


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
    Compare real SkillForge assessment scores against the
    requirements of the student's selected target role.

    The skills displayed here come from the selected career profile.
    """

    # get_role_requirements() supports both the original detailed
    # roles and the expanded 91-career catalog.
    # Do NOT force expanded careers back to Software Engineer.
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
                if item["required_score"] > 0
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
        "target_role": target_role,
        "alignment_score": alignment_score,
        "ready_count": ready_count,
        "near_ready_count": near_ready_count,
        "needs_improvement_count": len(needs_improvement),
        "priority_gaps": needs_improvement[:3],
        "skills": skills,
    }
