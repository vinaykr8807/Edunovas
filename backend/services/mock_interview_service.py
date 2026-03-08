import os
import json
from groq import Groq
from services.career_pathfinder import _search_ddg_jobs

# Use simple search instead of complex scraping for speed and reliability, but simulate web context
def get_most_asked_questions(role, domain):
    try:
        # Just use DDG to get some context
        query = f"most asked interview questions for {role} {domain} github"
        results = _search_ddg_jobs(query, max_results=2)
        context = " ".join([r.get("snippet", "") for r in results])
        return context
    except:
        return ""

def llm_json_mock(prompt, temperature=0.3):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return None
    client = Groq(api_key=api_key)
    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(r.choices[0].message.content)
    except Exception as e:
        print(f"Mock LLM Error: {e}")
        return None

def build_mock_plan(role, domain, extracted_skills):
    skills = extracted_skills[:3] if extracted_skills else [domain]
    if len(skills) < 3: skills += ["Problem Solving", "System Architecture"]
    
    return [
        {"type": "fundamental", "skill": skills[0]},
        {"type": "technical", "skill": skills[1]},
        {"type": "scenario", "skill": skills[2]},
        {"type": "behavioral", "skill": "Leadership/Teamwork"}
    ]

def generate_mock_question(role, domain, plan_item, asked, difficulty):
    web_context = get_most_asked_questions(role, domain)
    
    prompt = f"""
    You are a friendly, encouraging interviewer hiring a Junior/Entry-level {role} in {domain}.
    
    Current Interview Step:
    Type: {plan_item['type']}
    Core Skill Focus: {plan_item['skill']}
    Difficulty Level: {difficulty}
    
    Recently Searched Market Context (use basic concepts from this):
    {web_context[:1000]}
    
    Previously Asked Questions (DO NOT REPEAT):
    {json.dumps(asked)}
    
    Task:
    Generate a highly realistic but APPROACHABLE interview question for a Junior/Entry-Level candidate.
    
    RULES:
    - If the step is 'fundamental', ask for basic terminology, what a specific concept means, or the difference between two simple concepts.
    - If the step is 'technical', ask them about a small project they might have built using {plan_item['skill']}, to explain its use-case, and how they approached building it.
    - If the step is 'scenario', ask a very simple, everyday problem (e.g. how to find a bug, or how to explain a technical concept to a non-technical person).
    - UNDER NO CIRCUMSTANCES should you ask complex FAANG-style system design, advanced algorithms, or deep architecture questions. 
    - Keep it practical and closely related to basic resume skills.
    
    Return pure JSON:
    {{
        "question": "The actual question text",
        "category": "The question category",
        "expected_key_points": ["point 1", "point 2"]
    }}
    """
    res = llm_json_mock(prompt, 0.4)
    if res and "question" in res:
        return res
    return {
        "question": f"Explain a challenging problem you solved related to {plan_item['skill']} and how you approached it.",
        "category": plan_item['type'],
        "expected_key_points": ["Clear explanation", "Challenge faced", "Resolution"]
    }

def evaluate_mock_answer(question, answer, role, domain):
    prompt = f"""
    Evaluate this Junior/Entry-Level candidate's interview answer for a {role} position.
    
    Question: {question}
    Candidate Answer: {answer}
    
    This is an entry-level candidate, so judge them warmly and fairly. Focus heavily on whether they grasp the core concept, their logic, or their passion for the project mentioned. If they explain the basic idea in their own words, give them a good score.
    
    Provide a strict JSON evaluation:
    {{
        "overall_score": <1-10>,
        "technical_accuracy": <1-10>,
        "communication": <1-10>,
        "strengths": "Brief summary of strengths",
        "weaknesses": "Brief summary of weaknesses (be constructive and gentle)",
        "improved_answer": "How a good junior {role} would answer this simply and clearly",
        "advice": "Actionable, simple advice"
    }}
    """
    res = llm_json_mock(prompt, 0.2)
    if res:
        return res
    return {
        "overall_score": 5, "technical_accuracy": 5, "communication": 5,
        "strengths": "Provided an answer.",
        "weaknesses": "Answer lacked depth and structure.",
        "improved_answer": "Use the STAR method to structure your technical examples clearly.",
        "advice": "Practice articulating your technical decisions out loud."
    }
