from typing import Dict, List


# ============================================================
# SKILLFORGE ROLE PROFILES
# ============================================================
# Single source of truth for:
# - profession selection
# - assessment skill selection
# - placement alignment
# - adaptive learning priorities
# - AI study planning
# ============================================================

ROLE_PROFILES: Dict[str, Dict] = {

    "Software Engineer": {
        "description": "Build software systems, algorithms, APIs and production applications.",
        "skills": {
            "DSA": 1.00,
            "Python": 0.90,
            "OOP": 0.90,
            "SQL": 0.75,
            "DBMS": 0.75,
            "C": 0.60,
            "Aptitude": 0.70,
        },
    },

    "Software Developer": {
        "description": "Develop reliable applications and solve programming problems.",
        "skills": {
            "DSA": 1.00,
            "Python": 0.90,
            "OOP": 0.90,
            "SQL": 0.75,
            "DBMS": 0.75,
            "C": 0.60,
            "Aptitude": 0.70,
        },
    },

    "Full Stack Developer": {
        "description": "Build complete web applications across frontend, backend and databases.",
        "skills": {
            "JavaScript": 1.00,
            "React": 0.95,
            "APIs": 0.90,
            "Python": 0.80,
            "SQL": 0.85,
            "DBMS": 0.80,
            "DSA": 0.65,
        },
    },

    "Frontend Developer": {
        "description": "Build responsive, interactive and accessible user interfaces.",
        "skills": {
            "JavaScript": 1.00,
            "HTML/CSS": 0.95,
            "React": 0.95,
            "Web": 0.90,
            "DSA": 0.55,
            "Aptitude": 0.40,
        },
    },

    "Backend Developer": {
        "description": "Build APIs, application logic, databases and scalable backend systems.",
        "skills": {
            "APIs": 1.00,
            "Python": 0.95,
            "SQL": 0.95,
            "DBMS": 1.00,
            "OOP": 0.90,
            "DSA": 0.80,
            "Git": 0.60,
        },
    },

    "Data Analyst": {
        "description": "Analyze data, query databases and turn information into actionable insights.",
        "skills": {
            "SQL": 1.00,
            "Python": 0.90,
            "Statistics": 0.95,
            "Data Visualization": 0.95,
            "DBMS": 0.80,
            "Excel": 0.85,
            "Aptitude": 0.55,
        },
    },

    "Data Scientist": {
        "description": "Use statistics, Python and machine learning to solve data problems.",
        "skills": {
            "Python": 1.00,
            "Machine Learning": 1.00,
            "Statistics": 0.95,
            "SQL": 0.85,
            "Data Visualization": 0.75,
            "DSA": 0.55,
        },
    },

    "AI/ML Engineer": {
        "description": "Build, evaluate and deploy machine learning and AI systems.",
        "skills": {
            "Python": 1.00,
            "Machine Learning": 1.00,
            "Statistics": 0.90,
            "DSA": 0.85,
            "OOP": 0.80,
            "SQL": 0.60,
            "APIs": 0.65,
        },
    },

    "DevOps Engineer": {
        "description": "Automate software delivery, infrastructure and reliable production systems.",
        "skills": {
            "Linux": 1.00,
            "Cloud": 0.95,
            "CI/CD": 1.00,
            "Networking": 0.90,
            "Git": 0.90,
            "Python": 0.70,
            "Security": 0.65,
        },
    },

    "Cybersecurity Engineer": {
        "description": "Protect applications, systems, networks and data from security threats.",
        "skills": {
            "Cybersecurity": 1.00,
            "Networking": 0.95,
            "Linux": 0.90,
            "Security": 0.95,
            "Python": 0.75,
            "SQL": 0.65,
            "C": 0.60,
        },
    },
}


DEFAULT_ROLE = "Software Engineer"


def get_role_profile(target_role: str | None) -> Dict:
    """Return selected profession or safe default."""
    if target_role in ROLE_PROFILES:
        return ROLE_PROFILES[target_role]

    return ROLE_PROFILES[DEFAULT_ROLE]


def get_supported_roles() -> List[str]:
    """Return all professions supported by SkillForge."""
    return list(ROLE_PROFILES.keys())


def get_role_skills(target_role: str | None) -> List[str]:
    """Return role skills ordered by preparation priority."""
    profile = get_role_profile(target_role)

    return [
        skill
        for skill, _weight in sorted(
            profile["skills"].items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]


def get_role_weights(target_role: str | None) -> Dict[str, float]:
    """Return role preparation weights."""
    return dict(get_role_profile(target_role)["skills"])


# ============================================================
# EXPANDABLE CAREER CATALOG
# ============================================================
#
# ROLE_PROFILES contains detailed skill mappings for roles that
# SkillForge currently assesses directly.
#
# CAREER_CATALOG contains additional professions that can be
# added to the platform. New roles can later receive detailed
# AI-generated skill profiles without changing the UI architecture.
# ============================================================

CAREER_CATALOG = {
    "Technology": [
        "Software Engineer",
        "Software Developer",
        "Full Stack Developer",
        "Frontend Developer",
        "Backend Developer",
        "Mobile App Developer",
        "Web Developer",
        "Cloud Engineer",
        "DevOps Engineer",
        "Site Reliability Engineer",
        "Data Engineer",
        "Data Analyst",
        "Data Scientist",
        "AI/ML Engineer",
        "Machine Learning Engineer",
        "Computer Vision Engineer",
        "NLP Engineer",
        "Cybersecurity Engineer",
        "Security Engineer",
        "Network Engineer",
        "Database Administrator",
        "Solutions Architect",
        "System Administrator",
        "QA Engineer",
        "Automation Test Engineer",
        "Embedded Systems Engineer",
        "IoT Engineer",
        "Robotics Engineer",
        "Blockchain Developer",
        "Game Developer",
    ],

    "Design": [
        "UI/UX Designer",
        "Product Designer",
        "UX Researcher",
        "Visual Designer",
        "Graphic Designer",
        "Interaction Designer",
        "Motion Designer",
    ],

    "Product & Management": [
        "Product Manager",
        "Technical Product Manager",
        "Project Manager",
        "Program Manager",
        "Scrum Master",
        "Product Owner",
        "Engineering Manager",
    ],

    "Business & Analytics": [
        "Business Analyst",
        "Business Intelligence Analyst",
        "Financial Analyst",
        "Operations Analyst",
        "Marketing Analyst",
        "Management Consultant",
        "Risk Analyst",
    ],

    "Finance": [
        "Financial Planner",
        "Investment Analyst",
        "Credit Analyst",
        "Accountant",
        "Auditor",
        "FinTech Analyst",
    ],

    "Marketing & Sales": [
        "Digital Marketing Specialist",
        "SEO Specialist",
        "Content Strategist",
        "Social Media Manager",
        "Growth Marketer",
        "Sales Engineer",
        "Business Development Executive",
        "Account Executive",
    ],

    "Human Resources": [
        "HR Analyst",
        "HR Generalist",
        "Talent Acquisition Specialist",
        "Recruiter",
        "People Operations Specialist",
        "Learning & Development Specialist",
    ],

    "Engineering": [
        "Mechanical Engineer",
        "Electrical Engineer",
        "Electronics Engineer",
        "Civil Engineer",
        "Chemical Engineer",
        "Aerospace Engineer",
        "Automotive Engineer",
        "Biomedical Engineer",
        "Industrial Engineer",
        "Manufacturing Engineer",
        "Control Systems Engineer",
        "Mechatronics Engineer",
    ],

    "Media & Creative": [
        "Technical Writer",
        "Content Writer",
        "Copywriter",
        "Video Editor",
        "Content Creator",
        "Photographer",
        "Animator",
        "3D Artist",
    ],
}


def get_career_catalog():
    """Return the complete categorized career catalog."""
    return CAREER_CATALOG


def get_all_careers():
    """Return a flat list of every career in the catalog."""
    return [
        career
        for careers in CAREER_CATALOG.values()
        for career in careers
    ]


def is_supported_detailed_role(role: str) -> bool:
    """Return True when SkillForge has a detailed assessment profile."""
    return role in ROLE_PROFILES


def get_career_category(role: str):
    """Find the category containing a profession."""
    for category, careers in CAREER_CATALOG.items():
        if role in careers:
            return category
    return None
