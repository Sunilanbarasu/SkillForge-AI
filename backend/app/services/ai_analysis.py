import json
import re
from typing import Dict, Any, List

from app.core.config import settings
from app.schemas.ai_analysis import (
    AIAnalysisResultSchema,
    StrengthItem,
    WeaknessItem,
    SkillGapItem,
    PriorityItem,
    RecommendationItem,
)


def get_score_category(score: float) -> str:
    """Deterministic score categorization calculated by backend."""
    if score >= 80.0:
        return "Strong"
    elif score >= 65.0:
        return "Good"
    elif score >= 50.0:
        return "Needs Improvement"
    else:
        return "Critical"


def build_ai_input_payload(
    target_role: str,
    experience_level: str,
    overall_score: float,
    total_correct: int,
    total_questions: int,
    skill_scores: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Construct structured fact payload for the AI service."""
    formatted_skills = []

    for sk in skill_scores:
        score_val = float(sk.get("score", 0.0))

        formatted_skills.append(
            {
                "skill": sk.get("skill"),
                "score": score_val,
                "category": get_score_category(score_val),
                "correct_answers": sk.get("correct_answers"),
                "total_questions": sk.get("total_questions"),
            }
        )

    return {
        "target_role": target_role or "Software Developer",
        "experience_level": experience_level or "Student",
        "assessment": {
            "overall_score": overall_score,
            "total_correct": total_correct,
            "total_questions": total_questions,
        },
        "skills": formatted_skills,
    }


def generate_skill_gap_analysis(
    payload: Dict[str, Any],
) -> AIAnalysisResultSchema:
    """
    Generates AI skill-gap analysis using Google Gemini API.

    Numerical assessment facts are calculated by the backend.
    Gemini only interprets those facts and returns structured analysis.
    """

    api_key = settings.GEMINI_API_KEY.strip()

    # ---------------------------------------------------------
    # TEST / MOCK MODE
    # ---------------------------------------------------------
    # Used by the automated Phase 4/5/6 test suites.
    if api_key in ("mock_test_key", "MOCK_TEST_KEY", "TEST_MODE"):

        strengths = [
            StrengthItem(
                skill=s["skill"],
                reason=(
                    f"Your performance indicates strong proficiency "
                    f"with a score of {s['score']}%."
                ),
            )
            for s in payload.get("skills", [])
            if s["score"] >= 70.0
        ]

        weaknesses = [
            WeaknessItem(
                skill=s["skill"],
                reason=(
                    f"Your assessment score of {s['score']}% "
                    f"indicates areas requiring targeted preparation."
                ),
            )
            for s in payload.get("skills", [])
            if s["score"] < 70.0
        ]

        skill_gaps = [
            SkillGapItem(
                skill=s["skill"],
                gap=(
                    f"Foundational application and problem solving "
                    f"in {s['skill']}."
                ),
                focus_topics=[
                    f"{s['skill']} Fundamentals",
                    f"Advanced {s['skill']} Practice",
                ],
            )
            for s in payload.get("skills", [])
            if s["score"] < 70.0
        ]

        priorities = [
            PriorityItem(
                skill=s["skill"],
                priority="High" if s["score"] < 50.0 else "Medium",
                reason=f"Current performance is {s['category']}.",
            )
            for s in payload.get("skills", [])
            if s["score"] < 70.0
        ]

        recommendations = [
            RecommendationItem(
                skill=s["skill"],
                actions=[
                    f"Review core concepts of {s['skill']}",
                    (
                        f"Solve practice problems focusing on "
                        f"{s['skill']} edge cases"
                    ),
                ],
            )
            for s in payload.get("skills", [])
            if s["score"] < 70.0
        ]

        summary_text = (
            f"Your overall score is "
            f"{payload['assessment']['overall_score']}%. "
            f"Your assessment suggests strength in "
            f"{[
                s['skill']
                for s in payload.get('skills', [])
                if s['score'] >= 70
            ]} "
            f"and identifies priority preparation gaps in "
            f"{[
                s['skill']
                for s in payload.get('skills', [])
                if s['score'] < 70
            ]}."
        )

        return AIAnalysisResultSchema(
            summary=summary_text,
            strengths=strengths
            or [
                StrengthItem(
                    skill="Overall Aptitude",
                    reason="Completed diagnostic assessment.",
                )
            ],
            weaknesses=weaknesses
            or [
                WeaknessItem(
                    skill="Advanced Topics",
                    reason="Continued practice recommended.",
                )
            ],
            skill_gaps=skill_gaps
            or [
                SkillGapItem(
                    skill="DSA",
                    gap="Algorithmic problem solving",
                    focus_topics=["Binary Search", "Hash Tables"],
                )
            ],
            priorities=priorities
            or [
                PriorityItem(
                    skill="DSA",
                    priority="Medium",
                    reason="Placement core round Preparation.",
                )
            ],
            recommendations=recommendations
            or [
                RecommendationItem(
                    skill="DSA",
                    actions=["Practice binary search problems"],
                )
            ],
        )

    # ---------------------------------------------------------
    # LIVE GEMINI API
    # ---------------------------------------------------------
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured in backend "
            "environment variables (.env)."
        )

    system_instruction = (
        "You are SkillForge AI, a placement preparation analysis "
        "engine for software engineering students.\n"
        "Analyze the student's provided assessment facts and identify "
        "strengths, weaknesses, skill gaps, priorities, and practical "
        "preparation recommendations.\n\n"
        "CRITICAL RULES:\n"
        "1. The numerical scores provided are authoritative backend data. "
        "Never recalculate, modify, or invent scores.\n"
        "2. Only infer conclusions supported by the provided assessment "
        "scores.\n"
        "3. Do not invent student experience, projects, achievements, "
        "certifications, or assessment answers.\n"
        "4. Avoid generic advice like 'Practice more.' Provide specific "
        "placement preparation actions (e.g., 'Practice binary search "
        "problems involving boundary conditions and sorted arrays').\n"
        "5. Use supportive, evidence-based language such as "
        "'Your assessment suggests...' or "
        "'Your performance indicates...'\n"
        "6. Return ONLY valid JSON matching the required schema. "
        "No Markdown formatting surrounding the JSON."
    )

    user_prompt = (
        f"{system_instruction}\n\n"
        f"STUDENT ASSESSMENT FACTS:\n"
        f"{json.dumps(payload, indent=2)}\n\n"
        f"Return JSON matching exact structure:\n"
        "{\n"
        '  "summary": "Short overall placement-readiness interpretation",\n'
        '  "strengths": [{"skill": "SkillName", '
        '"reason": "Reason based on high score"}],\n'
        '  "weaknesses": [{"skill": "SkillName", '
        '"reason": "Reason based on low score"}],\n'
        '  "skill_gaps": [{"skill": "SkillName", '
        '"gap": "Explanation of knowledge gap", '
        '"focus_topics": ["Topic 1", "Topic 2"]}],\n'
        '  "priorities": [{"skill": "SkillName", '
        '"priority": "High/Medium/Low", '
        '"reason": "Priority rationale"}],\n'
        '  "recommendations": [{"skill": "SkillName", '
        '"actions": ["Action 1", "Action 2"]}]\n'
        "}"
    )

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=user_prompt,
        )

        response_text = response.text

    except Exception as e:
        raise ValueError(
            f"Gemini API call failed: {str(e)}"
        )

    # ---------------------------------------------------------
    # CLEAN GEMINI RESPONSE
    # ---------------------------------------------------------
    cleaned_json = response_text.strip()

    cleaned_json = re.sub(
        r"^```(json)?",
        "",
        cleaned_json,
        flags=re.IGNORECASE,
    )

    cleaned_json = re.sub(
        r"```$",
        "",
        cleaned_json,
    ).strip()

    # ---------------------------------------------------------
    # VALIDATE STRUCTURED RESPONSE
    # ---------------------------------------------------------
    try:
        data_dict = json.loads(cleaned_json)

        validated_analysis = AIAnalysisResultSchema.model_validate(
            data_dict
        )

        return validated_analysis

    except Exception as parse_err:
        raise ValueError(
            "Failed to parse and validate AI response JSON: "
            f"{str(parse_err)}"
        )
