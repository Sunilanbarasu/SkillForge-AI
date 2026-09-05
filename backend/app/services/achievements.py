from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app.models.assessment import Assessment, SkillScore
from app.models.study_plan import StudyPlan, Task


def build_achievements(
    current_user_id: int,
    db: Session,
) -> List[Dict[str, Any]]:
    """
    Build evidence-based achievements entirely from existing SkillForge data.

    Achievements are derived from authoritative database records and are
    never manually assigned.
    """

    achievements: List[Dict[str, Any]] = []

    completed_assessments = (
        db.query(Assessment)
        .filter(
            Assessment.user_id == current_user_id,
            Assessment.completed_at.isnot(None),
        )
        .order_by(Assessment.completed_at.asc())
        .all()
    )

    study_plans = (
        db.query(StudyPlan)
        .filter(StudyPlan.user_id == current_user_id)
        .all()
    )

    plan_ids = [plan.id for plan in study_plans]

    completed_tasks = 0

    if plan_ids:
        completed_tasks = (
            db.query(Task)
            .filter(
                Task.study_plan_id.in_(plan_ids),
                Task.status == "completed",
            )
            .count()
        )

    # 1. First Assessment
    if len(completed_assessments) >= 1:
        achievements.append(
            {
                "key": "first_assessment",
                "title": "First Assessment",
                "description": "Completed your first SkillForge assessment.",
                "evidence": f"{len(completed_assessments)} completed assessment(s).",
            }
        )

    # 2. Plan Starter
    if completed_tasks >= 1:
        achievements.append(
            {
                "key": "plan_starter",
                "title": "Plan Starter",
                "description": "Completed your first personalized study-plan task.",
                "evidence": f"{completed_tasks} study-plan task(s) completed.",
            }
        )

    # 3. Consistent Learner
    if completed_tasks >= 5:
        achievements.append(
            {
                "key": "consistent_learner",
                "title": "Consistent Learner",
                "description": "Completed at least five personalized study-plan tasks.",
                "evidence": f"{completed_tasks} study-plan task(s) completed.",
            }
        )

    # 4. Skill Improver
    improved_skills = []

    if len(completed_assessments) >= 2:
        previous = completed_assessments[-2]
        current = completed_assessments[-1]

        previous_scores = (
            db.query(SkillScore)
            .filter(SkillScore.assessment_id == previous.id)
            .all()
        )

        current_scores = (
            db.query(SkillScore)
            .filter(SkillScore.assessment_id == current.id)
            .all()
        )

        previous_map = {
            score.skill: float(score.score)
            for score in previous_scores
        }

        current_map = {
            score.skill: float(score.score)
            for score in current_scores
        }

        for skill in sorted(set(previous_map) | set(current_map)):
            previous_score = previous_map.get(skill, 0.0)
            current_score = current_map.get(skill, 0.0)

            if current_score - previous_score > 5:
                improved_skills.append(skill)

    if improved_skills:
        achievements.append(
            {
                "key": "skill_improver",
                "title": "Skill Improver",
                "description": "Improved at least one skill by more than five percentage points.",
                "evidence": "Improved skills: " + ", ".join(improved_skills),
            }
        )

    # 5. Skill Mastery
    mastered_skills = []

    if completed_assessments:
        latest = completed_assessments[-1]

        latest_scores = (
            db.query(SkillScore)
            .filter(SkillScore.assessment_id == latest.id)
            .all()
        )

        mastered_skills = sorted(
            score.skill
            for score in latest_scores
            if float(score.score) >= 80.0
        )

    if mastered_skills:
        achievements.append(
            {
                "key": "skill_mastery",
                "title": "Skill Mastery",
                "description": "Reached 80% or higher in at least one assessed skill.",
                "evidence": "Mastered skills: " + ", ".join(mastered_skills),
            }
        )

    # 6. Placement Ready Skill
    placement_ready_skills = []

    if completed_assessments:
        latest = completed_assessments[-1]

        latest_scores = (
            db.query(SkillScore)
            .filter(SkillScore.assessment_id == latest.id)
            .all()
        )

        score_map = {
            score.skill: float(score.score)
            for score in latest_scores
        }

        # Use the same default Software Developer requirements as the
        # existing placement-alignment service.
        requirements = {
            "DSA": 75,
            "Python": 70,
            "OOP": 70,
            "SQL": 65,
            "DBMS": 65,
            "C": 60,
            "Aptitude": 70,
        }

        placement_ready_skills = sorted(
            skill
            for skill, required_score in requirements.items()
            if score_map.get(skill, 0.0) >= required_score
        )

    if placement_ready_skills:
        achievements.append(
            {
                "key": "placement_ready_skill",
                "title": "Placement Ready Skill",
                "description": "Reached the target score for at least one placement skill.",
                "evidence": "Placement-ready skills: "
                + ", ".join(placement_ready_skills),
            }
        )

    return achievements
