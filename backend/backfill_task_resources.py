from app.db.session import SessionLocal
from app.models.study_plan import Task
from app.services.study_resources import get_study_resource


def main():
    db = SessionLocal()

    try:
        tasks = db.query(Task).all()

        updated = 0

        for task in tasks:
            resource = get_study_resource(
                skill=task.skill,
                task=task.task
            )

            if resource["url"]:
                task.resource_title = resource["title"]
                task.resource_url = resource["url"]
                updated += 1

        db.commit()

        print(f"Updated {updated} tasks with study resources.")

    finally:
        db.close()


if __name__ == "__main__":
    main()