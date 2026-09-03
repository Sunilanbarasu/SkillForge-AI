from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.assessment import Assessment, SkillScore
from app.models.ai_analysis import AIAnalysis
from app.models.study_plan import StudyPlan, Task
from app.models.progress import SkillProgress
from app.schemas.study_plan import (
    StudyPlanResponse,
    TaskUpdateRequest,
    TaskResponse,
)
from app.services.study_plan import (
    build_study_plan_input_payload,
    generate_study_plan,
    build_adaptive_study_plan_input_payload,
    generate_adaptive_study_plan,
)
from app.services.ai_analysis import get_score_category
from app.services.study_resources import get_study_resource
from app.api.deps import get_current_user

router = APIRouter()


def _get_latest_completed_assessment(
    db: Session,
    user_id: int
) -> Assessment:
    """Returns the latest completed assessment for the user or None."""
    return (
        db.query(Assessment)
        .filter(
            Assessment.user_id == user_id,
            Assessment.completed_at.isnot(None)
        )
        .order_by(Assessment.completed_at.desc())
        .first()
    )


def _get_ai_analysis_for_assessment(
    db: Session,
    assessment_id: int
) -> AIAnalysis:
    """Returns AI analysis for the given assessment or None."""
    return (
        db.query(AIAnalysis)
        .filter(
            AIAnalysis.assessment_id == assessment_id
        )
        .first()
    )


@router.post(
    "/generate",
    response_model=StudyPlanResponse,
    summary="Generate or retrieve personalized study plan"
)
def generate_study_plan_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a personalized study plan from the latest completed
    assessment and its AI analysis.

    SECURITY & COST SAFEGUARDS:
    - JWT required.
    - Idempotent: If a plan already exists for the latest assessment,
      return the cached plan.
    """

    assessment = _get_latest_completed_assessment(
        db,
        current_user.id
    )

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No completed assessment found. "
                "Complete an assessment before generating a study plan."
            )
        )

    existing_plan = (
        db.query(StudyPlan)
        .filter(
            StudyPlan.user_id == current_user.id,
            StudyPlan.assessment_id == assessment.id
        )
        .first()
    )

    if existing_plan:
        return existing_plan

    ai_analysis = _get_ai_analysis_for_assessment(
        db,
        assessment.id
    )

    if ai_analysis is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No AI analysis found for the latest assessment. "
                "Generate AI skill-gap analysis first."
            )
        )

    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current_user.id)
        .first()
    )

    target_role = (
        profile.target_role
        if profile
        else "Software Developer"
    )

    exp_level = (
        profile.experience_level
        if profile
        else "Student"
    )

    skill_scores = (
        db.query(SkillScore)
        .filter(
            SkillScore.assessment_id == assessment.id
        )
        .all()
    )

    sk_data_list = []

    for ss in skill_scores:
        score_val = float(ss.score)

        sk_data_list.append({
            "skill": ss.skill,
            "score": score_val,
            "category": get_score_category(score_val),
            "correct_answers": ss.correct_answers,
            "total_questions": ss.total_questions
        })

    payload = build_study_plan_input_payload(
        target_role=target_role,
        experience_level=exp_level,
        overall_score=assessment.overall_score,
        skill_scores=sk_data_list,
        ai_strengths=ai_analysis.strengths or [],
        ai_weaknesses=ai_analysis.weaknesses or [],
        ai_skill_gaps=ai_analysis.skill_gaps or [],
        ai_priorities=ai_analysis.priorities or [],
        ai_recommendations=ai_analysis.recommendations or []
    )

    try:
        validated_plan = generate_study_plan(payload)

    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(val_err)
        )

    new_plan = StudyPlan(
        user_id=current_user.id,
        assessment_id=assessment.id,
        title=validated_plan.title,
        goal=validated_plan.goal,
        duration_weeks=validated_plan.duration_weeks
    )

    db.add(new_plan)
    db.flush()

    for t in validated_plan.tasks:
        resource = get_study_resource(
            skill=t.skill,
            task=t.task
        )

        db.add(
            Task(
                study_plan_id=new_plan.id,
                skill=t.skill,
                week_number=t.week_number,
                task=t.task,
                difficulty=t.difficulty,
                estimated_minutes=t.estimated_minutes,
                resource_title=resource["title"],
                resource_url=resource["url"],
                status="pending"
            )
        )

    db.commit()
    db.refresh(new_plan)

    tasks = (
        db.query(Task)
        .filter(Task.study_plan_id == new_plan.id)
        .order_by(Task.week_number.asc())
        .all()
    )

    new_plan.tasks = tasks

    return new_plan


@router.post(
    "/adapt",
    response_model=StudyPlanResponse,
    summary="Generate an adaptive study plan from reassessment progress"
)
def adapt_study_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a NEW study plan based on the latest reassessment.

    The previous study plan remains unchanged.

    A new plan is created only when the latest assessment does not
    already have an associated study plan.
    """

    # ---------------------------------------------------------
    # 1. Get the two latest completed assessments
    # ---------------------------------------------------------

    assessments = (
        db.query(Assessment)
        .filter(
            Assessment.user_id == current_user.id,
            Assessment.completed_at.isnot(None)
        )
        .order_by(Assessment.completed_at.desc())
        .all()
    )

    if len(assessments) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "At least two completed assessments are required "
                "to adapt a study plan."
            )
        )

    current_assessment = assessments[0]
    previous_assessment = assessments[1]

    # ---------------------------------------------------------
    # 2. Idempotency check
    # ---------------------------------------------------------

    existing_plan = (
        db.query(StudyPlan)
        .filter(
            StudyPlan.user_id == current_user.id,
            StudyPlan.assessment_id == current_assessment.id
        )
        .first()
    )

    if existing_plan:
        tasks = (
            db.query(Task)
            .filter(
                Task.study_plan_id == existing_plan.id
            )
            .order_by(Task.week_number.asc())
            .all()
        )

        existing_plan.tasks = tasks

        return existing_plan

    # ---------------------------------------------------------
    # 3. Get progress data
    # ---------------------------------------------------------

    progress_rows = (
        db.query(SkillProgress)
        .filter(
            SkillProgress.user_id == current_user.id,
            SkillProgress.previous_assessment_id == previous_assessment.id,
            SkillProgress.current_assessment_id == current_assessment.id
        )
        .order_by(SkillProgress.skill.asc())
        .all()
    )

    if not progress_rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Progress data not found for the latest assessments. "
                "Calculate progress before adapting the study plan."
            )
        )

    # ---------------------------------------------------------
    # 4. Get latest AI analysis
    # ---------------------------------------------------------

    ai_analysis = _get_ai_analysis_for_assessment(
        db,
        current_assessment.id
    )

    if ai_analysis is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No AI analysis found for the latest assessment. "
                "Generate AI skill-gap analysis first."
            )
        )

    # ---------------------------------------------------------
    # 5. Get profile
    # ---------------------------------------------------------

    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current_user.id)
        .first()
    )

    target_role = (
        profile.target_role
        if profile
        else "Software Developer"
    )

    exp_level = (
        profile.experience_level
        if profile
        else "Student"
    )

    # ---------------------------------------------------------
    # 6. Convert progress into deterministic AI input
    # ---------------------------------------------------------

    skill_progress = []

    for row in progress_rows:
        skill_progress.append({
            "skill": row.skill,
            "previous_score": float(row.previous_score),
            "current_score": float(row.current_score),
            "score_change": float(row.score_change),
            "status": row.status
        })

    overall_score_change = round(
        float(current_assessment.overall_score)
        - float(previous_assessment.overall_score),
        2
    )

    payload = build_adaptive_study_plan_input_payload(
        target_role=target_role,
        experience_level=exp_level,
        previous_overall_score=float(
            previous_assessment.overall_score
        ),
        current_overall_score=float(
            current_assessment.overall_score
        ),
        overall_score_change=overall_score_change,
        skill_progress=skill_progress,
        ai_strengths=ai_analysis.strengths or [],
        ai_weaknesses=ai_analysis.weaknesses or [],
        ai_skill_gaps=ai_analysis.skill_gaps or [],
        ai_priorities=ai_analysis.priorities or [],
        ai_recommendations=ai_analysis.recommendations or []
    )

    # ---------------------------------------------------------
    # 7. Generate adaptive AI plan
    # ---------------------------------------------------------

    try:
        validated_plan = generate_adaptive_study_plan(
            payload
        )

    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(val_err)
        )

    # ---------------------------------------------------------
    # 8. Create NEW study plan
    # ---------------------------------------------------------

    new_plan = StudyPlan(
        user_id=current_user.id,
        assessment_id=current_assessment.id,
        title=validated_plan.title,
        goal=validated_plan.goal,
        duration_weeks=validated_plan.duration_weeks
    )

    db.add(new_plan)
    db.flush()

    # ---------------------------------------------------------
    # 9. Persist adaptive tasks
    # ---------------------------------------------------------

    for t in validated_plan.tasks:
        resource = get_study_resource(
            skill=t.skill,
            task=t.task
        )

        db.add(
            Task(
                study_plan_id=new_plan.id,
                skill=t.skill,
                week_number=t.week_number,
                task=t.task,
                difficulty=t.difficulty,
                estimated_minutes=t.estimated_minutes,
                resource_title=resource["title"],
                resource_url=resource["url"],
                status="pending"
            )
        )

    db.commit()
    db.refresh(new_plan)

    # ---------------------------------------------------------
    # 10. Return plan with tasks
    # ---------------------------------------------------------

    tasks = (
        db.query(Task)
        .filter(
            Task.study_plan_id == new_plan.id
        )
        .order_by(Task.week_number.asc())
        .all()
    )

    new_plan.tasks = tasks

    return new_plan


@router.get(
    "/current",
    response_model=StudyPlanResponse,
    summary="Get current user's latest study plan"
)
def get_current_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the current user's most recent study plan with tasks."""

    plan = (
        db.query(StudyPlan)
        .filter(
            StudyPlan.user_id == current_user.id
        )
        .order_by(StudyPlan.created_at.desc())
        .first()
    )

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No study plan found. "
                "Generate a study plan first."
            )
        )

    tasks = (
        db.query(Task)
        .filter(
            Task.study_plan_id == plan.id
        )
        .order_by(Task.week_number.asc())
        .all()
    )

    plan.tasks = tasks

    return plan


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update task completion status"
)
def update_task_status(
    task_id: int,
    update_in: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates a task's completion status.

    SECURITY CHECK:
    Task must belong to a plan owned by the current user.
    """

    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )

    plan = (
        db.query(StudyPlan)
        .filter(
            StudyPlan.id == task.study_plan_id
        )
        .first()
    )

    if plan is None or plan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not authorized to update this task."
            )
        )

    if update_in.status == "completed":
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)

    else:
        task.status = "pending"
        task.completed_at = None

    db.commit()
    db.refresh(task)

    return task