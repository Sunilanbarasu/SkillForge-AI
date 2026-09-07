from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.question import Question
from app.models.assessment import Assessment, Answer, SkillScore
from app.models.ai_analysis import AIAnalysis
from app.schemas.assessment import (
    AssessmentStartResponse,
    QuestionOut,
    AssessmentSubmitRequest,
    AssessmentResultResponse,
    AssessmentHistoryItem,
    SkillScoreDetail
)
from app.schemas.ai_analysis import AIAnalysisResponse
from app.services.ai_analysis import build_ai_input_payload, generate_skill_gap_analysis
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/start", response_model=AssessmentStartResponse, status_code=status.HTTP_201_CREATED, summary="Start a placement diagnostic assessment")
def start_assessment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new assessment for the authenticated student and fetches questions.
    SECURITY REQUIREMENT: Correct answers are NEVER returned.
    """
    questions = db.query(Question).order_by(Question.id.asc()).all()
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No assessment questions available in database."
        )

    new_assessment = Assessment(
        user_id=current_user.id,
        started_at=datetime.now(timezone.utc),
        total_questions=len(questions),
        total_correct=0,
        overall_score=0.0
    )
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)

    question_outs = [QuestionOut.model_validate(q) for q in questions]

    return AssessmentStartResponse(
        assessment_id=new_assessment.id,
        total_questions=len(questions),
        started_at=new_assessment.started_at,
        questions=question_outs
    )


@router.post("/{assessment_id}/submit", response_model=AssessmentResultResponse, summary="Submit assessment answers for server-side scoring")
def submit_assessment(
    assessment_id: int,
    submit_in: AssessmentSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits student answers, calculates score server-side, saves answers and skill scores.
    SECURITY CHECKS:
    - User can only submit their own assessment.
    - Cannot resubmit already completed assessment.
    - Validates submitted question IDs.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found."
        )

    if assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to submit this assessment."
        )

    if assessment.completed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment has already been submitted and completed."
        )

    if not submit_in.answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No answers provided in submission."
        )

    db_questions = db.query(Question).all()
    q_map = {q.id: q for q in db_questions}

    skill_stats = {}
    total_correct = 0

    db.query(Answer).filter(Answer.assessment_id == assessment_id).delete()

    for item in submit_in.answers:
        if item.question_id not in q_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid question ID: {item.question_id}"
            )

        q = q_map[item.question_id]
        selected_upper = item.selected_answer.strip().upper()
        is_correct = (selected_upper == q.correct_answer.strip().upper())

        ans = Answer(
            assessment_id=assessment.id,
            question_id=q.id,
            selected_answer=selected_upper,
            is_correct=is_correct
        )
        db.add(ans)

        if is_correct:
            total_correct += 1

        if q.skill not in skill_stats:
            skill_stats[q.skill] = {"total": 0, "correct": 0}
        skill_stats[q.skill]["total"] += 1
        if is_correct:
            skill_stats[q.skill]["correct"] += 1

    total_q_count = len(submit_in.answers)
    overall_score = round((total_correct / total_q_count * 100.0), 2) if total_q_count > 0 else 0.0

    db.query(SkillScore).filter(SkillScore.assessment_id == assessment_id).delete()
    skill_score_objs = []
    for skill_name, stats in skill_stats.items():
        s_total = stats["total"]
        s_correct = stats["correct"]
        s_score = round((s_correct / s_total * 100.0), 2) if s_total > 0 else 0.0

        ss = SkillScore(
            assessment_id=assessment.id,
            skill=skill_name,
            total_questions=s_total,
            correct_answers=s_correct,
            score=s_score
        )
        db.add(ss)
        skill_score_objs.append(ss)

    assessment.completed_at = datetime.now(timezone.utc)
    assessment.total_questions = total_q_count
    assessment.total_correct = total_correct
    assessment.overall_score = overall_score

    db.commit()
    db.refresh(assessment)

    return AssessmentResultResponse(
        id=assessment.id,
        user_id=assessment.user_id,
        started_at=assessment.started_at,
        completed_at=assessment.completed_at,
        total_questions=assessment.total_questions,
        total_correct=assessment.total_correct,
        overall_score=assessment.overall_score,
        skill_scores=[SkillScoreDetail.model_validate(ss) for ss in skill_score_objs]
    )


@router.get("/history", response_model=List[AssessmentHistoryItem], summary="Get completed assessment history")
def get_assessment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns list of completed assessments for the authenticated student.
    """
    assessments = db.query(Assessment).filter(
        Assessment.user_id == current_user.id,
        Assessment.completed_at.isnot(None)
    ).order_by(Assessment.completed_at.desc()).all()

    return assessments


@router.get("/{assessment_id}/result", response_model=AssessmentResultResponse, summary="Get assessment detailed result")
def get_assessment_result(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns overall score and skill-wise performance breakdown for a completed assessment.
    SECURITY CHECK: User can only view their own assessment result.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found."
        )

    if assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this assessment result."
        )

    skill_scores = db.query(SkillScore).filter(SkillScore.assessment_id == assessment_id).all()

    return AssessmentResultResponse(
        id=assessment.id,
        user_id=assessment.user_id,
        started_at=assessment.started_at,
        completed_at=assessment.completed_at,
        total_questions=assessment.total_questions,
        total_correct=assessment.total_correct,
        overall_score=assessment.overall_score,
        skill_scores=[SkillScoreDetail.model_validate(ss) for ss in skill_scores]
    )


@router.post("/{assessment_id}/ai-analysis", response_model=AIAnalysisResponse, summary="Generate or retrieve AI Skill-Gap Analysis")
def generate_ai_analysis(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates AI skill-gap analysis interpreting completed assessment performance.
    SECURITY & COST SAFEGUARDS:
    - JWT required.
    - User can only analyze their own assessment.
    - Assessment must be completed.
    - Caching: Returns stored analysis if already generated (avoids duplicate API costs).
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found."
        )

    # Ownership check
    if assessment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to analyze this assessment."
        )

    # Completion check
    if assessment.completed_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment must be completed before generating AI analysis."
        )

    # Idempotency check: Return existing stored analysis if present
    existing_analysis = db.query(AIAnalysis).filter(AIAnalysis.assessment_id == assessment_id).first()
    if existing_analysis:
        return existing_analysis

    # Load student profile & skill scores from DB
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    target_role = profile.target_role if profile else "Software Developer"
    exp_level = profile.experience_level if profile else "Student"

    skill_scores = db.query(SkillScore).filter(SkillScore.assessment_id == assessment_id).all()
    sk_data_list = [
        {
            "skill": ss.skill,
            "score": ss.score,
            "correct_answers": ss.correct_answers,
            "total_questions": ss.total_questions
        }
        for ss in skill_scores
    ]

    # Build structured fact payload
    payload = build_ai_input_payload(
        target_role=target_role,
        experience_level=exp_level,
        overall_score=assessment.overall_score,
        total_correct=assessment.total_correct,
        total_questions=assessment.total_questions,
        skill_scores=sk_data_list
    )

    # Call AI service
    try:
        validated_ai_result = generate_skill_gap_analysis(payload)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(val_err)
        )

    # Store AIAnalysis in PostgreSQL
    new_ai_analysis = AIAnalysis(
        user_id=current_user.id,
        assessment_id=assessment.id,
        summary=validated_ai_result.summary,
        strengths=[s.model_dump() for s in validated_ai_result.strengths],
        weaknesses=[w.model_dump() for w in validated_ai_result.weaknesses],
        skill_gaps=[sg.model_dump() for sg in validated_ai_result.skill_gaps],
        priorities=[p.model_dump() for p in validated_ai_result.priorities],
        recommendations=[r.model_dump() for r in validated_ai_result.recommendations]
    )

    db.add(new_ai_analysis)
    db.commit()
    db.refresh(new_ai_analysis)

    return new_ai_analysis

# ============================================================
# PHASE 4 - ADAPTIVE PRACTICE
# ============================================================

@router.get(
    "/adaptive-practice",
    summary="Get adaptive practice questions based on latest performance"
)
def get_adaptive_practice(
    skill: str | None = None,
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Selects practice questions using the student's real latest
    assessment performance.

    Adaptation:
    - Critical / very weak skill -> Beginner questions
    - Needs Improvement -> Beginner + Intermediate
    - Good -> Intermediate
    - Strong -> Intermediate
    - If previous answers exist, difficulty adapts from accuracy.
    """

    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 20."
        )

    # Latest completed assessment
    latest_assessment = (
        db.query(Assessment)
        .filter(
            Assessment.user_id == current_user.id,
            Assessment.completed_at.isnot(None)
        )
        .order_by(Assessment.completed_at.desc())
        .first()
    )

    if latest_assessment is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complete an assessment before starting adaptive practice."
        )

    # Latest skill scores
    skill_scores = (
        db.query(SkillScore)
        .filter(SkillScore.assessment_id == latest_assessment.id)
        .all()
    )

    if not skill_scores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No skill performance data is available."
        )

    score_map = {
        item.skill: float(item.score)
        for item in skill_scores
    }

    # If no skill was supplied, choose the weakest skill automatically.
    if skill:
        if skill not in score_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No assessment performance found for skill: {skill}"
            )
        target_skill = skill
    else:
        target_skill = min(
            score_map,
            key=score_map.get
        )

    current_score = score_map[target_skill]

    # Determine adaptive difficulty from actual performance.
    if current_score < 50:
        recommended_difficulty = "Beginner"
    elif current_score < 70:
        recommended_difficulty = "Intermediate"
    else:
        recommended_difficulty = "Intermediate"

    # Check recent practice/assessment answers for this skill.
    recent_answers = (
        db.query(Answer)
        .join(Question, Answer.question_id == Question.id)
        .join(Assessment, Answer.assessment_id == Assessment.id)
        .filter(
            Assessment.user_id == current_user.id,
            Question.skill == target_skill
        )
        .order_by(Assessment.completed_at.desc())
        .limit(20)
        .all()
    )

    if recent_answers:
        recent_correct = sum(
            1 for answer in recent_answers
            if answer.is_correct
        )

        recent_accuracy = (
            recent_correct / len(recent_answers) * 100
        )

        # If the student is performing well, increase difficulty.
        if recent_accuracy >= 80:
            recommended_difficulty = "Intermediate"

        # If performance is very weak, reinforce fundamentals.
        elif recent_accuracy < 50:
            recommended_difficulty = "Beginner"

    # Candidate questions.
    query = db.query(Question).filter(
        Question.skill == target_skill,
        Question.difficulty == recommended_difficulty
    )

    candidates = query.order_by(Question.id.asc()).all()

    # Fallback if the exact adaptive difficulty is unavailable.
    if not candidates:
        candidates = (
            db.query(Question)
            .filter(Question.skill == target_skill)
            .order_by(Question.id.asc())
            .all()
        )

    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No practice questions available for {target_skill}."
        )

    # Avoid immediately repeating questions from the latest assessment.
    latest_question_ids = {
        answer.question_id
        for answer in (
            db.query(Answer)
            .filter(
                Answer.assessment_id == latest_assessment.id
            )
            .all()
        )
    }

    unseen_candidates = [
        question
        for question in candidates
        if question.id not in latest_question_ids
    ]

    if unseen_candidates:
        candidates = unseen_candidates

    selected = candidates[:limit]

    return {
        "assessment_id": latest_assessment.id,
        "skill": target_skill,
        "current_score": current_score,
        "recommended_difficulty": recommended_difficulty,
        "recent_accuracy": round(
            recent_accuracy, 2
        ) if recent_answers else None,
        "reason": (
            f"{target_skill} is currently at {current_score:.2f}%. "
            f"Adaptive practice selected {recommended_difficulty} questions "
            f"to target this skill."
        ),
        "questions": [
            {
                "id": question.id,
                "skill": question.skill,
                "question_text": question.question_text,
                "option_a": question.option_a,
                "option_b": question.option_b,
                "option_c": question.option_c,
                "option_d": question.option_d,
                "difficulty": question.difficulty
            }
            for question in selected
        ]
    }
