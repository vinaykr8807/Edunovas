from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import UserProgress, Achievement

POINTS_MAP = {
    "quiz_complete": 50,
    "interview_complete": 100,
    "code_analysis": 25,
    "daily_streak": 10,
    "profile_update": 20
}

def reward_user(user_id: str, activity: str, db: Session):
    prog = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
    if not prog:
        prog = UserProgress(user_id=user_id)
        db.add(prog)
    
    points = POINTS_MAP.get(activity, 10)
    prog.points += points
    
    # Streak Logic
    from datetime import timezone
    now = datetime.now(timezone.utc)
    if prog.last_active:
        # DB may return naive or aware, force comparison
        last = prog.last_active
        if last.tzinfo is None:
            from datetime import timedelta
            last = last.replace(tzinfo=timezone.utc)
        
        diff = now - last
        if diff.days == 1:
            prog.streak_days += 1
            prog.points += POINTS_MAP["daily_streak"]
        elif diff.days > 1:
            prog.streak_days = 1
    else:
        prog.streak_days = 1
        
    prog.last_active = now
    
    # Level Up logic (roughly every 500 points)
    new_level = (prog.points // 500) + 1
    if new_level > prog.level:
        prog.level = new_level
        # Add Achievement
        achievement = Achievement(
            user_id=user_id,
            title=f"Reached Level {new_level}",
            description=f"Congratulations! You've climbed to level {new_level}."
        )
        db.add(achievement)
    
    # Badge logic
    if prog.points >= 1000 and "Master" not in prog.badges:
        prog.badges = prog.badges + ["Master"]
        prog.career_phase = "Advanced"
        
    db.commit()
    return {"points_added": points, "total_points": prog.points, "streak": prog.streak_days}
