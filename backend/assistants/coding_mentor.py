import os
from groq import Groq
import json

def analyze_code_deep(code: str, language: str = "python"):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"bugs": [], "explanation": "API Key missing", "fix": "", "optimized": "", "mistakes": [], "optimization_score": 0}

    client = Groq(api_key=api_key)
    prompt = f"""
    You are Coding Mentor AI. Analyze this {language} code.
    
    Code:
    {code}
    
    TASK:
    1. Detect bugs or logic errors.
    2. Suggest a fix.
    3. Provide an optimized version.
    4. List common mistakes found here.

    Return ONLY a JSON object:
    {{
        "bugs": ["bug1"],
        "explanation": "string",
        "fix": "corrected copy",
        "optimized": "better copy",
        "mistakes": ["repeated pattern X"],
        "optimization_score": 85
    }}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            stream=False
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Code Analysis Error: {e}")
        return {
            "bugs": [],
            "explanation": f"Cloud analysis failed: {str(e)}",
            "fix": "",
            "optimized": "",
            "mistakes": [],
            "optimization_score": 0
        }
