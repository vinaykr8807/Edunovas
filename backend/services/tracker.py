from sqlalchemy.orm import Session
from database import QuizHistory, InterviewHistory, CodingError, ProgressTracking
from datetime import datetime

def track_quiz(user_id: str, topic: str, score: int, weak_areas: list, db: Session):
    record = QuizHistory(
        user_id=user_id,
        topic=topic,
        score=score,
        weak_areas=weak_areas
    )
    db.add(record)
    
    # Update general progress tracking
    prog = db.query(ProgressTracking).filter(ProgressTracking.user_id == user_id, ProgressTracking.topic == topic).first()
    if not prog:
        prog = ProgressTracking(user_id=user_id, topic=topic, confidence_score=score / 100.0)
        db.add(prog)
    else:
        from datetime import timezone
        prog.confidence_score = (prog.confidence_score + (score / 100.0)) / 2
        prog.times_attempted += 1
        prog.last_practiced = datetime.now(timezone.utc)
        
    db.commit()

def track_interview(user_id: str, role: str, score: int, weak_topics: list, feedback: str, db: Session):
    record = InterviewHistory(
        user_id=user_id,
        role=role,
        score=score,
        weak_topics=weak_topics,
        feedback=feedback
    )
    db.add(record)
    db.commit()

def track_coding_mistake(user_id: str, language: str, mistake_type: str, db: Session):
    err = db.query(CodingError).filter(
        CodingError.user_id == user_id, 
        CodingError.language == language, 
        CodingError.mistake_type == mistake_type
    ).first()
    
    if err:
        err.frequency += 1
    else:
        err = CodingError(user_id=user_id, language=language, mistake_type=mistake_type)
        db.add(err)
    
    db.commit()
