from __future__ import annotations

import json
import re
from typing import Any

from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.question import Question
from app.services.career_skill_profiles import get_career_skill_profile
from app.services.role_profiles import ROLE_PROFILES


MODEL_NAME = "gemini-3.5-flash-lite"


def _get_gemini_client():
    api_key = getattr(settings, "GEMINI_API_KEY", None)

    if not api_key:
        raise RuntimeError("Gemini API key is not configured.")

    return genai.Client(api_key=api_key)


def _extract_json(text: str) -> Any:
    """
    Extract JSON even if Gemini wraps it in markdown.
    """
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)

        if not match:
            raise ValueError("Gemini did not return valid JSON.")

        return json.loads(match.group(0))


def _normalise_difficulty(difficulty: str | None) -> str:
    if not difficulty:
        return "Beginner"

    value = str(difficulty).strip().lower()

    mapping = {
        "beginner": "Beginner",
        "easy": "Beginner",
        "intermediate": "Intermediate",
        "medium": "Intermediate",
        "advanced": "Advanced",
        "hard": "Advanced",
    }

    return mapping.get(value, "Beginner")


def _get_profile(career: str):
    """
    Use the original detailed profiles first.
    Then use the expanded 81-career intelligence profiles.
    """
    if career in ROLE_PROFILES:
        return ROLE_PROFILES[career]

    profile = get_career_skill_profile(career)

    if not profile:
        raise ValueError(f"Unsupported target role: {career}")

    return profile


def _existing_questions_by_skill(
    db: Session,
    skills: list[str],
    difficulty: str,
) -> dict[str, list[Question]]:
    questions = (
        db.query(Question)
        .filter(
            Question.skill.in_(skills),
            Question.difficulty == difficulty,
        )
        .all()
    )

    result = {skill: [] for skill in skills}

    for question in questions:
        result.setdefault(question.skill, []).append(question)

    return result


def _validate_question(
    item: dict[str, Any],
    allowed_skills: set[str],
    difficulty: str,
) -> dict[str, Any] | None:

    required = [
        "skill",
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
    ]

    if not all(key in item for key in required):
        return None

    skill = str(item["skill"]).strip()

    if skill not in allowed_skills:
        return None

    question_text = str(item["question_text"]).strip()

    if not question_text:
        return None

    correct_answer = str(item["correct_answer"]).strip().upper()

    if correct_answer not in {"A", "B", "C", "D"}:
        return None

    options = {
        "option_a": str(item["option_a"]).strip(),
        "option_b": str(item["option_b"]).strip(),
        "option_c": str(item["option_c"]).strip(),
        "option_d": str(item["option_d"]).strip(),
    }

    if any(not value for value in options.values()):
        return None

    return {
        "skill": skill,
        "question_text": question_text,
        **options,
        "correct_answer": correct_answer,
        "difficulty": difficulty,
    }


def generate_missing_questions(
    db: Session,
    target_role: str,
    difficulty: str | None = None,
    questions_per_skill: int = 3,
) -> int:
    """
    Generate only the missing assessment questions for a career.

    Existing questions are preserved.
    Generated questions are validated before insertion.
    """

    difficulty = _normalise_difficulty(difficulty)

    profile = _get_profile(target_role)
    skills = list(profile["skills"].keys())

    if not skills:
        raise ValueError(f"No skills configured for target role: {target_role}")

    existing = _existing_questions_by_skill(
        db,
        skills,
        difficulty,
    )

    missing_counts: dict[str, int] = {}

    for skill in skills:
        current_count = len(existing.get(skill, []))
        missing = max(0, questions_per_skill - current_count)

        if missing > 0:
            missing_counts[skill] = missing

    if not missing_counts:
        return 0

    requested_skills = []

    for skill, count in missing_counts.items():
        requested_skills.append(
            {
                "skill": skill,
                "questions_needed": count,
            }
        )

    prompt = f"""
You are the assessment-question generator for SkillForge AI.

Generate high-quality multiple-choice placement assessment questions
for this career:

CAREER:
{target_role}

DIFFICULTY:
{difficulty}

SKILLS THAT NEED QUESTIONS:
{json.dumps(requested_skills, indent=2)}

Requirements:

1. Generate EXACTLY the requested number of questions for each skill.
2. Every question must test the named skill.
3. Questions must be appropriate for the specified career.
4. Do not create generic questions unrelated to the career.
5. Avoid duplicate questions.
6. Use four meaningful options.
7. Only one option may be correct.
8. The correct_answer must be exactly A, B, C, or D.
9. Do not include explanations.
10. Do not include markdown.
11. Return ONLY valid JSON.

Return this exact structure:

{{
  "questions": [
    {{
      "skill": "Skill Name",
      "question_text": "Question?",
      "option_a": "Option A",
      "option_b": "Option B",
      "option_c": "Option C",
      "option_d": "Option D",
      "correct_answer": "A"
    }}
  ]
}}
"""

    client = _get_gemini_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    raw_text = getattr(response, "text", None)

    if not raw_text:
        raise RuntimeError("Gemini returned an empty question-generation response.")

    payload = _extract_json(raw_text)

    if not isinstance(payload, dict):
        raise ValueError("Gemini response must be a JSON object.")

    generated = payload.get("questions", [])

    if not isinstance(generated, list):
        raise ValueError("Gemini questions field must be a list.")

    allowed_skills = set(skills)

    existing_keys = {
        (
            question.skill.strip(),
            question.question_text.strip().lower(),
        )
        for question_list in existing.values()
        for question in question_list
    }

    added = 0
    generated_counts = {skill: 0 for skill in missing_counts}

    for item in generated:
        if not isinstance(item, dict):
            continue

        validated = _validate_question(
            item,
            allowed_skills,
            difficulty,
        )

        if not validated:
            continue

        skill = validated["skill"]

        if skill not in missing_counts:
            continue

        if generated_counts[skill] >= missing_counts[skill]:
            continue

        key = (
            validated["skill"],
            validated["question_text"].strip().lower(),
        )

        if key in existing_keys:
            continue

        db.add(Question(**validated))
        existing_keys.add(key)
        generated_counts[skill] += 1
        added += 1

    db.commit()

    return added


def ensure_questions_for_career(
    db: Session,
    target_role: str,
    difficulty: str | None = None,
    questions_per_skill: int = 3,
) -> int:
    """
    Ensure the selected career has enough questions for every skill.

    Returns the number of newly generated questions.
    """

    return generate_missing_questions(
        db=db,
        target_role=target_role,
        difficulty=difficulty,
        questions_per_skill=questions_per_skill,
    )
