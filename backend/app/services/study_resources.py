RESOURCE_MAP = {
    "Python": {
        "url": "https://docs.python.org/3/tutorial/",
        "title": "Python Official Tutorial",
    },
    "C": {
        "url": "https://en.cppreference.com/w/c/language",
        "title": "C Language Reference",
    },
    "DSA": {
        "url": "https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/",
        "title": "DSA Tutorial",
    },
    "SQL": {
        "url": "https://sqlbolt.com/",
        "title": "SQLBolt Interactive SQL Lessons",
    },
    "OOP": {
        "url": "https://www.geeksforgeeks.org/object-oriented-programming-oops-concept-in-java/",
        "title": "OOP Concepts",
    },
    "DBMS": {
        "url": "https://www.geeksforgeeks.org/dbms/dbms/",
        "title": "DBMS Tutorial",
    },
    "Aptitude": {
        "url": "https://www.indiabix.com/aptitude/questions-and-answers/",
        "title": "Aptitude Practice",
    },
}


def get_study_resource(skill: str, task: str = ""):
    resource = RESOURCE_MAP.get(skill)

    if not resource:
        return {
            "url": None,
            "title": None,
        }

    return resource