import json
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.assessment import Assessment, SkillScore
from app.models.profile import Profile
from app.models.study_plan import StudyPlan, Task
from app.services.adaptive_engine import build_adaptive_analysis
from app.services.placement_alignment import build_placement_alignment


def build_student_context(
    current_user_id: int,
    db: Session,
) -> Dict[str, Any]:
    """
    Build an evidence-based context packet for the AI study coach.

    All student performance facts come from SkillForge's database.
    """

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.user_id == current_user_id,
            Assessment.completed_at.isnot(None),
        )
        .order_by(Assessment.completed_at.desc())
        .first()
    )

    if assessment is None:
        raise ValueError(
            "Complete at least one assessment before using the AI study coach."
        )

    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current_user_id)
        .first()
    )

    target_role = (
        profile.target_role
        if profile and profile.target_role
        else "Software Developer"
    )

    adaptive = build_adaptive_analysis(
        current_user_id=current_user_id,
        db=db,
    )

    skill_scores = (
        db.query(SkillScore)
        .filter(SkillScore.assessment_id == assessment.id)
        .all()
    )

    score_data = [
        {
            "skill": row.skill,
            "score": float(row.score),
            "total_questions": row.total_questions,
            "correct_answers": row.correct_answers,
        }
        for row in skill_scores
    ]

    placement = build_placement_alignment(
        target_role=target_role,
        skill_scores=score_data,
    )

    current_plan = (
        db.query(StudyPlan)
        .filter(
            StudyPlan.user_id == current_user_id,
        )
        .order_by(StudyPlan.created_at.desc())
        .first()
    )

    tasks = []

    if current_plan:
        plan_tasks = (
            db.query(Task)
            .filter(
                Task.study_plan_id == current_plan.id,
            )
            .order_by(
                Task.week_number.asc(),
                Task.id.asc(),
            )
            .all()
        )

        tasks = [
            {
                "title": task.task,
                "skill": task.skill,
                "week": task.week_number,
                "difficulty": task.difficulty,
                "duration_minutes": task.estimated_minutes,
                "status": task.status,
            }
            for task in plan_tasks
        ]

    return {
        "student": {
            "target_role": target_role,
        },
        "assessment": {
            "assessment_id": assessment.id,
            "overall_score": float(assessment.overall_score),
            "total_questions": assessment.total_questions,
            "total_correct": assessment.total_correct,
        },
        "adaptive_analysis": adaptive,
        "placement_alignment": placement,
        "study_plan": {
            "tasks": tasks,
        },
    }


def generate_coach_response(
    context: Dict[str, Any],
    question: str,
) -> str:
    """
    Generate a student-aware response using the existing Gemini setup.

    Gemini interprets authoritative SkillForge facts.
    It does not create or modify numerical performance data.
    """

    question = question.strip()

    if not question:
        raise ValueError("Coach question cannot be empty.")

    api_key = settings.GEMINI_API_KEY.strip()

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured in backend environment variables."
        )

    system_instruction = (
        "You are SkillForge AI Study Coach, a student-aware placement "
        "preparation coach.\n\n"
        "Use ONLY the student's provided SkillForge context.\n"
        "The assessment scores, trends, classifications, placement gaps, "
        "and task statuses are authoritative.\n"
        "Never invent student achievements, experience, scores, projects, "
        "certifications, or completed work.\n"
        "Do not claim the student is job-ready based only on this data.\n"
        "Give practical, specific guidance connected to the student's "
        "actual weaknesses, priorities, target role, and current study plan.\n"
        "When recommending a skill, explain the evidence briefly.\n"
        "If the student asks what to study next, prioritize the highest "
        "priority skill gap and consider pending study-plan tasks.\n"
        "If the student asks about progress, use the supplied assessment "
        "comparison and task status.\n"
        "If the context does not contain enough information to answer, "
        "say so clearly instead of inventing facts.\n"
        "Keep responses concise and actionable."
    )

    if api_key in ("mock_test_key", "MOCK_TEST_KEY", "TEST_MODE"):
        priority_skills = context["adaptive_analysis"].get(
            "priority_skills",
            [],
        )

        top_skill = (
            priority_skills[0]
            if priority_skills
            else "your highest-priority skill"
        )

        return (
            f"Based on your latest SkillForge assessment, focus on "
            f"{top_skill} next. Your current placement analysis and "
            f"adaptive assessment data identify this as a priority. "
            f"Start with the related pending study-plan task, then "
            f"practice problems before reassessing."
        )

    prompt = (
        f"{system_instruction}\n\n"
        f"STUDENT CONTEXT:\n"
        f"{json.dumps(context, indent=2)}\n\n"
        f"STUDENT QUESTION:\n"
        f"{question}\n\n"
        "Answer the student's question using the context above."
    )

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )

        response_text = response.text.strip()

    except Exception as exc:
        raise ValueError(
            f"Gemini API call failed: {str(exc)}"
        )

    if not response_text:
        raise ValueError("Gemini returned an empty coach response.")

    return response_text

