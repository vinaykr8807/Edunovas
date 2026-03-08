import os
import io
import json
from groq import Groq
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
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
    """Ask Groq what skills the market currently demands for a given role/domain."""
    prompt = f"""You are a tech hiring market analyst for India and global markets (2024-2025).
For the role: "{role}" in domain: "{domain}", provide a structured JSON response with:
- required_skills: list of 10-15 must-have technical skills demanded in job postings today
- nice_to_have_skills: list of 5-8 bonus/emerging skills
- top_tools: list of 5-6 specific tools/frameworks hiring managers look for
- avg_salary_india: estimated salary range in INR (LPA format)
- demand_level: "Very High" / "High" / "Moderate" / "Low"
- growth_trend: short sentence about job market trend

Return ONLY valid JSON, no markdown, no explanation."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        raw = response.choices[0].message.content.strip()
        return _parse_groq_json(raw)
    except Exception as e:
        return {
            "required_skills": ["Python", "JavaScript", "SQL", "Git", "REST APIs"],
            "nice_to_have_skills": ["Docker", "Cloud", "CI/CD"],
            "top_tools": ["VS Code", "GitHub", "Postman"],
            "avg_salary_india": "6-18 LPA",
            "demand_level": "High",
            "growth_trend": f"Strong demand for {role} professionals in 2025.",
            "error": str(e)
        }


def explain_subtopic(topic: str, subtopic: str, domain: str,
                     has_doubt: bool = False, doubt_text: str = None) -> dict:
    """Generate a Groq-powered explanation for a subtopic with RAG from DuckDuckGo and Mermaid support."""
    from services.rag_service import generate_rag_context
    
    rag_context = generate_rag_context(topic, subtopic, domain)
    context_injection = ""
    if rag_context:
        context_injection = f"\n\nHere is some real-time extracted context from the web to help you:\n{rag_context}\n\nUse this context to provide an extremely detailed, context-aware explanation that scales from beginner to advanced.\n"

    if has_doubt and doubt_text:
        prompt = f"""You are an expert {domain} tutor. A student is studying "{subtopic}" under "{topic}".
They have this specific doubt: "{doubt_text}"
{context_injection}
Provide a clear, structured response with:
1. Direct answer to their doubt
2. A concrete example
3. Common misconception to avoid
4. 1-2 follow-up study tips

Format in clear sections with headers. Be concise, practical, and encouraging."""
    else:
        prompt = f"""You are a master {domain} tutor and highly experienced industry expert teaching "{subtopic}" (part of "{topic}").
{context_injection}
Provide an extremely deep, master-level explanation of this topic. Structure your response dynamically based on what best suits the topic, but ensure it scales from beginner-friendly intuition (so a novice can understand) to advanced, expert-level edge cases and real-world system design.

Use professional formatting with clear markdown headers. Your response should naturally adapt to the specific nature of this subtopic, but could broadly hit these points:
## 📌 Beginner Intuition & Core Concept
(What is it in simple terms? Why was it invented?)

## ⚙️ How it Works Under the Hood
(The detailed mechanics, math, or logic behind it)

## 💻 Technical Syntax & Practical Examples
(Code snippets, configuration setups, or formulas)

## 🗺️ Visual Architecture
(Provide a D2 diagram code block starting with ` ```d2 ` to visualize the architecture, flow, or system design. 
D2 is much more powerful than Mermaid. Use this syntax:
1. Connections: `User -> API: request`
2. Containers: `Backend {{ label: "Server Side"; Auth -> Database }}`
3. Shapes: `Cloud: {{ shape: cloud }}`
4. Styling: Use simple labels and clear connections. Each statement MUST be on its own line.)

## 🚀 Advanced Use Cases & System Design
(Where is this used in large-scale modern systems? What are its limits/edge cases?)

## ⚠️ Common Pitfalls & Best Practices
(What do experts know that beginners do not?)

Be authoritative, precise, and highly engaging. adapt the flow to deeply explain this specific topic while scaling from beginner concepts to advanced applications."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3000
        )
        explanation = response.choices[0].message.content.strip()

        return {
            "explanation": explanation,
            "topic": topic,
            "subtopic": subtopic,
            "domain": domain
        }

        return {
            "explanation": explanation,
            "topic": topic,
            "subtopic": subtopic,
            "domain": domain
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
  "key_concepts": ["concept 1", "concept 2", "concept 3", "concept 4", "concept 5"],
  "table_data": [
    {{"term": "Term 1", "definition": "Definition 1", "example": "Example 1"}},
    {{"term": "Term 2", "definition": "Definition 2", "example": "Example 2"}},
    {{"term": "Term 3", "definition": "Definition 3", "example": "Example 3"}}
  ],
  "code_example": "Short code snippet or pseudocode showing the concept (if applicable, else empty string)",
  "common_mistakes": ["mistake 1", "mistake 2", "mistake 3"],
  "practice_tasks": ["task 1", "task 2", "task 3"]
}}

Return ONLY valid JSON."""

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
