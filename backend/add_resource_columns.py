from sqlalchemy import text
from app.db.session import engine


def main():
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE tasks "
                "ADD COLUMN IF NOT EXISTS resource_title VARCHAR(200)"
            )
        )

        connection.execute(
            text(
                "ALTER TABLE tasks "
                "ADD COLUMN IF NOT EXISTS resource_url TEXT"
            )
        )

    print("Resource columns added successfully.")


if __name__ == "__main__":
    main()