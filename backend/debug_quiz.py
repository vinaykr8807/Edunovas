import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def debug_quiz_generation(subject="Computer Science", topic="Data Structures", difficulty="Medium"):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Error: GROQ_API_KEY not found.")
        return

    print(f"📡 Debugging Quiz for: {subject} - {topic} ({difficulty})")
    client = Groq(api_key=api_key)
    
    prompt = f"""
    You are Quiz Master AI. Generate a technical quiz on {subject} - {topic} at {difficulty} difficulty level.
    Requirements:
    - Exactly 5 Questions
    - Mix of MCQs and conceptual logic
    - Include correct answer and a brief explanation for each.
    CRITICAL: Return ONLY a JSON object with a "quiz" key containing the list of questions.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            stream=False
        )
        
        raw_content = chat_completion.choices[0].message.content
        print(f"📥 Raw response from Groq:\n{raw_content}")
        
        data = json.loads(raw_content)
        print(f"✅ JSON Parsed Successfully.")
        
        if "quiz" in data:
            print(f"✅ Found 'quiz' key with {len(data['quiz'])} questions.")
        else:
            print(f"❌ 'quiz' key NOT found in: {list(data.keys())}")
            
    except Exception as e:
        print(f"❌ Error during debug: {str(e)}")

if __name__ == "__main__":
    debug_quiz_generation()
