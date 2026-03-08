import streamlit as st
import json
import os
import tempfile
import matplotlib.pyplot as plt
import numpy as np
from pypdf import PdfReader
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
import streamlit.components.v1 as components

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found in .env file")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(
    page_title="AI Interview Simulator Pro",
    layout="wide",
    page_icon="🤖",
)

def safe_json(text):
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == -1:
            return None
        return json.loads(text[start:end])
    except Exception:
        return None

def llm(prompt, temperature=0.3):
    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Groq API Error: {e}")
        return None

def llm_json(prompt, temperature=0.3):
    out = llm(prompt, temperature)
    if not out:
        return None
    parsed = safe_json(out)
    if parsed:
        return parsed
    repair_prompt = f"""
Convert the following into STRICT valid JSON.
Return ONLY JSON.

Content:
{out}
"""
    out2 = llm(repair_prompt, temperature=0)
    if not out2:
        return None
    return safe_json(out2)

def speech_to_text(audio_file):
    try:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            response_format="json",
            temperature=0.0,
        )
        return transcription.text
    except Exception as e:
        st.error(f"Voice transcription error: {e}")
        return ""

def speak_text_browser(text):
    js = f"""
    <script>
    const msg = new SpeechSynthesisUtterance({json.dumps(text)});
    msg.lang = 'en-US';
    window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js)

def extract_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for p in reader.pages:
            t = p.extract_text()
            if t:
                text += t + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"PDF reading error: {e}")
        return ""

def analyze_resume(text):
    prompt = f"""
You are a senior resume intelligence system.

Return STRICT JSON.

{{
 "primary_skills": [],
 "secondary_skills": [],
 "projects": [],
 "experience_level": "",
 "domains": [],
 "seniority": ""
}}

Resume:
{text[:6000]}
"""
    data = llm_json(prompt, 0.2)
    if data:
        return data
    return {
        "primary_skills": [],
        "secondary_skills": [],
        "projects": [],
        "experience_level": "Unknown",
        "domains": [],
        "seniority": "Unknown",
    }

def ats_score_resume(text):
    prompt = f"""
You are an ATS resume scanner.

Return STRICT JSON:
{{
 "ats_score": 0,
 "keyword_match": "",
 "format_issues": "",
 "missing_skills": "",
 "improvements": ""
}}

Resume:
{text[:6000]}
"""
    return llm_json(prompt, 0.2)

def build_plan(data):
    skills = data.get("primary_skills", [])[:3]
    if not skills:
        skills = ["python", "data analysis", "problem solving"]
    return [
        {"type": "resume", "skill": skills[0]},
        {"type": "technical", "skill": skills[0]},
        {"type": "coding", "skill": skills[0]},
        {"type": "scenario", "skill": skills[min(1, len(skills)-1)]},
        {"type": "behavioral", "skill": None},
        {"type": "final", "skill": None},
    ]

def generate_question(plan_item, resume_data, asked, difficulty):
    prompt = f"""
You are a strict FAANG interviewer.

Candidate resume summary:
{json.dumps(resume_data, indent=2)}

Interview step:
type = {plan_item['type']}
focus_skill = {plan_item['skill']}
difficulty = {difficulty}

Rules:
- Must be unique
- Must not repeat
- Must be specific to resume
- If type is coding, ask a real coding problem
- Avoid generic questions
- Avoid these previous questions: {asked}

Return STRICT JSON:
{{
 "question": "",
 "category": ""
}}
"""
    for _ in range(3):
        q = llm_json(prompt, 0.5)
        if isinstance(q, dict) and q.get("question"):
            return q
    skill = plan_item.get("skill") or "your main expertise"
    return {
        "question": f"Based on your experience with {skill}, explain a complex problem you solved.",
        "category": plan_item.get("type", "technical"),
    }

def evaluate(question, answer):
    prompt = f"""
You are a senior technical interviewer.

Question: {question}
Answer: {answer}

Return STRICT JSON:
{{
 "overall_score": 0,
 "technical_accuracy": 0,
 "depth": 0,
 "communication": 0,
 "strengths": "",
 "weaknesses": "",
 "improved_answer": "",
 "advice": ""
}}
"""
    ev = llm_json(prompt, 0.3)
    if ev:
        return ev
    return {
        "overall_score": 5,
        "technical_accuracy": 5,
        "depth": 5,
        "communication": 5,
        "strengths": "Needs improvement",
        "weaknesses": "Answer lacked clarity",
        "improved_answer": "Provide structured technical explanation",
        "advice": "Use STAR method and quantify impact",
    }

def next_diff(score):
    if score >= 8:
        return "Hard"
    if score >= 5:
        return "Medium"
    return "Easy"

def radar_chart(evals):
    if not evals:
        return
    tech = np.mean([e["technical_accuracy"] for e in evals])
    depth = np.mean([e["depth"] for e in evals])
    comm = np.mean([e["communication"] for e in evals])
    overall = np.mean([e["overall_score"] for e in evals])
    labels = ["Technical", "Depth", "Communication", "Overall"]
    values = [tech, depth, comm, overall]
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 10)
    st.pyplot(fig)

if "stage" not in st.session_state:
    st.session_state.stage = "upload"
    st.session_state.resume_data = None
    st.session_state.plan = []
    st.session_state.q_index = 0
    st.session_state.questions = []
    st.session_state.evals = []
    st.session_state.difficulty = "Medium"
    st.session_state.ats = None
    st.session_state.spoken_q = -1

st.title("🤖 AI Interview Simulator Pro")
st.caption("Resume → Intelligence → Real Interview")

if st.session_state.stage == "upload":
    f = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
    if f and st.button("🚀 Start AI Interview"):
        with st.spinner("🔍 Analyzing resume deeply..."):
            txt = extract_text(f)
            data = analyze_resume(txt)
            ats = ats_score_resume(txt)
            plan = build_plan(data)
        st.session_state.resume_data = data
        st.session_state.plan = plan
        st.session_state.ats = ats
        st.session_state.stage = "interview"
        st.rerun()

elif st.session_state.stage == "interview":
    idx = st.session_state.q_index
    plan = st.session_state.plan
    if idx >= len(plan):
        st.session_state.stage = "report"
        st.rerun()

    if len(st.session_state.questions) <= idx:
        qobj = generate_question(
            plan[idx],
            st.session_state.resume_data,
            st.session_state.questions,
            st.session_state.difficulty,
        )
        st.session_state.questions.append(qobj["question"])

    question = st.session_state.questions[idx]
    current_type = plan[idx]["type"]

    st.progress(idx / len(plan))
    st.subheader(f"🧠 Question {idx + 1}")
    st.info(question)

    if st.session_state.spoken_q != idx:
        speak_text_browser(question)
        st.session_state.spoken_q = idx

    if current_type != "coding":
        st.markdown("### ✍️ Type or Speak Your Answer")
        st.markdown("### 🎙️ Record Live Answer")
        audio_data = mic_recorder(
            start_prompt="🎤 Start Recording",
            stop_prompt="⏹️ Stop Recording",
            key=f"mic_{idx}"
        )

        if audio_data and audio_data.get("bytes"):
            if st.button("🧠 Transcribe Recording", key=f"transcribe_live_{idx}"):
                with st.spinner("Transcribing your voice..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp.write(audio_data["bytes"])
                        tmp_path = tmp.name
                    with open(tmp_path, "rb") as f:
                        text_from_voice = speech_to_text(f)
                    if text_from_voice:
                        st.session_state[f"a_{idx}"] = text_from_voice
                        st.success("✅ Voice converted to text!")

    ans = st.text_area(
        "Your Answer",
        value=st.session_state.get(f"a_{idx}", ""),
        height=260 if current_type=="coding" else 150,
        key=f"a_{idx}"
    )

    if st.button("Submit Answer"):
        if not ans.strip():
            st.warning("⚠️ Please write an answer.")
        else:
            with st.spinner("🤖 AI evaluating your response..."):
                ev = evaluate(question, ans)
            st.session_state.evals.append(ev)
            st.session_state.q_index += 1
            st.session_state.difficulty = next_diff(ev["overall_score"])
            st.rerun()

elif st.session_state.stage == "report":
    st.header("📊 Interview Intelligence Report")

    if st.session_state.ats:
        ats = st.session_state.ats
        st.subheader("📄 ATS Resume Score")
        st.metric("ATS Score", f"{ats.get('ats_score', 0)}/100")
        st.write("**Keyword Match:**", ats.get("keyword_match", ""))
        st.write("**Format Issues:**", ats.get("format_issues", ""))
        st.write("**Missing Skills:**", ats.get("missing_skills", ""))
        st.info("💡 Improvements: " + ats.get("improvements", ""))

    scores = [e["overall_score"] for e in st.session_state.evals]
    avg = sum(scores) / len(scores)
    st.metric("Overall Interview Score", f"{avg:.1f}/10")

    st.subheader("📈 Performance Radar")
    radar_chart(st.session_state.evals)

    for i, ev in enumerate(st.session_state.evals):
        with st.expander(f"Question {i+1} Analysis"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Overall", ev["overall_score"])
            c2.metric("Technical", ev["technical_accuracy"])
            c3.metric("Depth", ev["depth"])
            c4.metric("Communication", ev["communication"])
            st.write("**Strengths:**", ev["strengths"])
            st.write("**Weaknesses:**", ev["weaknesses"])
            st.success(ev["improved_answer"])
            st.info("💡 AI Advice: " + ev["advice"])

    if st.button("🔄 Start New Interview"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()