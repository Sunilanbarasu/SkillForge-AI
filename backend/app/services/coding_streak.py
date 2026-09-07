from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.coding_streak import CodingStreak


def record_successful_completion(db: Session, user_id: int, completed_date: date):
    streak = (
        db.query(CodingStreak)
        .filter(CodingStreak.user_id == user_id)
        .first()
    )

    if streak is None:
        streak = CodingStreak(
            user_id=user_id,
            current_streak=1,
            best_streak=1,
            last_completed_date=completed_date,
            total_completed=1,
        )
        db.add(streak)
        db.commit()
        db.refresh(streak)
        return streak

    # Do not count the same daily challenge twice.
    if streak.last_completed_date == completed_date:
        return streak

    if streak.last_completed_date == completed_date - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.best_streak = max(streak.best_streak, streak.current_streak)
    streak.total_completed += 1
    streak.last_completed_date = completed_date

    db.commit()
    db.refresh(streak)

    return streak
