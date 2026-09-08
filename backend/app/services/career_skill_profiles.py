
"""
Skill intelligence for every career in the SkillForge career catalog.

The existing ROLE_PROFILES remain the authoritative detailed profiles for
the original 10 assessment roles. This module extends the same concept to
the complete career catalog without silently converting careers to another
profession.
"""

from app.services.role_profiles import get_all_careers, get_career_catalog


# ---------------------------------------------------------------------------
# Skill libraries
# ---------------------------------------------------------------------------

TECH_SKILLS = [
    "Programming",
    "Data Structures",
    "Algorithms",
    "Software Design",
    "Databases",
    "APIs",
    "Git",
    "Testing",
]

WEB_SKILLS = [
    "HTML/CSS",
    "JavaScript",
    "Web",
    "UI Development",
    "APIs",
    "Git",
    "Testing",
]

DATA_SKILLS = [
    "Python",
    "SQL",
    "Statistics",
    "Data Analysis",
    "Data Visualization",
    "Databases",
    "Excel",
]

AI_SKILLS = [
    "Python",
    "Machine Learning",
    "Statistics",
    "Data Analysis",
    "Data Visualization",
    "Algorithms",
    "SQL",
]

CLOUD_SKILLS = [
    "Linux",
    "Cloud",
    "Networking",
    "CI/CD",
    "Git",
    "Python",
    "Security",
]

SECURITY_SKILLS = [
    "Cybersecurity",
    "Networking",
    "Security",
    "Linux",
    "Python",
    "SQL",
]

DESIGN_SKILLS = [
    "UI/UX Design",
    "User Research",
    "Visual Design",
    "Interaction Design",
    "Prototyping",
    "Design Systems",
    "Accessibility",
]

PRODUCT_SKILLS = [
    "Product Strategy",
    "User Research",
    "Product Analytics",
    "Agile",
    "Project Management",
    "Communication",
    "Problem Solving",
]

BUSINESS_SKILLS = [
    "Business Analysis",
    "Data Analysis",
    "Statistics",
    "Excel",
    "SQL",
    "Communication",
    "Problem Solving",
]

FINANCE_SKILLS = [
    "Financial Analysis",
    "Accounting",
    "Excel",
    "Statistics",
    "Risk Management",
    "Financial Modeling",
    "Business Analysis",
]

MARKETING_SKILLS = [
    "Digital Marketing",
    "Market Research",
    "Content Strategy",
    "SEO",
    "Analytics",
    "Communication",
    "Sales",
]

HR_SKILLS = [
    "Human Resources",
    "Recruitment",
    "Communication",
    "People Analytics",
    "Employee Relations",
    "Talent Management",
    "Problem Solving",
]

ENGINEERING_SKILLS = [
    "Engineering Mathematics",
    "Engineering Design",
    "CAD",
    "Problem Solving",
    "Project Management",
    "Technical Analysis",
    "Safety",
]

CREATIVE_SKILLS = [
    "Content Creation",
    "Writing",
    "Visual Storytelling",
    "Communication",
    "Editing",
    "Creative Thinking",
    "Digital Media",
]


def _profile(skills, weights=None, category="Technology"):
    if weights is None:
        weights = {}

    result = {}
    total = len(skills)

    for index, skill in enumerate(skills):
        if skill in weights:
            weight = weights[skill]
        else:
            # Earlier skills are slightly more important by default.
            weight = max(0.45, round(0.90 - (index * 0.06), 2))

        result[skill] = weight

    return {
        "category": category,
        "skills": result,
    }


# ---------------------------------------------------------------------------
# Explicit career profiles
# ---------------------------------------------------------------------------

CAREER_SKILL_PROFILES = {

    # Technology ------------------------------------------------------------

    "Mobile App Developer": _profile(
        ["Java", "Kotlin", "Swift", "Mobile Development", "APIs", "Git", "Testing"],
    ),

    "Web Developer": _profile(
        WEB_SKILLS,
    ),

    "Cloud Engineer": _profile(
        ["Cloud", "Linux", "Networking", "Python", "Security", "Git", "CI/CD"],
    ),

    "Site Reliability Engineer": _profile(
        ["Linux", "Cloud", "Networking", "CI/CD", "Monitoring", "Python", "Security"],
    ),

    "Data Engineer": _profile(
        ["Python", "SQL", "Data Engineering", "Databases", "ETL", "Cloud", "Data Modeling"],
    ),

    "Machine Learning Engineer": _profile(
        ["Python", "Machine Learning", "Statistics", "Algorithms", "Data Engineering", "APIs", "Cloud"],
    ),

    "Computer Vision Engineer": _profile(
        ["Python", "Computer Vision", "Machine Learning", "Deep Learning", "Image Processing", "Statistics", "Algorithms"],
    ),

    "NLP Engineer": _profile(
        ["Python", "Natural Language Processing", "Machine Learning", "Deep Learning", "Statistics", "Algorithms", "APIs"],
    ),

    "Security Engineer": _profile(
        SECURITY_SKILLS,
    ),

    "Network Engineer": _profile(
        ["Networking", "Linux", "Security", "Cloud", "Network Administration", "Troubleshooting", "Python"],
    ),

    "Database Administrator": _profile(
        ["SQL", "Databases", "Database Administration", "Linux", "Security", "Backup & Recovery", "Performance Tuning"],
    ),

    "Solutions Architect": _profile(
        ["System Architecture", "Cloud", "APIs", "Databases", "Security", "Networking", "Problem Solving"],
    ),

    "System Administrator": _profile(
        ["Linux", "System Administration", "Networking", "Security", "Cloud", "Scripting", "Troubleshooting"],
    ),

    "QA Engineer": _profile(
        ["Software Testing", "Test Design", "Automation", "Programming", "APIs", "Git", "Debugging"],
    ),

    "Automation Test Engineer": _profile(
        ["Test Automation", "Programming", "Software Testing", "APIs", "Selenium", "Git", "CI/CD"],
    ),

    "Embedded Systems Engineer": _profile(
        ["C", "C++", "Embedded Systems", "Microcontrollers", "Electronics", "RTOS", "Debugging"],
    ),

    "IoT Engineer": _profile(
        ["IoT", "Embedded Systems", "Networking", "Python", "Cloud", "Sensors", "Security"],
    ),

    "Robotics Engineer": _profile(
        ["Robotics", "C++", "Python", "Control Systems", "Computer Vision", "Embedded Systems", "Algorithms"],
    ),

    "Blockchain Developer": _profile(
        ["Blockchain", "Solidity", "Cryptography", "Programming", "Smart Contracts", "Web3", "Security"],
    ),

    "Game Developer": _profile(
        ["Game Development", "C++", "C#", "Game Engines", "3D Mathematics", "Algorithms", "Graphics"],
    ),

    # Design ----------------------------------------------------------------

    "UI/UX Designer": _profile(
        DESIGN_SKILLS,
        category="Design",
    ),

    "Product Designer": _profile(
        ["UI/UX Design", "User Research", "Product Strategy", "Prototyping", "Visual Design", "Design Systems", "Accessibility"],
        category="Design",
    ),

    "UX Researcher": _profile(
        ["User Research", "User Interviews", "Usability Testing", "Data Analysis", "Psychology", "Product Analytics", "Communication"],
        category="Design",
    ),

    "Visual Designer": _profile(
        ["Visual Design", "Typography", "Color Theory", "Brand Design", "Graphic Design", "Design Systems", "Digital Media"],
        category="Design",
    ),

    "Graphic Designer": _profile(
        ["Graphic Design", "Visual Design", "Typography", "Color Theory", "Brand Design", "Adobe Creative Tools", "Creative Thinking"],
        category="Design",
    ),

    "Interaction Designer": _profile(
        ["Interaction Design", "UI/UX Design", "User Research", "Prototyping", "Information Architecture", "Accessibility", "Usability Testing"],
        category="Design",
    ),

    "Motion Designer": _profile(
        ["Motion Design", "Animation", "Visual Storytelling", "Video Editing", "Typography", "Graphic Design", "Creative Thinking"],
        category="Design",
    ),

    # Product & Management --------------------------------------------------

    "Product Manager": _profile(
        PRODUCT_SKILLS,
        category="Product & Management",
    ),

    "Technical Product Manager": _profile(
        ["Product Strategy", "Software Development", "APIs", "System Architecture", "Product Analytics", "Agile", "Communication"],
        category="Product & Management",
    ),

    "Project Manager": _profile(
        ["Project Management", "Planning", "Risk Management", "Communication", "Agile", "Budget Management", "Leadership"],
        category="Product & Management",
    ),

    "Program Manager": _profile(
        ["Program Management", "Project Management", "Planning", "Risk Management", "Leadership", "Communication", "Business Analysis"],
        category="Product & Management",
    ),

    "Scrum Master": _profile(
        ["Agile", "Scrum", "Facilitation", "Communication", "Conflict Resolution", "Team Leadership", "Project Management"],
        category="Product & Management",
    ),

    "Product Owner": _profile(
        ["Product Strategy", "Backlog Management", "User Research", "Agile", "Product Analytics", "Communication", "Problem Solving"],
        category="Product & Management",
    ),

    "Engineering Manager": _profile(
        ["Software Development", "System Design", "Engineering Management", "Leadership", "Project Management", "Agile", "Communication"],
        category="Product & Management",
    ),

    # Business & Analytics --------------------------------------------------

    "Business Analyst": _profile(
        BUSINESS_SKILLS,
        category="Business & Analytics",
    ),

    "Business Intelligence Analyst": _profile(
        ["SQL", "Data Analysis", "Data Visualization", "Business Intelligence", "Statistics", "Excel", "Business Analysis"],
        category="Business & Analytics",
    ),

    "Financial Analyst": _profile(
        FINANCE_SKILLS,
        category="Business & Analytics",
    ),

    "Operations Analyst": _profile(
        ["Operations Analysis", "Data Analysis", "Excel", "Statistics", "Process Improvement", "Business Analysis", "Problem Solving"],
        category="Business & Analytics",
    ),

    "Marketing Analyst": _profile(
        ["Marketing Analytics", "Data Analysis", "Statistics", "Market Research", "Excel", "SQL", "Digital Marketing"],
        category="Business & Analytics",
    ),

    "Management Consultant": _profile(
        ["Business Analysis", "Strategy", "Market Research", "Data Analysis", "Problem Solving", "Communication", "Presentation"],
        category="Business & Analytics",
    ),

    "Risk Analyst": _profile(
        ["Risk Analysis", "Statistics", "Financial Analysis", "Data Analysis", "Excel", "Risk Management", "Business Analysis"],
        category="Business & Analytics",
    ),

    # Finance ---------------------------------------------------------------

    "Financial Planner": _profile(
        ["Financial Planning", "Investment Analysis", "Accounting", "Taxation", "Risk Management", "Financial Modeling", "Communication"],
        category="Finance",
    ),

    "Investment Analyst": _profile(
        ["Investment Analysis", "Financial Modeling", "Financial Analysis", "Statistics", "Risk Management", "Excel", "Economics"],
        category="Finance",
    ),

    "Credit Analyst": _profile(
        ["Credit Analysis", "Financial Analysis", "Risk Management", "Accounting", "Excel", "Statistics", "Financial Modeling"],
        category="Finance",
    ),

    "Accountant": _profile(
        ["Accounting", "Financial Reporting", "Taxation", "Auditing", "Excel", "Financial Analysis", "Business Law"],
        category="Finance",
    ),

    "Auditor": _profile(
        ["Auditing", "Accounting", "Risk Management", "Financial Reporting", "Internal Controls", "Excel", "Compliance"],
        category="Finance",
    ),

    "FinTech Analyst": _profile(
        ["Financial Technology", "Financial Analysis", "Data Analysis", "SQL", "Python", "Risk Management", "Digital Payments"],
        category="Finance",
    ),

    # Marketing & Sales -----------------------------------------------------

    "Digital Marketing Specialist": _profile(
        ["Digital Marketing", "SEO", "Content Strategy", "Social Media", "Analytics", "Email Marketing", "Communication"],
        category="Marketing & Sales",
    ),

    "SEO Specialist": _profile(
        ["SEO", "Keyword Research", "Analytics", "Content Strategy", "Technical SEO", "Web", "Digital Marketing"],
        category="Marketing & Sales",
    ),

    "Content Strategist": _profile(
        ["Content Strategy", "Content Creation", "Market Research", "SEO", "Communication", "Analytics", "Brand Strategy"],
        category="Marketing & Sales",
    ),

    "Social Media Manager": _profile(
        ["Social Media", "Content Creation", "Digital Marketing", "Analytics", "Communication", "Brand Strategy", "Creative Thinking"],
        category="Marketing & Sales",
    ),

    "Growth Marketer": _profile(
        ["Growth Marketing", "Digital Marketing", "Analytics", "A/B Testing", "Product Analytics", "SEO", "Market Research"],
        category="Marketing & Sales",
    ),

    "Sales Engineer": _profile(
        ["Sales Engineering", "Technical Communication", "Product Knowledge", "APIs", "Problem Solving", "Presentation", "Sales"],
        category="Marketing & Sales",
    ),

    "Business Development Executive": _profile(
        ["Business Development", "Sales", "Communication", "Negotiation", "Market Research", "Lead Generation", "Presentation"],
        category="Marketing & Sales",
    ),

    "Account Executive": _profile(
        ["Sales", "Account Management", "Negotiation", "Communication", "CRM", "Presentation", "Business Development"],
        category="Marketing & Sales",
    ),

    # Human Resources -------------------------------------------------------

    "HR Analyst": _profile(
        HR_SKILLS,
        category="Human Resources",
    ),

    "HR Generalist": _profile(
        ["Human Resources", "Recruitment", "Employee Relations", "HR Operations", "Labor Law", "Communication", "Talent Management"],
        category="Human Resources",
    ),

    "Talent Acquisition Specialist": _profile(
        ["Recruitment", "Talent Sourcing", "Interviewing", "Communication", "Employer Branding", "Applicant Tracking", "Talent Management"],
        category="Human Resources",
    ),

    "Recruiter": _profile(
        ["Recruitment", "Talent Sourcing", "Interviewing", "Communication", "Candidate Screening", "Applicant Tracking", "Employer Branding"],
        category="Human Resources",
    ),

    "People Operations Specialist": _profile(
        ["People Operations", "Human Resources", "Employee Relations", "HR Analytics", "Communication", "Process Improvement", "Talent Management"],
        category="Human Resources",
    ),

    "Learning & Development Specialist": _profile(
        ["Learning & Development", "Training", "Communication", "Instructional Design", "People Analytics", "Talent Management", "Presentation"],
        category="Human Resources",
    ),

    # Engineering -----------------------------------------------------------

    "Mechanical Engineer": _profile(
        ["Engineering Mathematics", "Mechanical Design", "CAD", "Thermodynamics", "Materials Science", "Manufacturing", "Safety"],
        category="Engineering",
    ),

    "Electrical Engineer": _profile(
        ["Engineering Mathematics", "Circuit Analysis", "Electrical Systems", "Power Systems", "Control Systems", "Electronics", "Safety"],
        category="Engineering",
    ),

    "Electronics Engineer": _profile(
        ["Circuit Analysis", "Digital Electronics", "Analog Electronics", "Microcontrollers", "PCB Design", "Embedded Systems", "Signal Processing"],
        category="Engineering",
    ),

    "Civil Engineer": _profile(
        ["Structural Engineering", "Construction", "CAD", "Surveying", "Geotechnical Engineering", "Project Management", "Safety"],
        category="Engineering",
    ),

    "Chemical Engineer": _profile(
        ["Chemical Engineering", "Thermodynamics", "Fluid Mechanics", "Process Design", "Mass Transfer", "Process Control", "Safety"],
        category="Engineering",
    ),

    "Aerospace Engineer": _profile(
        ["Aerodynamics", "Aircraft Design", "Engineering Mathematics", "Flight Mechanics", "Propulsion", "Materials Science", "Control Systems"],
        category="Engineering",
    ),

    "Automotive Engineer": _profile(
        ["Automotive Engineering", "Vehicle Dynamics", "CAD", "Thermodynamics", "Manufacturing", "Control Systems", "Electronics"],
        category="Engineering",
    ),

    "Biomedical Engineer": _profile(
        ["Biomedical Engineering", "Biology", "Medical Devices", "Engineering Mathematics", "Signal Processing", "Data Analysis", "Safety"],
        category="Engineering",
    ),

    "Industrial Engineer": _profile(
        ["Industrial Engineering", "Operations Research", "Process Improvement", "Statistics", "Supply Chain", "Quality Management", "Engineering Mathematics"],
        category="Engineering",
    ),

    "Manufacturing Engineer": _profile(
        ["Manufacturing", "CAD", "Production Engineering", "Quality Management", "Process Improvement", "Materials Science", "Safety"],
        category="Engineering",
    ),

    "Control Systems Engineer": _profile(
        ["Control Systems", "Engineering Mathematics", "Signals & Systems", "Embedded Systems", "Electronics", "Programming", "Automation"],
        category="Engineering",
    ),

    "Mechatronics Engineer": _profile(
        ["Mechatronics", "Mechanical Design", "Electronics", "Control Systems", "Embedded Systems", "Robotics", "Programming"],
        category="Engineering",
    ),

    # Media & Creative ------------------------------------------------------

    "Technical Writer": _profile(
        ["Technical Writing", "Documentation", "Communication", "Research", "Editing", "Software Concepts", "Information Architecture"],
        category="Media & Creative",
    ),

    "Content Writer": _profile(
        ["Writing", "Content Creation", "Research", "SEO", "Editing", "Communication", "Creative Thinking"],
        category="Media & Creative",
    ),

    "Copywriter": _profile(
        ["Copywriting", "Content Strategy", "Marketing", "Writing", "Psychology", "Communication", "Creative Thinking"],
        category="Media & Creative",
    ),

    "Video Editor": _profile(
        ["Video Editing", "Visual Storytelling", "Motion Design", "Audio Editing", "Color Grading", "Digital Media", "Creative Thinking"],
        category="Media & Creative",
    ),

    "Content Creator": _profile(
        ["Content Creation", "Video Production", "Social Media", "Storytelling", "Digital Marketing", "Editing", "Creative Thinking"],
        category="Media & Creative",
    ),

    "Photographer": _profile(
        ["Photography", "Composition", "Lighting", "Image Editing", "Visual Storytelling", "Color Theory", "Creative Thinking"],
        category="Media & Creative",
    ),

    "Animator": _profile(
        ["Animation", "Character Design", "Motion Design", "Storytelling", "3D Modeling", "Visual Design", "Creative Thinking"],
        category="Media & Creative",
    ),

    "3D Artist": _profile(
        ["3D Modeling", "Texturing", "Lighting", "Rendering", "Animation", "Visual Design", "Creative Thinking"],
        category="Media & Creative",
    ),
}


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_career_skill_profile(career: str):
    """
    Return the detailed profile for a career.

    The original 10 ROLE_PROFILES are handled separately by the existing
    system. This function supplies profiles for the expanded catalog.
    """
    return CAREER_SKILL_PROFILES.get(career)


def get_all_skill_profiles():
    return CAREER_SKILL_PROFILES


def get_profile_skills(career: str):
    profile = get_career_skill_profile(career)
    if not profile:
        return []
    return list(profile["skills"].keys())


def get_profile_weights(career: str):
    profile = get_career_skill_profile(career)
    if not profile:
        return {}
    return profile["skills"]


def validate_catalog_coverage():
    """
    Verify that every career in the expandable catalog has intelligence.
    Existing 10 detailed roles are intentionally excluded because they live
    in ROLE_PROFILES.
    """
    catalog_careers = set(get_all_careers())
    covered = set(CAREER_SKILL_PROFILES.keys())

    # Existing detailed roles already have their authoritative profiles.
    from app.services.role_profiles import ROLE_PROFILES
    covered_total = covered | set(ROLE_PROFILES.keys())

    missing = sorted(catalog_careers - covered_total)
    extra = sorted(covered_total - catalog_careers)

    return {
        "catalog_total": len(catalog_careers),
        "covered_total": len(catalog_careers & covered_total),
        "missing": missing,
        "extra": extra,
        "complete": not missing,
    }
