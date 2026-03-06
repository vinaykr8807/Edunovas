import os
import json
from typing import Optional
from groq import Groq

def generate_dynamic_quiz(subject: str, topic: str, difficulty: str, domain: Optional[str] = None, subtopic: Optional[str] = None):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return []
        
    client = Groq(api_key=api_key)
    
    # Enrich prompt with curriculum context
    context_str = f"in {domain}" if domain else ""
    subtopic_str = f"specifically on {subtopic}" if subtopic else ""
    
    prompt = f"""
    You are an expert technical interviewer and educator. 
    Create a {difficulty} level technical quiz for a student learning {subject} {context_str}.
    The quiz should be {subtopic_str} (under the broader topic of {topic}).
    
    Rules:
    - Generate 5 high-quality multiple-choice questions.
    - Focus on conceptual understanding, common pitfalls, and practical implementation.
    - Format: JSON object with "quiz" key containing a list of objects.
    - Each question must have: 
        "question": string,
        "options": list of 4 strings,
        "answer": string (must exactly match one of the options),
        "explanation": string (explain why the answer is correct and why others might be tricky),
        "topic_tag": string (e.g. "React Hooks", "Memory Management")
    
    Return ONLY a valid JSON object.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=2000
        )
        
        raw_content = chat_completion.choices[0].message.content
        data = json.loads(raw_content)
        
        # Look for the list in common keys
        for key in ["quiz", "questions", "data", "questions_list"]:
            if key in data and isinstance(data[key], list):
                return data[key]
        
        # Fallback for any list
        for val in data.values():
            if isinstance(val, list) and len(val) > 0:
                return val
                
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Quiz Generation Error: {e}")
        return []

def generate_quiz_feedback(results: list, subject: str, topic: str):
    """
    Generates personalized mentorship advice based on quiz performance.
    'results' is a list of {question, topic_tag, is_correct, explanation}
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "Keep practicing!"
    
    client = Groq(api_key=api_key)
    prompt = f"""
    Analyze these {subject} ({topic}) quiz results for a student.
    RESULTS: {json.dumps(results)}
    
    Provide:
    1. "Gaps Identified": Bullet points of technical concepts missed.
    2. "Improvement Plan": 2-3 actionable steps to master this topic.
    Keep it encouraging but technical. Return ONLY a JSON object with "gaps" and "plan".
    """
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content)
    except:
        return {"gaps": ["General practice needed"], "plan": ["Review foundational concepts"]}
