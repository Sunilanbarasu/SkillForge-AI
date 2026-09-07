import json
import re
from datetime import date

from app.core.config import settings
from app.models.assessment import Assessment, SkillScore
from app.models.profile import Profile
from app.models.ai_analysis import AIAnalysis


def _clean_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def build_challenge_context(db, user_id: int) -> dict:
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == user_id)
        .first()
    )

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.user_id == user_id,
            Assessment.completed_at.isnot(None),
        )
        .order_by(Assessment.completed_at.desc())
        .first()
    )

    skills = []
    if assessment:
        scores = (
            db.query(SkillScore)
            .filter(SkillScore.assessment_id == assessment.id)
            .order_by(SkillScore.score.asc())
            .all()
        )
        skills = [
            {
                "skill": item.skill,
                "score": item.score,
                "correct": item.correct_answers,
                "total": item.total_questions,
            }
            for item in scores
        ]

    analysis = None
    if assessment:
        analysis = (
            db.query(AIAnalysis)
            .filter(AIAnalysis.assessment_id == assessment.id)
            .first()
        )

    return {
        "target_role": getattr(profile, "target_role", None) or "Software Engineer",
        "experience_level": getattr(profile, "experience_level", None) or "Beginner",
        "latest_assessment_score": assessment.overall_score if assessment else None,
        "priority_skills": skills[:3],
        "ai_analysis": getattr(analysis, "recommendations", None) if analysis else None,
        "today": date.today().isoformat(),
    }


def generate_daily_challenge(db, user_id: int) -> dict:
    context = build_challenge_context(db, user_id)

    api_key = getattr(settings, "GEMINI_API_KEY", None)

    if not api_key:
        raise RuntimeError("Gemini API key is not configured.")

    from google import genai

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are the coding challenge generator for SkillForge AI.

Create ONE practical programming challenge personalized to this student.

Student context:
Target role: {context["target_role"]}
Experience level: {context["experience_level"]}
Latest assessment score: {context["latest_assessment_score"]}
Weakest skills: {json.dumps(context["priority_skills"])}
AI recommendations: {json.dumps(context["ai_analysis"])}

Rules:
1. Focus primarily on the student's weakest relevant skill.
2. Match the challenge difficulty to the student's experience.
3. Make it solvable in 20-40 minutes.
4. Use Python.
5. Do not require external libraries.
6. Starter code must contain a function named solution that the student can complete.
7. Every test case must contain exactly these fields: function, input, expected_output.
8. The function field must always be "solution".
9. The input field must be JSON-compatible data only and must NEVER contain Python code, assignments, object construction, print statements, or executable expressions.
10. expected_output must be the JSON-compatible return value of solution().
11. Test cases must be directly callable by the evaluator as solution(input).
12. Return ONLY valid JSON.

Required JSON:
{{
  "title": "short challenge title",
  "description": "clear problem statement",
  "skill": "target skill",
  "language": "Python",
  "difficulty": "Beginner|Intermediate|Advanced",
  "starter_code": "complete starter code",
  "test_cases": [
    {{"function": "solution", "input": "...", "expected_output": "..."}}
  ],
  "hints": ["hint 1", "hint 2"],
  "explanation": "short explanation of the intended solution"
}}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    result = _clean_json(response.text)

    required = [
        "title",
        "description",
        "skill",
        "language",
        "difficulty",
        "starter_code",
        "test_cases",
        "hints",
        "explanation",
    ]

    missing = [key for key in required if key not in result]
    if missing:
        raise ValueError(f"Gemini challenge missing fields: {missing}")

    return result
