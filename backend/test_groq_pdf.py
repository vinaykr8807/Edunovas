import os
from dotenv import load_dotenv
load_dotenv()
from services.teacher_service import generate_topic_notes_pdf

try:
    print("Testing Groq PDF Generation...")
    buf = generate_topic_notes_pdf("Data Structures", "Linked Lists", "Computer Science")
    print(f"Success! Buffer size: {buf.getbuffer().nbytes}")
except Exception as e:
    print(f"Exception: {e}")
