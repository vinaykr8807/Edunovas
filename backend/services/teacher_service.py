import os
import io
import json
from groq import Groq
from dotenv import load_dotenv
from services.pexels_service import get_pexels_image, get_pexels_video
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _strip_md(text: str) -> str:
    """Remove markdown formatting tokens so ReportLab doesn't render them as raw text."""
    import re
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)   # **bold** -> bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)        # *italic* -> italic
    text = re.sub(r'`([^`]+)`', r'\1', text)          # `code` -> code
    text = re.sub(r'^#+\s*', '', text, flags=re.M)    # ## Heading -> Heading
    return text.strip()


def _parse_groq_json(raw: str) -> dict:
    """Robustly extract JSON from a Groq response that may have markdown fences."""
    import re
    # Strip leading/trailing whitespace
    raw = raw.strip()
    # Remove ```json ... ``` or ``` ... ``` fences
    raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.S)
    raw = re.sub(r'\s*```$', '', raw, flags=re.S)
    # Sometimes Groq wraps the JSON in a sentence; try to find the first { ... }
    match = re.search(r'\{.*\}', raw, re.S)
    if match:
        raw = match.group(0)
    return json.loads(raw)


def get_market_skills(role: str, domain: str) -> dict:
    """Ask Groq what skills the market currently demands for a given role/domain, enriched by live research."""
    from services.market_research import get_market_trends
    
    # Live scrape current signals
    search_query = f"top in-demand technical skills for {role} {domain} 2026 hiring trends india global"
    market_raw = get_market_trends(search_query)

    prompt = f"""You are a Lead Tech Recruiter and Market Intelligence Analyst.
Based on these current market signals:
{market_raw}

For the role: "{role}" in domain: "{domain}", provide a structured JSON response for a student:
- required_skills: list of 10-12 must-have technical skills
- nice_to_have_skills: list of 5-8 bonus/emerging skills
- top_tools: list of 5-6 specific tools/frameworks
- avg_salary_india: salary range in INR (LPA)
- demand_level: "Very High" | "High" | "Moderate" | "Low"
- growth_trend: A 2-sentence expert outlook on this role's future.
- trend_analytics: A list of objects for a chart: [ {{"skill": "SkillName", "demand_score": 0-100}}, ... ] (top 6 skills)

Return ONLY valid JSON."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        return _parse_groq_json(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"Market Skills Data Error: {e}")
        return {
            "required_skills": ["Technical Skill 1", "Technical Skill 2"],
            "nice_to_have_skills": ["Emerging Tech 1"],
            "top_tools": ["Industry Tool 1"],
            "avg_salary_india": "6-15 LPA",
            "demand_level": "High",
            "growth_trend": "Market is evolving with focus on AI integration.",
            "trend_analytics": [{"skill": "Python", "demand_score": 90}, {"skill": "Cloud", "demand_score": 85}],
            "error": str(e)
        }

def get_pro_coach_beginner_guide(role: str, domain: str) -> dict:
    """Generates a professional 'Zero-to-Hero' coaching guide for absolute beginners."""
    prompt = f"""You are a Senior Career Mentor. A student with ZERO knowledge wants to become a successful {role} in {domain}.
Generate a professional, encouraging, and comprehensive 'Zero-to-Hero' Blueprint.
Include:
1. Executive Summary (The professional path)
2. Week 1-4: The Foundation (What to learn first, exactly)
3. Month 2-3: Building Competency
4. Essential Soft Skills for {role}s
5. Industry Trends they must watch.

Return JSON:
{{
  "guide_title": "string",
  "summary": "markdown",
  "phases": [ {{"phase": "Phase Name", "focus": "markdown details"}} ],
  "soft_skills": ["skill1", "skill2"],
  "trends": ["trend1", "trend2"]
}}
"""
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return _parse_groq_json(res.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}


def explain_subtopic(topic: str, subtopic: str, domain: str,
                     has_doubt: bool = False, doubt_text: str = None,
                     history: list = None) -> dict:
    """Generate a Groq-powered explanation for a subtopic with RAG and chat memory."""
    from services.rag_service import generate_rag_context
    
    rag_context = generate_rag_context(topic, subtopic, domain)
    context_injection = ""
    if rag_context:
        context_injection = f"\n\nHere is some real-time extracted context from the web to help you:\n{rag_context}\n\nUse this context to provide an extremely detailed, context-aware explanation.\n"

    if has_doubt and doubt_text:
        system_prompt = f"""You are an expert {domain} tutor. A student is studying "{subtopic}" under "{topic}".
{context_injection}
Provide a clear, conversational, and technical answer to their doubt.
Use the conversation history for context to provide a continuous learning experience.
Maintain a helpful and direct tone.

Return a JSON object:
{{
  "explanation": "Markdown response with clear formatting..."
}}
"""
    else:
        system_prompt = f"""You are a master {domain} tutor and industry expert teaching "{subtopic}" (part of "{topic}").
{context_injection}
Provide an extremely deep, master-level explanation of this topic.
Your explanation MUST follow this exact structure and style:

# 🏛️ Core Architecture & Mastery: {subtopic}

## 📌 Beginner Intuition
(Explain like I'm five. What is the real-world analogy? Why does this exist?)

## ⚙️ Deep-Dive Mechanics
(Explain the underlying logic, architecture, and "how it works" in high detail.)

## 💻 Technical Implementation
(Provide clean, professional code examples or syntactical logic.)

## 🚀 Advanced System Design & Edge Cases
(Where does it break? How do experts use it at scale?)

## 🗺️ Visual System Flowchart
(MANDATORY: Provide a D2 diagram code block starting with ` ```d2 ` to visualize the architecture.
Use this syntax:
Backend {{ Auth -> DB }}
User -> API: Request
Cloud: {{ shape: cloud }}
Each statement on a new line.)

## ⚠️ Expert Pitfalls & Optimization
(What are the 3 things beginners get wrong?)

Also, provide TWO search queries for image/video.
IMPORTANT: For `visual_query`, Pexels (a stock photo site) is used. Do NOT use abstract academic or anatomical terms like "distributed systems core". Instead, use broad, simple technology photography terms (e.g. "server room", "cloud computing", "data center", "programmer typing", "software code"). Keep it 1-2 words.

Return a JSON object:
{{
  "explanation": "FULL markdown content following the structure above...",
  "visual_query": "broad tech stock photo keyword",
  "video_query": "specific instructional video query"
}}
"""

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for msg in history:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    
    if has_doubt and doubt_text:
        messages.append({"role": "user", "content": doubt_text})
    else:
        # Standard lesson request
        messages.append({"role": "user", "content": f"Explain {subtopic} in {topic}."})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content.strip())
        explanation = data.get("explanation", "")

        # Fetch visuals using AI-generated specific queries
        image_url = get_pexels_image(data.get("visual_query") or "technology computer")
        video_url = get_pexels_video(data.get("video_query") or f"tutorial {subtopic}")

        return {
            "explanation": explanation,
            "topic": topic,
            "subtopic": subtopic,
            "domain": domain,
            "image_url": image_url,
            "video_url": video_url
        }
    except Exception as e:
        return {
            "explanation": f"Sorry, could not generate explanation: {str(e)}",
            "topic": topic,
            "subtopic": subtopic,
            "domain": domain
        }


def generate_topic_notes_pdf(topic: str, subtopic: str, domain: str) -> io.BytesIO:
    """Generate professional PDF notes for a subtopic using Groq content + ReportLab, enhanced by RAG."""
    from services.rag_service import generate_rag_context
    rag_context = generate_rag_context(topic, subtopic, domain)
    context_injection = ""
    if rag_context:
        context_injection = f"\n\nHere is some real-time extracted context from the web to help you:\n{rag_context}\n\nUse this context to accurately enrich the generated notes, scaling from fundamental definitions to advanced applications.\n"

    # 1. Get content from Groq
    prompt = f"""You are an expert technical educator creating professional study notes for "{subtopic}" ({topic} — {domain}).
{context_injection}
Generate structured notes with these sections in JSON:
{{
  "summary": "2-3 sentence overview of the subtopic",
  "beginner_intuition": "Simple analogy and overview...",
  "mechanics": "Deep dive into how it works...",
  "advanced_design": "System design and scaling...",
  "d2_code": "D2 diagram code here...",
  "key_concepts": ["concept 1", "concept 2", "concept 3", "concept 4", "concept 5"],
  "table_data": [
    {{"term": "Term 1", "definition": "Definition 1", "example": "Example 1"}}
  ],
  "code_example": "Code snippet...",
  "common_mistakes": ["mistake 1", "mistake 2"],
  "practice_tasks": ["task 1", "task 2"]
}}

Return ONLY valid JSON and include the D2 code for a visual architecture."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3500,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content.strip()
        data = _parse_groq_json(raw)
    except Exception as e:
        print(f"pdf generation groq error: {e}")
        try:
            print(f"raw output was: {raw[:500]}...")
        except:
            pass
        data = {
            "summary": f"FALLBACK TRIGGERED! Exception details: {str(e)}",
            "key_concepts": ["Core concept 1", "Core concept 2", "Core concept 3"],
            "table_data": [{"term": "Key Term", "definition": "Definition", "example": "Example"}],
            "code_example": "",
            "common_mistakes": ["Common mistake 1", "Common mistake 2"],
            "practice_tasks": ["Practice task 1", "Practice task 2"]
        }

    # 2. Build PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    GREEN = colors.HexColor('#2d7d46')
    LIGHT_GREEN = colors.HexColor('#e8f5e9')
    DARK = colors.HexColor('#1a2e1f')

    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  textColor=GREEN, fontSize=22, spaceAfter=4)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'],
                                     textColor=colors.HexColor('#4a7c59'), fontSize=11,
                                     spaceAfter=12)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'],
                                    textColor=GREEN, fontSize=13, spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                 fontSize=10, leading=16, textColor=DARK)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
                                   fontSize=10, leading=15, textColor=DARK,
                                   leftIndent=15, bulletIndent=5)
    code_style = ParagraphStyle('Code', parent=styles['Code'],
                                 fontSize=9, leading=14,
                                 backColor=colors.HexColor('#f0f7f2'),
                                 borderColor=GREEN, borderWidth=1,
                                 borderPadding=8, leftIndent=10)

    story = []

    # Header
    story.append(Paragraph(_strip_md(subtopic), title_style))
    story.append(Paragraph(f"{_strip_md(topic)} · {domain} · Edunovas AI Notes", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=14))

    # Summary
    story.append(Paragraph("📌 Overview", section_style))
    story.append(Paragraph(_strip_md(data.get("summary", "")), body_style))
    story.append(Spacer(1, 10))

    # Add Pexels Image to PDF
    try:
        from services.pexels_service import get_pexels_image
        import requests
        from io import BytesIO
        img_url = get_pexels_image(f"technical {subtopic}")
        if img_url:
            resp = requests.get(img_url, timeout=5)
            if resp.ok:
                img_data = BytesIO(resp.content)
                story.append(Image(img_data, width=16*cm, height=8*cm))
                story.append(Spacer(1, 10))
    except:
        pass

    # Detailed Sections
    if data.get("beginner_intuition"):
        story.append(Paragraph("🧠 Beginner Intuition", section_style))
        story.append(Paragraph(_strip_md(data.get("beginner_intuition")), body_style))
        story.append(Spacer(1, 10))

    if data.get("mechanics"):
        story.append(Paragraph("⚙️ Technical Mechanics", section_style))
        story.append(Paragraph(_strip_md(data.get("mechanics")), body_style))
        story.append(Spacer(1, 10))

    # Flowchart Rendering (Kroki)
    d2_code = data.get("d2_code")
    if d2_code and isinstance(d2_code, str):
        try:
            import requests
            from io import BytesIO
            story.append(Paragraph("📊 Architecture Flowchart", section_style))
            res = requests.post("https://kroki.io/d2/png", data=d2_code.encode(), timeout=5)
            if res.ok:
                diag_data = BytesIO(res.content)
                story.append(Image(diag_data, width=16*cm, height=10*cm))
                story.append(Spacer(1, 10))
        except:
            pass

    # Key Concepts
    story.append(Paragraph("🔑 Key Concepts", section_style))
    for concept in data.get("key_concepts", []):
        if isinstance(concept, str):
            story.append(Paragraph(f"• {_strip_md(concept)}", bullet_style))
    story.append(Spacer(1, 10))

    # Table
    table_data = data.get("table_data", [])
    if table_data and isinstance(table_data, list) and isinstance(table_data[0], dict):
        story.append(Paragraph("📊 Quick Reference Table", section_style))
        t_rows = [["Term", "Definition", "Example"]]
        for row in table_data:
            if isinstance(row, dict):
                t_rows.append([
                    Paragraph(_strip_md(str(row.get("term", ""))), body_style),
                    Paragraph(_strip_md(str(row.get("definition", ""))), body_style),
                    Paragraph(_strip_md(str(row.get("example", ""))), body_style),
                ])
        t = Table(t_rows, colWidths=[3.5*cm, 8*cm, 5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), GREEN),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GREEN]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#b2dfdb')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))

    # Code example
    code = data.get("code_example", "")
    if isinstance(code, str):
        code = code.strip()
    if code:
        story.append(Paragraph("💻 Code / Pseudocode Example", section_style))
        # Strip markdown code fences from code example itself
        import re as _re
        import html
        code = _re.sub(r'^```\w*\s*', '', code)
        code = _re.sub(r'\s*```$', '', code)
        code_escaped = html.escape(code).replace('\n', '<br/>').replace(' ', '&nbsp;')
        story.append(Paragraph(code_escaped, code_style))
        story.append(Spacer(1, 10))

    # Common Mistakes
    story.append(Paragraph("⚠️ Common Mistakes to Avoid", section_style))
    for mistake in data.get("common_mistakes", []):
        if isinstance(mistake, str):
            story.append(Paragraph(f"✗  {_strip_md(mistake)}", bullet_style))
    story.append(Spacer(1, 10))

    # Practice Tasks
    story.append(Paragraph("✅ Practice Tasks", section_style))
    for i, task in enumerate(data.get("practice_tasks", []), 1):
        if isinstance(task, str):
            story.append(Paragraph(f"{i}. {_strip_md(task)}", bullet_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=GREEN))
    story.append(Paragraph("Generated by Edunovas AI · For educational use only",
                             ParagraphStyle('Footer', parent=styles['Normal'],
                                            fontSize=8, textColor=colors.grey,
                                            alignment=TA_CENTER, spaceBefore=6)))

    doc.build(story)
    buffer.seek(0)
    return buffer
