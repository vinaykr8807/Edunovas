def detect_mode(user_message: str):
    msg = user_message.lower()

    if "error" in msg or "code" in msg or "bug" in msg:
        return "coding"

    if "interview" in msg:
        return "interview"

    if "quiz" in msg or "test" in msg:
        return "quiz"

    if "career" in msg or "job" in msg:
        return "career"

    if "tired" in msg or "stuck" in msg or "demotivated" in msg:
        return "motivation"

    return "default"
