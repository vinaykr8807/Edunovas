import os
import json
from typing import Optional
from groq import Groq
import requests

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def get_image(query, page=1):
    if not PEXELS_API_KEY:
        return None
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 1, "page": page}
    try:
        r = requests.get(url, headers=headers, params=params)
        data = r.json()
        if data.get("photos"):
            return data["photos"][0]["src"]["large"]
    except:
        pass
    return None

def generate_dynamic_quiz(subject: str, topic: str, difficulty: str, mode: str = "standard", domain: Optional[str] = None, subtopic: Optional[str] = None):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return []
        
    client = Groq(api_key=api_key)
    
    context_str = f"in {domain}" if domain else ""
    subtopic_str = f"specifically on {subtopic}" if subtopic else ""
    
    # Mode-specific prompt additions - Integrated into a single unified flow
    instruction = "Generate a 10-question mixed-mode technical assessment. Include a mix of: 1. Standard conceptual MCQs, 2. Subtle True/False technical nuances, 3. 'Match the Following' permutations, 4. Code Completion logic (____), and 5. Image-Based analysis (provide a 'visual_query'). Ensure the difficulty scales from basic to advanced."

    prompt = f"""
    You are an expert technical interviewer and educator. 
    Create a {difficulty} level technical quiz for a student learning {subject} {context_str}.
    The quiz should be {subtopic_str} (under the broader topic of {topic}).
    
    QUIZ MODE: UNIFIED ADAPTIVE ASSESSMENT
    Instruction: {instruction}
    
    Rules:
    - Generate 10 questions.
    - Format: JSON object with "quiz" key containing a list.
    - Each question must have: 
        "question": string (conceptual prompt),
        "options": list of 4 strings (REQUIRED for 'mcq', 'true_false', 'code_completion', and 'image_based'),
        "answer": string (exactly matches one option),
        "explanation": string,
        "topic_tag": string,
        "type": string ('mcq', 'true_false', 'matching', 'code_completion', 'image_based'),
        "matching_pairs": JSON object with key-value pairs (ONLY if type is 'matching'),
        "visual_query": string (if relevant)
    
    For 'matching' type:
    - Set "question" to "Match the following terms correctly."
    - Provide "matching_pairs" (e.g., {{"React": "Frontend Framework", "Node": "Backend Runtime"}}).
    - Set "answer" to a string representing the correct full mapping for internal grading logic, but the UI will handle the actual interaction.
    
    Return ONLY a valid JSON object.
    If the mode is 'visual' or 'image_based', provide a 'visual_query' string in each question object for Pexels image search (e.g. "server room", "code screen", "data center"). DO NOT use abstract or academic terms like "distributed system core" as it fetches biological/anatomical images. Keep the keyword broad and 1-2 words.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.6,
            max_tokens=3000
        )
        
        raw_content = chat_completion.choices[0].message.content
        data = json.loads(raw_content)
        
        questions = []
        for key in ["quiz", "questions", "data", "questions_list"]:
            if key in data and isinstance(data[key], list):
                questions = data[key]
                break
        
        if not questions:
            for val in data.values():
                if isinstance(val, list) and len(val) > 0:
                    questions = val
                    break
        
        if not questions and isinstance(data, list):
            questions = data

        # Process Visuals
        for q in questions:
            if "visual_query" in q:
                q["image_url"] = get_image(q["visual_query"])
            elif mode in ["visual", "image_based"]:
                q["image_url"] = get_image(f"{subject} {topic} {q.get('topic_tag', '')}")
                
        return questions
    except Exception as e:
        print(f"Quiz Generation Error: {e}")
        return []

def generate_quiz_feedback(results: list, subject: str, topic: str):
    """
    Generates personalized mentorship advice based on quiz performance.
    'results' is a list of {question, topic_tag, is_correct, explanation}
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return {"gaps": ["General practice needed"], "plan": ["Review foundational concepts"]}
    
    client = Groq(api_key=api_key)
    prompt = f"""
    Analyze these {subject} ({topic}) quiz results for a student.
    RESULTS: {json.dumps(results)}
    
    Provide a critical and deep technical analysis:
    1. "gaps": A list of specific concepts the student failed to understand. DO NOT leave this empty if there are incorrect answers. For every "is_correct": false, identify the specific concept gap.
    2. "plan": A list of 3 concrete, actionable, and technical steps to improve.
    3. "knowledge_graph": A list of 4 objects for visual analytics. Adjust "level" (0-1) and "status" based on whether related questions were correct.
       [
         {"id": "1", "label": "Theory", "level": float, "status": "done"|"learning"|"struggling"},
         {"id": "2", "label": "Logic", "level": float, "status": "done"|"learning"|"struggling"},
         {"id": "3", "label": "Systems", "level": float, "status": "done"|"learning"|"struggling"},
         {"id": "4", "label": "Implementation", "level": float, "status": "done"|"learning"|"struggling"}
       ]
    
    Return ONLY a JSON object with "gaps", "plan", and "knowledge_graph".
    If the student has mistakes, ensure the gaps reflect the technical depth of the error.
    """
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "You are a critical technical mentor. Never provide generic feedback. Always analyze specific mistakes."}, {"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        data = json.loads(res.choices[0].message.content)
        # Final safety check
        if not data.get("gaps") and any(not r.get("is_correct") for r in results):
             data["gaps"] = ["Conceptual architectural foundational gaps identified from incorrect responses."]
        return data
    except Exception as e:
        print(f"Feedback AI Error: {e}")
        return {"gaps": ["Error analyzing gaps"], "plan": ["Review foundational concepts"]}

def evaluate_student_explanation(topic: str, explanation: str, subject: str):
    """
    Evaluates 'Teach the AI' mode where the student explains a concept.
    Returns score, clarity rating, and missing points.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return {"score": 0, "feedback": "API Error"}
    
    client = Groq(api_key=api_key)
    prompt = f"""
    You are an expert tutor in {subject}. A student is trying to explain the concept of "{topic}" to you.
    STUDENT EXPLANATION:
    "{explanation}"
    
    Evaluate this explanation for:
    1. Technical Accuracy (0-10)
    2. Clarity & Communication (0-10)
    3. Missing Key Concepts (Identify what they forgot to mention)
    
    Format JSON:
    {{
        "accuracy_score": integer,
        "clarity_score": integer,
        "missing_concepts": list of strings,
        "mentor_feedback": string (brief, constructive),
        "overall_rating": string (e.g. "Excellent", "Developing", "Needs Review")
    }}
    """
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        res_data = json.loads(res.choices[0].message.content)
        
        # Add a visual aid
        res_data["visual_aid"] = get_image(f"technical {topic}")
        
        return res_data
    except Exception as e:
        return {"accuracy_score": 0, "mentor_feedback": f"Evaluation failed: {str(e)}"}
