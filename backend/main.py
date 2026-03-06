from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import re
from router import detect_mode
from llm_service import generate_response, extract_text_from_file, analyze_resume_domain
from auth_service import get_password_hash, verify_password, create_access_token
from supabase_client import supabase
from datetime import datetime
from assistants.interview_coach import analyze_resume_deep
from assistants.quiz_master import generate_dynamic_quiz, generate_quiz_feedback
from assistants.coding_mentor import analyze_code_deep
from services.pdf_generator import generate_roadmap_pdf
from services.career_pathfinder import generate_career_report
from services.teacher_service import explain_subtopic, generate_topic_notes_pdf, get_market_skills

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _sanitize_filename(filename: str) -> str:
    if not filename:
        return "resume.pdf"
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    return str(safe)[:180]


def _get_user_id_by_email(user_email: str) -> Optional[str]:
    if not user_email:
        return None
    user_result = supabase.table("users").select("id").eq("email", user_email).execute()
    if not user_result.data:
        return None
    return user_result.data[0]["id"]


def _store_resume_for_user(contents: bytes, original_filename: str, user_email: Optional[str]) -> Optional[str]:
    user_id = _get_user_id_by_email(user_email) if user_email else None
    if not user_id:
        return None

    timestamp = int(datetime.now().timestamp())
    safe_name = _sanitize_filename(original_filename)
    storage_path = f"users/{user_id}/{timestamp}_{safe_name}"
    supabase.storage.from_("resumes").upload(storage_path, contents)
    return storage_path


def _get_latest_resume_path_for_user(user_email: str) -> Optional[str]:
    user_id = _get_user_id_by_email(user_email)
    if not user_id:
        return None

    folder = f"users/{user_id}"
    try:
        files = supabase.storage.from_("resumes").list(folder)
    except Exception as e:
        print(f"Resume list error: {e}")
        return None

    if not files:
        return None

    latest_name = None
    latest_ts = -1
    for item in files:
        name = item.get("name")
        if not name:
            continue
        m = re.match(r"^(\d+)_", name)
        ts = int(m.group(1)) if m else 0
        if ts > latest_ts:
            latest_ts = ts
            latest_name = name

    if not latest_name:
        return None
    return f"{folder}/{latest_name}"


def _load_resume_text(file: Optional[UploadFile], user_email: Optional[str]):
    # Returns (text, source_path, error)
    if file is not None:
        contents = file.file.read()
        text = extract_text_from_file(contents, file.filename)
        if not text:
            return None, None, "Text extraction failed. Please upload a readable PDF/DOCX/Image resume."

        source_path = None
        if user_email:
            try:
                source_path = _store_resume_for_user(contents, file.filename, user_email)
            except Exception as e:
                print(f"Supabase storage upload error: {e}")

        return text, source_path, None

    if not user_email:
        return None, None, "Please upload a resume first, or sign in to use your stored resume."

    latest_path = _get_latest_resume_path_for_user(user_email)
    if not latest_path:
        return None, None, "No stored resume found. Please upload your resume once."

    try:
        contents = supabase.storage.from_("resumes").download(latest_path)
        filename = latest_path.split("/")[-1]
        text = extract_text_from_file(contents, filename)
        if not text:
            return None, latest_path, "Stored resume found but text extraction failed. Upload a clearer resume."
        return text, latest_path, None
    except Exception as e:
        print(f"Supabase resume download error: {e}")
        return None, latest_path, "Failed to fetch stored resume from Supabase."

@app.get("/health")
def health():
    return {"status": "ok", "message": "Edunovas Backend is Alive"}

class UserAuth(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "student"

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: str
    full_name: Optional[str] = None

class StudentProfileSchema(BaseModel):
    degree: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[str] = None
    domain: Optional[str] = None
    skills: List[str] = []

class ChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "ROUTER"
    profile: Optional[StudentProfileSchema] = None
    user_email: Optional[str] = None

class QuizSubmission(BaseModel):
    user_email: str
    topic: str
    score: int
    weak_areas: List[str]

class QuizFeedbackRequest(BaseModel):
    results: List[dict]
    subject: str
    topic: str

@app.post("/signup", response_model=Token)
def signup(user_data: UserAuth):
    existing = supabase.table('users').select('*').eq('email', user_data.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = supabase.table('users').insert({
        'email': user_data.email,
        'full_name': user_data.full_name or user_data.email,
        'password_hash': get_password_hash(user_data.password),
        'role': user_data.role
    }).execute()
    
    user = new_user.data[0]
    access_token = create_access_token(data={"sub": user['email'], "role": user['role']})
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user['role'], 
        "email": user['email'],
        "full_name": user.get('full_name') or user['email']
    }

@app.post("/login", response_model=Token)
def login(user_data: UserAuth):
    result = supabase.table('users').select('*').eq('email', user_data.email).execute()
    if not result.data or not verify_password(user_data.password, result.data[0]['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = result.data[0]
    access_token = create_access_token(data={"sub": user['email'], "role": user['role']})
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user['role'], 
        "email": user['email'],
        "full_name": user.get('full_name') or user['email']
    }

@app.post("/chat")
def chat(req: ChatRequest):
    if req.mode == "ROUTER":
        mode = detect_mode(req.message)
    else:
        mode = req.mode
    profile_dict = None
    if req.profile:
        profile_dict = req.profile.dict()
    reply = generate_response(req.message, mode, profile_dict)
    return {"mode": mode, "response": reply}

@app.post("/save-profile")
def save_profile(profile: StudentProfileSchema, user_email: str):
    user_result = supabase.table('users').select('id').eq('email', user_email).execute()
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user_result.data[0]['id']
    existing = supabase.table('student_profiles').select('*').eq('user_id', user_id).execute()
    
    profile_data = {
        'user_id': user_id,
        'degree': profile.degree,
        'branch': profile.branch,
        'academic_year': profile.year,
        'domain': profile.domain,
        'skills': profile.skills
    }
    
    try:
        if existing.data:
            res = supabase.table('student_profiles').update(profile_data).eq('user_id', user_id).execute()
        else:
            res = supabase.table('student_profiles').insert(profile_data).execute()
        
        # Also ensure user progress exists
        supabase.table('user_progress').select('id').eq('user_id', user_id).execute()
        
        return {"success": True}
    except Exception as e:
        print(f"Profile Save Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/student/profile")
def get_user_profile(user_email: str):
    user_result = supabase.table('users').select('id').eq('email', user_email).execute()
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user_result.data[0]['id']
    profile_result = supabase.table('student_profiles').select('*').eq('user_id', user_id).execute()
    
    # Also check resume status
    resume_status = get_resume_status(user_email)
    
    profile = profile_result.data[0] if profile_result.data else None
    return {
        "profile": profile,
        "has_stored_resume": resume_status.get("has_stored_resume", False)
    }

@app.get("/student/progress")
def get_progress(user_email: str):
    user_result = supabase.table('users').select('id').eq('email', user_email).execute()
    if not user_result.data:
        raise HTTPException(status_code=404)
    
    user_id = user_result.data[0]['id']
    prog_result = supabase.table('user_progress').select('*').eq('user_id', user_id).execute()
    
    if not prog_result.data:
        try:
            new_prog = supabase.table('user_progress').insert({
                'user_id': user_id,
                'points': 0,
                'level': 1,
                'streak_days': 0,
                'badges': [],
                'career_phase': 'Foundational'
            }).execute()
            prog = new_prog.data[0] if new_prog.data else {
                'id': user_id, 'points': 0, 'level': 1, 'streak_days': 0,
                'badges': [], 'career_phase': 'Foundational', 'last_active': None
            }
        except Exception as e:
            print(f"Progress Init Error: {e}")
            prog = {
                'id': user_id, 'points': 0, 'level': 1, 'streak_days': 0,
                'badges': [], 'career_phase': 'Foundational', 'last_active': None
            }
    else:
        prog = prog_result.data[0]
    
    profile_result = supabase.table('student_profiles').select('*').eq('user_id', user_id).execute()
    
    return {
        "id": str(prog.get('id', user_id)),
        "points": prog.get('points', 0),
        "level": prog.get('level', 1),
        "streak_days": prog.get('streak_days', 0),
        "badges": prog.get('badges', []),
        "career_phase": prog.get('career_phase', 'Foundational'),
        "last_active": prog.get('last_active'),
        "profile_completed": len(profile_result.data) > 0
    }

# ─────────────────────────────────────────────────────────────────
# Performance Tracking: Pydantic models
# ─────────────────────────────────────────────────────────────────

class TeacherProgressModel(BaseModel):
    user_email: str
    domain: str
    roadmap_id: str
    phase_name: str
    phase_index: int
    milestone_title: str
    milestone_index: int
    status: str = 'done'   # 'learning' | 'done'

class InterviewSessionModel(BaseModel):
    user_email: str
    role: str
    domain: str
    level: str
    readiness_score: int
    extracted_skills: List[str] = []
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    market_skills: List[str] = []
    strong_domains: List[str] = []

@app.post("/save-teacher-progress")
def save_teacher_progress(data: TeacherProgressModel):
    """Upsert a student's subtopic progress into Supabase."""
    user_result = supabase.table('users').select('id').eq('email', data.user_email).execute()
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user_result.data[0]['id']

    from datetime import timezone
    now = datetime.now(timezone.utc).isoformat()
    record = {
        'user_id': user_id,
        'domain': data.domain,
        'roadmap_id': data.roadmap_id,
        'phase_name': data.phase_name,
        'phase_index': data.phase_index,
        'milestone_title': data.milestone_title,
        'milestone_index': data.milestone_index,
        'status': data.status,
        'completed_at': now if data.status == 'done' else None,
        'updated_at': now
    }
    try:
        supabase.table('teacher_progress').upsert(
            record,
            on_conflict='user_id,roadmap_id,phase_index,milestone_index'
        ).execute()
        # Award XP: +15 per topic done
        if data.status == 'done':
            supabase.table('user_progress').update({'points': supabase.table('user_progress').select('points').eq('user_id', user_id).execute().data[0].get('points', 0) + 15}).eq('user_id', user_id).execute()
        return {"success": True}
    except Exception as e:
        print(f"Teacher progress save error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/save-interview-session")
def save_interview_session(data: InterviewSessionModel):
    """Save a student's interview coach session results to Supabase."""
    user_result = supabase.table('users').select('id').eq('email', data.user_email).execute()
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user_result.data[0]['id']

    record = {
        'user_id': user_id,
        'role': data.role,
        'domain': data.domain,
        'level': data.level,
        'readiness_score': data.readiness_score,
        'extracted_skills': data.extracted_skills,
        'matched_skills': data.matched_skills,
        'missing_skills': data.missing_skills,
        'market_skills': data.market_skills,
        'strong_domains': data.strong_domains
    }
    try:
        supabase.table('interview_sessions').insert(record).execute()
        return {"success": True}
    except Exception as e:
        print(f"Interview session save error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/admin/analytics")
def get_analytics():
    """Aggregated analytics for admin dashboard."""
    users = supabase.table('users').select('id, email, full_name, created_at').eq('role', 'student').execute()
    profiles = supabase.table('student_profiles').select('skills, domain').execute()
    progress = supabase.table('user_progress').select('points').execute()

    # Skills from profiles
    skill_counts: dict = {}
    for p in profiles.data:
        if p.get('skills'):
            for skill in p['skills']:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    total_xp = sum(p.get('points', 0) for p in progress.data)

    # Domain distribution from teacher_progress (how many topics done per domain)
    try:
        tp = supabase.table('teacher_progress').select('domain').eq('status', 'done').execute()
        domain_dist: dict = {}
        for row in tp.data:
            d = row.get('domain', 'Other')
            domain_dist[d] = domain_dist.get(d, 0) + 1
    except Exception:
        domain_dist = {}

    # Total teacher topics completed
    try:
        total_topics_done = supabase.table('teacher_progress').select('id', count='exact').eq('status', 'done').execute()
        topics_completed = total_topics_done.count or 0
    except Exception:
        topics_completed = 0

    # Total interview sessions
    try:
        interview_rows = supabase.table('interview_sessions').select('readiness_score').execute()
        total_interviews = len(interview_rows.data)
        avg_readiness = round(sum(r.get('readiness_score', 0) for r in interview_rows.data) / total_interviews, 1) if total_interviews else 0
    except Exception:
        total_interviews = 0
        avg_readiness = 0

    return {
        "total_students": len(users.data),
        "active_today": 0,
        "total_xp": total_xp,
        "total_interaction_hits": topics_completed,
        "total_interviews": total_interviews,
        "avg_readiness_score": avg_readiness,
        "domain_distribution": domain_dist,
        "top_skills": [{"name": k, "count": v} for k, v in top_skills]
    }

@app.get("/admin/student-performance")
def get_student_performance():
    """Per-student breakdown for admin: topics completed, interview scores, domains."""
    try:
        users = supabase.table('users').select('id, email, full_name, created_at').eq('role', 'student').execute()
        result = []
        for user in users.data:
            uid = user['id']

            # Teacher progress
            tp = supabase.table('teacher_progress').select('domain, roadmap_id, milestone_title, status, completed_at').eq('user_id', uid).execute()
            done_topics = [r for r in tp.data if r.get('status') == 'done']
            domains_studied = list(set(r['domain'] for r in tp.data if r.get('domain')))

            # Interview sessions
            iv = supabase.table('interview_sessions').select('role, domain, level, readiness_score, session_date').eq('user_id', uid).order('session_date', desc=True).limit(5).execute()

            # XP
            prog = supabase.table('user_progress').select('points, level').eq('user_id', uid).execute()
            xp = prog.data[0].get('points', 0) if prog.data else 0
            level = prog.data[0].get('level', 1) if prog.data else 1

            result.append({
                "user_id": uid,
                "email": user.get('email'),
                "full_name": user.get('full_name', user.get('email')),
                "joined": user.get('created_at'),
                "xp": xp,
                "level": level,
                "topics_completed": len(done_topics),
                "total_topics_attempted": len(tp.data),
                "domains_studied": domains_studied,
                "last_topic": done_topics[-1]['milestone_title'] if done_topics else None,
                "interview_sessions": len(iv.data),
                "latest_readiness": iv.data[0]['readiness_score'] if iv.data else None,
                "avg_readiness": round(sum(s['readiness_score'] for s in iv.data) / len(iv.data), 1) if iv.data else None,
                "last_interview_role": iv.data[0]['role'] if iv.data else None,
            })
        return {"students": result}
    except Exception as e:
        print(f"Student performance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), user_email: Optional[str] = Form(None)):
    contents = file.file.read()

    text = extract_text_from_file(contents, file.filename)
    if not text:
        return {"error": "Text extraction failed. Supported formats: PDF, DOCX, IMG."}

    storage_path = None
    if user_email:
        try:
            storage_path = _store_resume_for_user(contents, file.filename, user_email)
            print(f"Resume saved to storage: {storage_path}")
        except Exception as e:
            print(f"Supabase Storage Error: {e}")

    analysis = analyze_resume_domain(text)
    return {"success": True, "analysis": analysis, "stored_path": storage_path}


@app.get("/resume-status")
def get_resume_status(user_email: str):
    latest_path = _get_latest_resume_path_for_user(user_email)
    return {
        "has_stored_resume": bool(latest_path),
        "stored_path": latest_path
    }


@app.post("/analyze-resume")
async def analyze_resume_endpoint(
    role: str = Form(...),
    level: str = Form(...),
    user_email: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    text, source_path, error = _load_resume_text(file, user_email)
    if error:
        return {"error": error}
    analysis = analyze_resume_deep(text, role, level)
    analysis["source_resume_path"] = source_path
    return analysis


@app.post("/career-pathfinder")
async def career_pathfinder_endpoint(
    role: str = Form(...),
    level: str = Form(...),
    city: str = Form(...),
    user_email: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    text, source_path, error = _load_resume_text(file, user_email)
    if error:
        return {"error": error}
    report = generate_career_report(text, role, level, city)
    report["source_resume_path"] = source_path
    return report

@app.get("/generate-quiz")
def get_quiz_endpoint(subject: str, topic: str, difficulty: str, domain: Optional[str] = None, subtopic: Optional[str] = None):
    from assistants.quiz_master import generate_dynamic_quiz
    return generate_dynamic_quiz(subject, topic, difficulty, domain, subtopic)

@app.post("/submit-quiz")
def submit_quiz_endpoint(data: QuizSubmission):
    user_result = supabase.table('users').select('id').eq('email', data.user_email).execute()
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user_result.data[0]['id']
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    
    try:
        # Save to teacher_progress or a separate quiz_performance table if it exists
        # For now, let's update user_progress points
        points_earned = 10 + (data.score // 10) # Base 10 + 1 per 10% score
        
        current_progress = supabase.table('user_progress').select('points').eq('user_id', user_id).execute()
        if current_progress.data:
            new_points = current_progress.data[0].get('points', 0) + points_earned
            supabase.table('user_progress').update({'points': new_points}).eq('user_id', user_id).execute()
        
        # Persistence: Log the detailed quiz attempt for real-time stats
        supabase.table('quiz_sessions').insert({
            'user_id': user_id,
            'domain': data.domain,
            'subject': data.subject,
            'topic': data.topic,
            'score': data.score,
            'weak_areas': data.weak_areas,
            'created_at': now
        }).execute()
        
        return {"success": True, "score": data.score, "points_earned": points_earned}
    except Exception as e:
        print(f"Quiz submission error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/quiz-feedback")
def get_quiz_feedback(data: QuizFeedbackRequest):
    return generate_quiz_feedback(data.results, data.subject, data.topic)

@app.post("/analyze-code")
def analyze_code_endpoint(code: str = Form(...), language: str = Form("python")):
    return analyze_code_deep(code, language)

@app.get("/performance-stats")
def get_performance_stats(user_email: str):
    """Fetch real-time student performance metrics from Supabase."""
    try:
        user_res = supabase.table('users').select('id').eq('email', user_email).execute()
        if not user_res.data:
            return {"quiz_accuracy": 0, "interview_score": 0, "code_optimization": 80, "accuracy_trend": [0], "domain_strength": {}}
        
        user_id = user_res.data[0]['id']

        # 1. Quiz Performance
        quizzes = supabase.table('quiz_sessions').select('score, created_at').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
        quiz_accuracy = round(sum(q['score'] for q in quizzes.data) / len(quizzes.data)) if quizzes.data else 0
        accuracy_trend = [q['score'] for q in reversed(quizzes.data)] if quizzes.data else [0]

        # 2. Interview Score
        interviews = supabase.table('interview_sessions').select('readiness_score').eq('user_id', user_id).order('session_date', desc=True).limit(1).execute()
        interview_score = interviews.data[0]['readiness_score'] if interviews.data else 0

        # 3. Code Optimization
        coding = supabase.table('coding_sessions').select('optimization_score').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
        code_optimization = round(sum(c['optimization_score'] for c in coding.data) / len(coding.data)) if coding.data else 80

        # 4. Domain Strength (Based on teacher progress + quiz domains)
        progress = supabase.table('teacher_progress').select('domain').eq('user_id', user_id).eq('status', 'done').execute()
        domain_counts = {}
        for p in progress.data:
            d = p.get('domain', 'General')
            domain_counts[d] = domain_counts.get(d, 0) + 1
        
        # Normalize domain strength (placeholder logic)
        total_topics = len(progress.data) or 1
        domain_strength = {d: round((c / total_topics) * 100) for d, c in domain_counts.items()}
        if not domain_strength: domain_strength = {"General": 0}

        return {
            "quiz_accuracy": quiz_accuracy,
            "interview_score": interview_score,
            "code_optimization": code_optimization,
            "accuracy_trend": accuracy_trend,
            "domain_strength": domain_strength
        }
    except Exception as e:
        print(f"Stats Error: {e}")
        return {"quiz_accuracy": 0, "interview_score": 0, "code_optimization": 0, "accuracy_trend": [0], "domain_strength": {}}

@app.post("/download-roadmap-pdf")
def download_roadmap_pdf(roadmap_data: dict):
    pdf_buffer = generate_roadmap_pdf(roadmap_data)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={roadmap_data['title'].replace(' ', '_')}_Roadmap.pdf"}
    )

# ─────────────────────────────────────────────────────────────────
# Teacher AI endpoints
# ─────────────────────────────────────────────────────────────────

class TeacherExplainRequest(BaseModel):
    topic: str
    subtopic: str
    domain: str
    has_doubt: bool = False
    doubt_text: Optional[str] = None
    user_email: Optional[str] = None  # Used to persist notes to Supabase Storage

class MarketSkillsRequest(BaseModel):
    role: str
    domain: str

@app.post("/teacher/market-skills")
def teacher_market_skills(req: MarketSkillsRequest):
    """Return what skills the market demands for the given role/domain via Groq."""
    result = get_market_skills(req.role, req.domain)
    return result

@app.post("/teacher/explain")
def teacher_explain(req: TeacherExplainRequest):
    """Groq-powered subtopic explanation. If has_doubt, answer the specific doubt."""
    result = explain_subtopic(req.topic, req.subtopic, req.domain, req.has_doubt, req.doubt_text)
    return result

@app.post("/teacher/generate-notes")
def teacher_generate_notes(req: TeacherExplainRequest):
    """Generate professional PDF notes, save to Supabase Storage, and stream for download."""
    import time, io
    pdf_buffer = generate_topic_notes_pdf(req.topic, req.subtopic, req.domain)
    safe_name = str(re.sub(r"[^A-Za-z0-9_-]", "_", req.subtopic))[:60]
    filename = f"{safe_name}_Notes.pdf"

    # --- Persist to Supabase Storage if user is logged in ---
    storage_path = None
    if req.user_email:
        try:
            user_result = supabase.table('users').select('id').eq('email', req.user_email).execute()
            if user_result.data:
                user_id = user_result.data[0]['id']
                ts = int(time.time())
                storage_path = f"notes/{user_id}/{ts}_{filename}"
                pdf_bytes = pdf_buffer.read()
                pdf_buffer.seek(0)   # reset for streaming
                supabase.storage.from_("student-notes").upload(
                    path=storage_path,
                    file=pdf_bytes,
                    file_options={"content-type": "application/pdf", "upsert": "true"}
                )
                # Also record the note path in teacher_progress metadata
                supabase.table('teacher_progress').update({
                    'notes_path': storage_path
                }).eq('user_id', user_id).eq('domain', req.domain).eq('milestone_title', req.subtopic).execute()
                print(f"Notes saved to storage: {storage_path}")
        except Exception as e:
            print(f"Notes storage upload error: {e}")
            pdf_buffer.seek(0)  # ensure buffer is reset even on error

    # Stream to browser for immediate download
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Storage-Path": storage_path or ""
        }
    )

@app.get("/student/notes")
def list_student_notes(user_email: str):
    """List all PDF notes saved in Supabase Storage for a student."""
    try:
        user_result = supabase.table('users').select('id').eq('email', user_email).execute()
        if not user_result.data:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user_result.data[0]['id']
        folder = f"notes/{user_id}"

        files = supabase.storage.from_("student-notes").list(folder)
        notes = []
        for f in (files or []):
            name = f.get("name", "")
            if not name:
                continue
            path = f"{folder}/{name}"
            # Generate a signed URL valid for 1 hour
            try:
                signed = supabase.storage.from_("student-notes").create_signed_url(path, 3600)
                url = signed.get("signedURL") or signed.get("signed_url") or ""
            except Exception:
                url = ""
            # Parse display name from filename: remove timestamp prefix and _Notes.pdf suffix
            display = re.sub(r"^\d+_", "", name).replace("_Notes.pdf", "").replace("_", " ")
            notes.append({
                "name": name,
                "display_name": display,
                "path": path,
                "signed_url": url,
                "created_at": f.get("created_at") or f.get("updated_at") or ""
            })
        # Sort newest first
        notes.sort(key=lambda x: x["name"], reverse=True)
        return {"notes": notes, "count": len(notes)}
    except HTTPException:
        raise
    except Exception as e:
        print(f"List notes error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


    print("Pre-Uvicorn Run...")
    import uvicorn
    print("Starting Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

