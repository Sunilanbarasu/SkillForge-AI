import json
import re
from typing import Dict, Any, List

from app.core.config import settings
from app.schemas.study_plan import StudyPlanAIResponse, StudyTask


# ============================================================
# NORMAL STUDY PLAN
# ============================================================

def build_study_plan_input_payload(
    target_role: str,
    experience_level: str,
    overall_score: float,
    skill_scores: List[Dict[str, Any]],
    ai_strengths: List[Dict[str, Any]],
    ai_weaknesses: List[Dict[str, Any]],
    ai_skill_gaps: List[Dict[str, Any]],
    ai_priorities: List[Dict[str, Any]],
    ai_recommendations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Construct structured fact payload for the AI study plan service."""

    formatted_skills = []

    for sk in skill_scores:
        formatted_skills.append({
            "skill": sk.get("skill"),
            "score": sk.get("score"),
            "category": sk.get("category"),
            "correct_answers": sk.get("correct_answers"),
            "total_questions": sk.get("total_questions")
        })

    return {
        "target_role": target_role or "Software Developer",
        "experience_level": experience_level or "Student",
        "assessment": {
            "overall_score": overall_score
        },
        "skills": formatted_skills,
        "ai_analysis": {
            "strengths": ai_strengths,
            "weaknesses": ai_weaknesses,
            "skill_gaps": ai_skill_gaps,
            "priorities": ai_priorities,
            "recommendations": ai_recommendations
        }
    }


def generate_study_plan(
    payload: Dict[str, Any]
) -> StudyPlanAIResponse:
    """Generates a personalized study plan using Google Gemini API."""

    api_key = settings.GEMINI_API_KEY.strip()

    # Test-only deterministic mode.
    if api_key in (
        "mock_test_key",
        "MOCK_TEST_KEY",
        "TEST_MODE"
    ):
        return _mock_study_plan(payload)

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured in backend "
            "environment variables (.env)."
        )

    system_instruction = _system_instruction()

    user_prompt = _user_prompt(
        payload,
        system_instruction
    )

    try:
        from google import genai

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=user_prompt,
        )

        response_text = response.text

    except Exception as e:
        raise ValueError(
            f"Gemini API call failed: {str(e)}"
        )

    cleaned_json = _clean_ai_json(response_text)

    try:
        data_dict = json.loads(cleaned_json)

        data_dict = _normalize_gemini_study_plan(
            data_dict
        )

        validated_plan = StudyPlanAIResponse.model_validate(
            data_dict
        )

        # Enforce deterministic study-plan rules.
        validated_plan = _enforce_task_durations(
            validated_plan
        )

        return validated_plan

    except Exception as parse_err:
        raise ValueError(
            "Failed to parse and validate AI response JSON: "
            f"{str(parse_err)}"
        )


def _mock_study_plan(
    payload: Dict[str, Any]
) -> StudyPlanAIResponse:
    """Deterministic mock study plan generator for tests."""

    skills_sorted = sorted(
        payload.get("skills", []),
        key=lambda s: float(
            s.get("score", 0)
        )
    )

    if not skills_sorted:
        skills_sorted = [
            {
                "skill": "DSA",
                "score": 0,
                "category": "Needs Improvement"
            }
        ]

    weak_skills = [
        s
        for s in skills_sorted
        if float(s.get("score", 0)) < 65.0
    ]

    strong_skills = [
        s
        for s in skills_sorted
        if float(s.get("score", 0)) >= 65.0
    ]

    priority_skills = (
        weak_skills
        or skills_sorted[:2]
    )

    tasks = []

    week_templates = {
        1: [
            "Review core fundamentals of {skill} and solve 3 beginner placement problems.",
            "Practice basic {skill} concepts with focused examples and short exercises.",
            "Identify common mistakes in {skill} and solve 3 targeted problems.",
            "Revise important {skill} concepts using active recall and write key notes.",
            "Complete a beginner placement-style {skill} practice set and review mistakes.",
        ],
        2: [
            "Practice intermediate {skill} problems focusing on common placement patterns.",
            "Solve 3 intermediate {skill} problems and explain the approach for each.",
            "Practice {skill} application questions under a time limit.",
            "Review mistakes from previous {skill} practice and solve similar problems.",
            "Complete an intermediate placement-style {skill} practice set.",
        ],
        3: [
            "Solve mixed {skill} application problems and review edge cases.",
            "Practice 3 timed {skill} problems using placement-style constraints.",
            "Work on a mini {skill} problem set covering multiple concepts.",
            "Analyze previous {skill} mistakes and retry the difficult questions.",
            "Complete a mixed-difficulty {skill} assessment and review the results.",
        ],
        4: [
            "Take a timed placement-style {skill} practice set and revise mistakes.",
            "Solve advanced {skill} problems commonly seen in technical interviews.",
            "Complete a mock placement test focused on {skill}.",
            "Review the most important {skill} concepts and weak areas from the plan.",
            "Complete a final {skill} challenge and record remaining improvement areas.",
        ],
    }

    for week in range(1, 5):

        for task_index in range(5):

            if priority_skills:
                skill_data = priority_skills[
                    (task_index + week - 1)
                    % len(priority_skills)
                ]
            else:
                skill_data = skills_sorted[
                    (task_index + week - 1)
                    % len(skills_sorted)
                ]

            skill = skill_data["skill"]

            difficulty = (
                "Beginner"
                if week == 1
                else "Intermediate"
                if week in (2, 3)
                else "Advanced"
            )

            tasks.append(
                StudyTask(
                    skill=skill,
                    week_number=week,
                    task=week_templates[week][task_index].format(
                        skill=skill
                    ),
                    difficulty=difficulty,
                    estimated_minutes=60
                )
            )

    if strong_skills:

        maintenance_skill = strong_skills[0]["skill"]

        tasks[-1] = StudyTask(
            skill=maintenance_skill,
            week_number=4,
            task=(
                f"Maintain {maintenance_skill} proficiency with "
                "a mixed placement practice set and quick revision."
            ),
            difficulty="Intermediate",
            estimated_minutes=45
        )

    return StudyPlanAIResponse(
        title=(
            f"{payload.get('target_role') or 'Software Developer'} "
            "Placement Plan"
        ),
        goal=(
            "Strengthen weaker skills through targeted practice "
            "while maintaining strong areas."
        ),
        duration_weeks=4,
        tasks=tasks
    )


# ============================================================
# STUDY-PLAN ENFORCEMENT
# ============================================================

def _enforce_task_durations(
    plan: StudyPlanAIResponse
) -> StudyPlanAIResponse:
    """
    Enforce SkillForge study-plan rules.

    Rules:
    - Maximum 5 tasks per week.
    - Normal tasks = 60 minutes.
    - Explicit maintenance tasks = 45 minutes.
    """

    tasks_by_week: Dict[int, List[StudyTask]] = {}

    # Group tasks by week while preserving AI-generated order.
    for task in plan.tasks:

        week = task.week_number

        if week not in tasks_by_week:
            tasks_by_week[week] = []

        # Keep a maximum of 5 tasks for each week.
        if len(tasks_by_week[week]) < 5:
            tasks_by_week[week].append(task)

    normalized_tasks = []

    # Rebuild tasks in chronological week order.
    for week in sorted(tasks_by_week):

        for task in tasks_by_week[week]:

            task_text = task.task.lower()

            if (
                "maintain" in task_text
                or "maintenance" in task_text
            ):
                minutes = 45
            else:
                minutes = 60

            normalized_tasks.append(
                task.model_copy(
                    update={
                        "estimated_minutes": minutes
                    }
                )
            )

    return plan.model_copy(
        update={
            "tasks": normalized_tasks
        }
    )


def _system_instruction() -> str:
    return (
        "You are SkillForge AI, a placement preparation planner.\n"
        "Create a practical study plan based ONLY on the provided student data.\n\n"

        "CRITICAL RULES:\n"

        "1. The numerical assessment scores are authoritative backend facts. "
        "Never change, recalculate, or invent scores.\n"

        "2. Prioritize weaker skills according to the supplied scores "
        "and AI skill-gap analysis.\n"

        "3. Do not invent student achievements, experience, certifications, "
        "or external URLs.\n"

        "4. Create actionable placement-preparation tasks suitable "
        "for a college student.\n"

        "5. Avoid vague tasks like 'Study DSA.' Provide specific, "
        "actionable tasks.\n"

        "6. Generate a study plan for exactly 4 weeks. "
        "Do not generate fewer or more than 4 weeks.\n"

        "7. Generate exactly 5 tasks per week, for exactly 20 tasks total.\n"

        "8. Standard study tasks are 60 minutes. "
        "Only explicit maintenance/revision tasks may be 45 minutes.\n"

        "9. Target approximately 60-90 minutes per study day.\n"

        "10. Do not generate hundreds of tasks.\n"

        "11. Do not require paid resources.\n"

        "12. Return ONLY valid JSON matching the requested schema. "
        "No Markdown formatting surrounding the JSON."
    )


def _user_prompt(
    payload: Dict[str, Any],
    system_instruction: str
) -> str:
    return (
        f"{system_instruction}\n\n"
        f"STUDENT ASSESSMENT FACTS:\n"
        f"{json.dumps(payload, indent=2)}\n\n"

        "Return JSON matching exact structure:\n"

        "{\n"
        '  "title": "Software Developer Placement Plan",\n'
        '  "goal": "Strengthen DSA and DBMS while maintaining strong SQL skills.",\n'
        '  "duration_weeks": 4,\n'
        '  "tasks": [\n'
        '    {\n'
        '      "skill": "DSA",\n'
        '      "week_number": 1,\n'
        '      "task": "Review time complexity and solve 3 beginner problems.",\n'
        '      "difficulty": "Beginner",\n'
        '      "estimated_minutes": 60\n'
        "    }\n"
        "  ]\n"
        "}"
    )


# ============================================================
# ADAPTIVE STUDY PLAN
# ============================================================

def build_adaptive_study_plan_input_payload(
    target_role: str,
    experience_level: str,
    previous_overall_score: float,
    current_overall_score: float,
    overall_score_change: float,
    skill_progress: List[Dict[str, Any]],
    ai_strengths: List[Dict[str, Any]],
    ai_weaknesses: List[Dict[str, Any]],
    ai_skill_gaps: List[Dict[str, Any]],
    ai_priorities: List[Dict[str, Any]],
    ai_recommendations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Construct structured facts for an adaptive study plan."""

    return {
        "target_role": target_role or "Software Developer",
        "experience_level": experience_level or "Student",

        "previous_assessment": {
            "overall_score": previous_overall_score
        },

        "current_assessment": {
            "overall_score": current_overall_score
        },

        "overall_score_change": overall_score_change,

        "skill_progress": skill_progress,

        "ai_analysis": {
            "strengths": ai_strengths,
            "weaknesses": ai_weaknesses,
            "skill_gaps": ai_skill_gaps,
            "priorities": ai_priorities,
            "recommendations": ai_recommendations
        }
    }


def generate_adaptive_study_plan(
    payload: Dict[str, Any]
) -> StudyPlanAIResponse:
    """
    Generates a new study plan based on reassessment progress.

    Backend-provided numerical progress values are authoritative.
    """

    api_key = settings.GEMINI_API_KEY.strip()

    # --------------------------------------------------------
    # TEST MODE
    # --------------------------------------------------------

    if api_key in (
        "mock_test_key",
        "MOCK_TEST_KEY",
        "TEST_MODE"
    ):
        return _mock_adaptive_study_plan(payload)

    # --------------------------------------------------------
    # PRODUCTION MODE
    # --------------------------------------------------------

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured in backend "
            "environment variables (.env)."
        )

    system_instruction = (
        "You are SkillForge AI, an adaptive placement preparation planner.\n"
        "Create a NEW 4-week study plan based ONLY on the supplied "
        "student progress data.\n\n"

        "CRITICAL RULES:\n"

        "1. Backend numerical scores and score changes are authoritative facts.\n"

        "2. Never change, recalculate, or invent scores.\n"

        "3. Prioritize skills that are weak or declined.\n"

        "4. Skills that improved strongly should receive maintenance "
        "rather than excessive repetition.\n"

        "5. Unchanged skills should receive appropriate continued practice.\n"

        "6. Create specific, actionable placement-preparation tasks.\n"

        "7. Generate exactly 4 weeks.\n"

        "8. Generate exactly 5 tasks per week, for exactly 20 tasks total.\n"

        "9. Standard study tasks are 60 minutes. "
        "Only explicit maintenance/revision tasks may be 45 minutes.\n"

        "10. Do not generate hundreds of tasks.\n"

        "11. Do not require paid resources.\n"

        "12. Return ONLY valid JSON matching the requested schema.\n"
    )

    user_prompt = (
        f"{system_instruction}\n\n"

        f"STUDENT PROGRESS FACTS:\n"
        f"{json.dumps(payload, indent=2)}\n\n"

        "ADAPTATION REQUIREMENTS:\n"

        "Use the skill_progress values to determine how the roadmap "
        "should change.\n"

        "Give additional focus to skills marked Declined.\n"

        "Give strong focus to skills that remain weak even if they improved.\n"

        "Use maintenance tasks for skills that are already strong.\n"

        "Do not claim improvement or decline that is not present in the data.\n\n"

        "Return JSON matching this structure:\n"

        "{\n"
        '  "title": "Adaptive Software Developer Placement Plan",\n'
        '  "goal": "Focus on weaker and declining skills while maintaining improved skills.",\n'
        '  "duration_weeks": 4,\n'
        '  "tasks": [\n'
        '    {\n'
        '      "skill": "DSA",\n'
        '      "week_number": 1,\n'
        '      "task": "Solve 3 targeted placement problems based on recent weaknesses.",\n'
        '      "difficulty": "Intermediate",\n'
        '      "estimated_minutes": 60\n'
        '    }\n'
        '  ]\n'
        "}"
    )

    try:
        from google import genai

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=user_prompt,
        )

        response_text = response.text

    except Exception as e:

        raise ValueError(
            f"Gemini API call failed: {str(e)}"
        )

    cleaned_json = _clean_ai_json(
        response_text
    )

    try:
        data_dict = json.loads(
            cleaned_json
        )

        data_dict = _normalize_gemini_study_plan(
            data_dict
        )

        validated_plan = StudyPlanAIResponse.model_validate(
            data_dict
        )

        # Enforce deterministic study-plan rules.
        validated_plan = _enforce_task_durations(
            validated_plan
        )

        return validated_plan

    except Exception as parse_err:

        raise ValueError(
            "Failed to parse and validate adaptive AI response JSON: "
            f"{str(parse_err)}"
        )


def _mock_adaptive_study_plan(
    payload: Dict[str, Any]
) -> StudyPlanAIResponse:
    """
    Deterministic adaptive study-plan generator used only for tests.

    Priority order:
    1. Declined skills
    2. Weak skills
    3. Unchanged skills
    4. Improved skills for maintenance
    """

    progress = payload.get(
        "skill_progress",
        []
    )

    if not progress:

        progress = [
            {
                "skill": "DSA",
                "previous_score": 0,
                "current_score": 0,
                "score_change": 0,
                "status": "Unchanged"
            }
        ]

    status_priority = {
        "Declined": 0,
        "Unchanged": 1,
        "Improved": 2
    }

    ordered_progress = sorted(
        progress,
        key=lambda item: (
            status_priority.get(
                item.get("status"),
                3
            ),
            float(
                item.get(
                    "current_score",
                    0
                )
            )
        )
    )

    # --------------------------------------------------------
    # Select skills requiring focus.
    # --------------------------------------------------------

    focus_skills = [
        item
        for item in ordered_progress
        if (
            item.get("status") == "Declined"
            or float(
                item.get(
                    "current_score",
                    0
                )
            ) < 65
        )
    ]

    # If all skills are strong/improved,
    # use improved skills for maintenance.
    if not focus_skills:

        focus_skills = [
            item
            for item in ordered_progress
            if item.get("status") == "Improved"
        ]

    if not focus_skills:

        focus_skills = ordered_progress[:2]

    tasks = []

    week_templates = {
        1: [
            "Review the most important {skill} concepts and identify remaining weak areas.",
            "Solve 3 targeted {skill} placement problems and review every mistake.",
            "Practice {skill} application questions using a timed approach.",
            "Revise common {skill} interview patterns and solve 3 practice questions.",
            "Complete a focused {skill} placement practice set and analyze the result.",
        ],

        2: [
            "Solve 3 intermediate {skill} problems focused on placement patterns.",
            "Practice {skill} problems under a time limit and review mistakes.",
            "Work through a mixed {skill} problem set covering multiple concepts.",
            "Explain the solution approach for 3 {skill} problems without referring to notes.",
            "Complete an intermediate {skill} practice test and record weak topics.",
        ],

        3: [
            "Solve mixed-difficulty {skill} problems and analyze edge cases.",
            "Complete 3 timed {skill} problems using interview-style constraints.",
            "Review previous {skill} mistakes and solve similar problems again.",
            "Practice a mini {skill} assessment covering multiple concepts.",
            "Identify remaining {skill} gaps and complete targeted practice.",
        ],

        4: [
            "Take a timed placement-style {skill} practice set and review mistakes.",
            "Solve advanced {skill} problems commonly used in technical interviews.",
            "Complete a mock placement test focused on {skill}.",
            "Review high-value {skill} concepts and remaining weak areas.",
            "Complete a final {skill} challenge and record remaining improvement areas.",
        ],
    }

    # --------------------------------------------------------
    # Generate exactly 5 tasks per week.
    # --------------------------------------------------------

    for week in range(1, 5):

        for task_index in range(5):

            skill_data = focus_skills[
                (task_index + week - 1)
                % len(focus_skills)
            ]

            skill = skill_data["skill"]

            current_score = float(
                skill_data.get(
                    "current_score",
                    0
                )
            )

            skill_status = skill_data.get(
                "status"
            )

            if skill_status == "Declined":

                task_prefix = (
                    "Priority recovery: "
                )

            elif current_score < 65:

                task_prefix = (
                    "Weak-skill focus: "
                )

            else:

                task_prefix = ""

            difficulty = (
                "Beginner"
                if week == 1
                else "Intermediate"
                if week in (2, 3)
                else "Advanced"
            )

            task_text = (
                task_prefix
                + week_templates[week][task_index].format(
                    skill=skill
                )
            )

            tasks.append(
                StudyTask(
                    skill=skill,
                    week_number=week,
                    task=task_text,
                    difficulty=difficulty,
                    estimated_minutes=60
                )
            )

    # --------------------------------------------------------
    # Add maintenance for a strong improved skill.
    # --------------------------------------------------------

    maintenance_skills = [
        item
        for item in ordered_progress
        if (
            item.get("status") == "Improved"
            and float(
                item.get(
                    "current_score",
                    0
                )
            ) >= 80
        )
    ]

    if maintenance_skills:

        maintenance_skill = (
            maintenance_skills[0]["skill"]
        )

        tasks[-1] = StudyTask(
            skill=maintenance_skill,
            week_number=4,
            task=(
                f"Maintain {maintenance_skill} proficiency with "
                "a mixed placement practice set and quick revision."
            ),
            difficulty="Intermediate",
            estimated_minutes=45
        )

    return StudyPlanAIResponse(
        title=(
            f"{payload.get('target_role') or 'Software Developer'} "
            "Adaptive Placement Plan"
        ),
        goal=(
            "Adapt preparation using reassessment progress by "
            "prioritizing weak or declining skills while maintaining "
            "strong skills."
        ),
        duration_weeks=4,
        tasks=tasks
    )


# ============================================================
# GEMINI RESPONSE NORMALIZATION
# ============================================================

def _normalize_gemini_study_plan(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize common Gemini field names into the existing
    SkillForge StudyPlanAIResponse schema.

    SkillForge requires:
    - skill
    - week_number
    - task
    - difficulty
    - estimated_minutes

    Gemini may return equivalent names such as:
    - week / week_number
    - task_description / description / activity / task
    - duration_minutes / duration / estimated_minutes
    """

    if not isinstance(data, dict):
        raise ValueError(
            "Gemini study-plan response must be a JSON object."
        )

    tasks = data.get("tasks")

    if not isinstance(tasks, list):
        raise ValueError(
            "Gemini study-plan response must contain a tasks list."
        )

    normalized_tasks = []

    for index, task in enumerate(tasks):

        if not isinstance(task, dict):
            raise ValueError(
                f"Gemini study-plan task {index + 1} must be an object."
            )

        normalized_task = dict(task)

        # ----------------------------------------------------
        # SKILL
        # ----------------------------------------------------

        skill = normalized_task.get("skill")

        if not skill:
            skill = normalized_task.get("topic")

        if not skill:
            raise ValueError(
                f"Gemini study-plan task {index + 1} "
                "is missing skill."
            )

        normalized_task["skill"] = str(skill).strip()

        # ----------------------------------------------------
        # WEEK NUMBER
        # ----------------------------------------------------

        week_number = normalized_task.get("week_number")

        if week_number is None:
            week_number = normalized_task.get("week")

        if week_number is None:
            raise ValueError(
                f"Gemini study-plan task {index + 1} "
                "is missing week/week_number."
            )

        try:
            week_number = int(week_number)
        except (TypeError, ValueError):
            raise ValueError(
                f"Gemini study-plan task {index + 1} "
                "has an invalid week number."
            )

        normalized_task["week_number"] = week_number

        # ----------------------------------------------------
        # TASK TEXT
        # ----------------------------------------------------

        task_text = normalized_task.get("task")

        if not task_text:
            task_text = normalized_task.get("task_description")

        if not task_text:
            task_text = normalized_task.get("description")

        if not task_text:
            task_text = normalized_task.get("activity")

        if not task_text:
            raise ValueError(
                f"Gemini study-plan task {index + 1} "
                "is missing task/task_description."
            )

        normalized_task["task"] = str(task_text).strip()

        # ----------------------------------------------------
        # ESTIMATED MINUTES
        # ----------------------------------------------------

        estimated_minutes = normalized_task.get(
            "estimated_minutes"
        )

        if estimated_minutes is None:
            estimated_minutes = normalized_task.get(
                "duration_minutes"
            )

        if estimated_minutes is None:
            estimated_minutes = normalized_task.get(
                "duration"
            )

        if estimated_minutes is None:
            estimated_minutes = 60

        try:
            estimated_minutes = int(estimated_minutes)
        except (TypeError, ValueError):
            estimated_minutes = 60

        normalized_task["estimated_minutes"] = estimated_minutes

        # ----------------------------------------------------
        # DIFFICULTY
        # ----------------------------------------------------

        difficulty = normalized_task.get("difficulty")

        if not difficulty:
            if week_number == 1:
                difficulty = "Beginner"
            elif week_number in (2, 3):
                difficulty = "Intermediate"
            else:
                difficulty = "Advanced"

        difficulty_map = {
            "beginner": "Beginner",
            "basic": "Beginner",
            "easy": "Beginner",
            "intermediate": "Intermediate",
            "medium": "Intermediate",
            "moderate": "Intermediate",
            "advanced": "Advanced",
            "hard": "Advanced",
            "expert": "Advanced",
        }

        difficulty = difficulty_map.get(
            str(difficulty).strip().lower(),
            str(difficulty).strip()
        )

        normalized_task["difficulty"] = difficulty

        # ----------------------------------------------------
        # REMOVE GEMINI-ONLY ALIASES
        # ----------------------------------------------------

        normalized_task.pop("week", None)
        normalized_task.pop("day", None)
        normalized_task.pop("topic", None)
        normalized_task.pop("task_description", None)
        normalized_task.pop("description", None)
        normalized_task.pop("activity", None)
        normalized_task.pop("duration_minutes", None)
        normalized_task.pop("duration", None)

        normalized_tasks.append(normalized_task)

    normalized_data = dict(data)
    normalized_data["tasks"] = normalized_tasks

    return normalized_data


# ============================================================
# SHARED AI RESPONSE CLEANUP
# ============================================================

def _clean_ai_json(
    response_text: str
) -> str:
    """Remove optional Markdown code fences from an AI JSON response."""

    cleaned_json = response_text.strip()

    cleaned_json = re.sub(
        r"^```(?:json)?",
        "",
        cleaned_json,
        flags=re.IGNORECASE
    )

    cleaned_json = re.sub(
        r"```$",
        "",
        cleaned_json
    )

    return cleaned_json.strip()

# ============================================================
# PHASE 2 - PHASE-1-AWARE PERSONALIZED STUDY PLAN
# ============================================================

def build_phase1_personalized_plan_payload(
    target_role: str,
    experience_level: str,
    assessment_id: int,
    overall_score: float,
    adaptive_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a personalized study-plan payload directly from
    the deterministic Phase 1 adaptive analysis.
    """

    return {
        "target_role": target_role or "Software Developer",
        "experience_level": experience_level or "Student",
        "assessment": {
            "assessment_id": assessment_id,
            "overall_score": overall_score,
        },
        "adaptive_analysis": {
            "strong_skills": adaptive_analysis.get("strong_skills", []),
            "good_skills": adaptive_analysis.get("good_skills", []),
            "weak_skills": adaptive_analysis.get("weak_skills", []),
            "critical_skills": adaptive_analysis.get("critical_skills", []),
            "improving_skills": adaptive_analysis.get("improving_skills", []),
            "declining_skills": adaptive_analysis.get("declining_skills", []),
            "priority_skills": adaptive_analysis.get("priority_skills", []),
            "skills": adaptive_analysis.get("skills", []),
        },
    }


def generate_phase1_personalized_study_plan(
    payload: Dict[str, Any]
) -> StudyPlanAIResponse:
    """
    Generate a personalized 4-week study plan directly from
    Phase 1 adaptive analysis.
    """

    api_key = settings.GEMINI_API_KEY.strip()

    if api_key in (
        "mock_test_key",
        "MOCK_TEST_KEY",
        "TEST_MODE"
    ):
        return _mock_phase1_personalized_study_plan(payload)

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured in backend "
            "environment variables (.env)."
        )

    system_instruction = (
        "You are SkillForge AI, an adaptive placement preparation planner.\n"
        "Create a personalized 4-week placement preparation plan "
        "using ONLY the supplied Phase 1 adaptive analysis.\n\n"

        "RULES:\n"
        "1. Backend assessment scores and skill accuracies are authoritative.\n"
        "2. Never invent or change numerical scores.\n"
        "3. Critical skills receive the strongest learning focus.\n"
        "4. Weak skills receive strong targeted practice.\n"
        "5. Strong and Good skills receive maintenance where appropriate.\n"
        "6. Use supplied priority_skills as the primary focus.\n"
        "7. Every task must name a real skill from the supplied data.\n"
        "8. Tasks must be specific and actionable for placement preparation.\n"
        "9. Generate exactly 4 weeks.\n"
        "10. Generate exactly 5 tasks per week.\n"
        "11. Generate exactly 20 tasks total.\n"
        "12. Standard tasks are 60 minutes.\n"
        "13. Only explicit maintenance tasks may be 45 minutes.\n"
        "14. Do not require paid resources.\n"
        "15. Return ONLY valid JSON.\n"
    )

    user_prompt = (
        f"{system_instruction}\n\n"
        "PHASE 1 ADAPTIVE ANALYSIS:\n"
        f"{json.dumps(payload, indent=2)}\n\n"

        "ADAPTIVE BEHAVIOR:\n"
        "Prioritize the supplied priority_skills.\n"
        "Give the most attention to Critical skills.\n"
        "Then address Weak and Needs Improvement skills.\n"
        "Use maintenance for strong skills when appropriate.\n"
        "Do not claim improvement unless the supplied data says so.\n\n"

        "Return JSON matching this structure:\n"
        "{\n"
        '  "title": "Personalized Software Developer Placement Plan",\n'
        '  "goal": "Improve the highest-priority skills identified by the adaptive assessment.",\n'
        '  "duration_weeks": 4,\n'
        '  "tasks": []\n'
        "}"
    )

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=user_prompt,
        )

        response_text = response.text

    except Exception as e:
        raise ValueError(
            f"Gemini API call failed: {str(e)}"
        )

    cleaned_json = _clean_ai_json(response_text)

    try:
        data_dict = json.loads(cleaned_json)

        data_dict = _normalize_gemini_study_plan(
            data_dict
        )

        validated_plan = StudyPlanAIResponse.model_validate(
            data_dict
        )

        return _enforce_task_durations(validated_plan)

    except Exception as parse_err:
        raise ValueError(
            "Failed to parse and validate personalized AI response JSON: "
            f"{str(parse_err)}"
        )


def _mock_phase1_personalized_study_plan(
    payload: Dict[str, Any]
) -> StudyPlanAIResponse:
    """
    Deterministic test-mode generator using actual Phase 1 priorities.
    """

    adaptive = payload.get(
        "adaptive_analysis",
        {}
    )

    skills_data = adaptive.get(
        "skills",
        []
    )

    priority_skills = adaptive.get(
        "priority_skills",
        []
    )

    critical_skills = adaptive.get(
        "critical_skills",
        []
    )

    weak_skills = adaptive.get(
        "weak_skills",
        []
    )

    # Build skill order from actual Phase 1 data.
    skill_order = list(
        dict.fromkeys(
            critical_skills
            + priority_skills
            + weak_skills
        )
    )

    # Only use skills that actually exist in Phase 1 results.
    actual_skills = {
        item.get("skill")
        for item in skills_data
        if item.get("skill")
    }

    skill_order = [
        skill
        for skill in skill_order
        if skill in actual_skills
    ]

    if not skill_order:
        skill_order = [
            item.get("skill")
            for item in skills_data
            if item.get("skill")
        ]

    if not skill_order:
        skill_order = ["DSA"]

    templates = {
        1: [
            "Review the core fundamentals of {skill} and identify weak concepts.",
            "Solve 3 beginner {skill} placement problems and review every mistake.",
            "Practice basic {skill} concepts using active recall and short exercises.",
            "Revise common {skill} placement patterns and solve 3 targeted questions.",
            "Complete a focused {skill} practice set and analyze incorrect answers.",
        ],
        2: [
            "Solve 3 intermediate {skill} placement problems.",
            "Practice {skill} application questions under a time limit.",
            "Complete a mixed {skill} problem set and review mistakes.",
            "Explain the approach for 3 {skill} problems before checking solutions.",
            "Complete an intermediate {skill} practice test and record weak topics.",
        ],
        3: [
            "Solve mixed-difficulty {skill} placement problems.",
            "Complete 3 timed {skill} problems using interview-style constraints.",
            "Retry difficult {skill} questions without looking at the answers.",
            "Complete a mini {skill} assessment covering multiple concepts.",
            "Identify remaining {skill} gaps and complete targeted practice.",
        ],
        4: [
            "Take a timed placement-style {skill} practice set.",
            "Solve advanced {skill} interview problems.",
            "Complete a mock placement test focused on {skill}.",
            "Review high-value {skill} concepts and remaining weak areas.",
            "Complete a final {skill} challenge and record remaining improvement areas.",
        ],
    }

    tasks = []

    for week in range(1, 5):
        for index in range(5):

            skill = skill_order[
                (index + week - 1) % len(skill_order)
            ]

            difficulty = (
                "Beginner"
                if week == 1
                else "Intermediate"
                if week in (2, 3)
                else "Advanced"
            )

            tasks.append(
                StudyTask(
                    skill=skill,
                    week_number=week,
                    task=templates[week][index].format(
                        skill=skill
                    ),
                    difficulty=difficulty,
                    estimated_minutes=60
                )
            )

    return StudyPlanAIResponse(
        title=(
            f"{payload.get('target_role') or 'Software Developer'} "
            "Personalized Placement Plan"
        ),
        goal=(
            "Improve the highest-priority skills identified "
            "by the student's Phase 1 adaptive assessment."
        ),
        duration_weeks=4,
        tasks=tasks
    )

