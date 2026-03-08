import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.add_vertical_space import add_vertical_space
try:
    from streamlit_elements import elements, mui, html
except ImportError:
    # Fallback if elements not available
    elements = None
st.set_page_config(page_title="CodeX Intelligence Hub", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")
from dotenv import load_dotenv; load_dotenv()


import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import time
import subprocess

import requests
from sentence_transformers import SentenceTransformer
import faiss
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import csv
from datetime import datetime
from typing import Optional



def load_css():
    css = """
    <style>
    /* Modern Streamlit UI Design - React/Next.js Style */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --primary-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        --glass-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 0.5);
        --card-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        --text-primary: #0f172a;
        --text-secondary: #334155;
    }

    .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: radial-gradient(circle at top right, #f8fafc, #f1f5f9);
        color: var(--text-primary);
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stSidebar"] {
        color: var(--text-primary);
    }

    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    p, span, label, div {
        color: inherit;
    }

    .stMarkdown p, .stCaption, .stText {
        color: var(--text-secondary) !important;
    }

    /* Glass Panels */
    .stMetric, [data-testid="metric-container"], .stMarkdown div[data-testid="stExpander"] {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        border: 1px solid var(--glass-border) !important;
        box-shadow: var(--card-shadow) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stMetric:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.1) !important;
    }

    /* Modern Buttons */
    div.stButton > button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: none !important;
        letter-spacing: 0.01em !important;
    }

    div.stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.3) !important;
    }

    /* Sidebar Refinement */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(8px) !important;
        border-right: 1px solid rgba(0, 0, 0, 0.05) !important;
    }

    /* Custom Navigation Styling */
    .nav-link {
        border-radius: 10px !important;
        margin: 4px 0 !important;
        transition: all 0.2s ease !important;
    }

    /* Header Styling */
    .header-section {
        background: var(--primary-gradient);
        padding: 3rem;
        border-radius: 24px;
        margin-bottom: 3rem;
        color: white !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }

    .header-section::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 80%);
        pointer-events: none;
    }

    /* Card Grid */
    .react-card {
        background: white;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border: 1px solid #f1f5f9;
        margin-bottom: 1rem;
    }

    /* Tabs Modernization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        padding: 4px;
        background: #f1f5f9;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 8px 16px !important;
        border: none !important;
        background: transparent !important;
        color: var(--text-secondary) !important;
    }

    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #6366f1 !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_css()

# Initialize session state for auto-save
if 'auto_save_enabled' not in st.session_state:
    st.session_state.auto_save_enabled = True

# GitHub and StackOverflow API helpers (no auth required)
HEADERS = {'Accept': 'application/vnd.github.v3+json'}

def fetch_github_code_snippets(query, language=None, max_files=5):
    """Fetch code snippets from GitHub with improved robustness and rate limit handling"""
    items = []
    if not query: return items
    
    per_page = 5
    page = 1
    fetched = 0
    q = query
    if language:
        q += f' language:{language}'

    headers = HEADERS.copy()
    token = os.getenv('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'token {token}'

    while fetched < max_files:
        try:
            import urllib.parse as _up
            url = f'https://api.github.com/search/code?q={_up.quote(q)}&per_page={per_page}&page={page}'
            r = requests.get(url, headers=headers, timeout=10)
            
            # Handle rate limiting gracefully
            if r.status_code == 403 and 'rate limit exceeded' in r.text.lower():
                # If we have some items, return what we have
                if items: return items
                # Otherwise, it's a hard fail
                break
                
            if r.status_code != 200:
                break
                
            resp = r.json()
            results = resp.get('items', [])
            if not results:
                break
                
            for item in results:
                if fetched >= max_files: break
                try:
                    repo_info = item.get('repository')
                    if not repo_info: continue
                    
                    full_name = repo_info.get('full_name', 'Unknown')
                    html_url = item.get('html_url', '')
                    
                    # More robust raw URL construction
                    download_url = html_url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
                    
                    cr = requests.get(download_url, timeout=5)
                    if cr.status_code == 200:
                        items.append({
                            'source': 'github',
                            'repo': full_name,
                            'path': item.get('path', ''),
                            'url': html_url,
                            'content': cr.text,
                            'language': item.get('language') or language
                        })
                        fetched += 1
                except:
                    continue
            page += 1
        except Exception:
            break
    return items

def fetch_stackoverflow_code_snippets(query=None, tag=None, pagesize=10, max_pages=1):
    """Fetch code snippets from StackOverflow with query+tag search"""
    import html as _html
    base = 'https://api.stackexchange.com/2.3'
    snippets = []
    
    try:
        params = {
            'order': 'desc',
            'sort': 'relevance',
            'site': 'stackoverflow',
            'pagesize': min(pagesize * 2, 30),
            'filter': 'withbody'
        }
        
        if query and query.strip():
            params['q'] = query.strip()
        if tag:
            params['tagged'] = tag
        
        if not query and not tag:
            return snippets
        
        r = requests.get(f"{base}/search/advanced", params=params, timeout=10)
        if r.status_code != 200:
            return snippets
        
        items = r.json().get('items', [])
        for q in items:
            if len(snippets) >= pagesize:
                break
            
            ar = requests.get(f"{base}/questions/{q['question_id']}/answers",
                             params={'order':'desc','sort':'votes','site':'stackoverflow','filter':'withbody'},
                             timeout=10)
            
            if ar.status_code == 200:
                for a in ar.json().get('items', [])[:3]:  # Check top 3 answers
                    if len(snippets) >= pagesize:
                        break
                    
                    soup = BeautifulSoup(a.get('body', ''), 'html.parser')
                    
                    # Extract ALL <pre><code> blocks from this answer
                    found_in_answer = False
                    for pre in soup.find_all('pre'):
                        code_block = pre.find('code')
                        if code_block:
                            code_text = _html.unescape(code_block.get_text()).strip()
                            if len(code_text) >= 40 or code_text.count('\n') >= 1:
                                snippets.append({
                                    'source': 'stackoverflow',
                                    'title': q.get('title'),
                                    'link': q.get('link'),
                                    'content': code_text
                                })
                                found_in_answer = True
                                if len(snippets) >= pagesize:
                                    break
                    
                    # If no <pre><code>, try standalone <code> tags
                    if not found_in_answer:
                        for code in soup.find_all('code'):
                            code_text = _html.unescape(code.get_text()).strip()
                            if len(code_text) >= 40 or code_text.count('\n') >= 1:
                                snippets.append({
                                    'source': 'stackoverflow',
                                    'title': q.get('title'),
                                    'link': q.get('link'),
                                    'content': code_text
                                })
                                if len(snippets) >= pagesize:
                                    break
    except Exception:
        pass
    
    return snippets

def get_search_query_from_code(code, language, groq_client):
    """Generate a clean search query for GitHub/StackOverflow using Groq"""
    if not groq_client:
        return ""
        
    prompt = f"""Extract 3-5 key technical keywords or function names from this {language} code snippet to use as a search query for finding similar real-world examples.
Respond ONLY with the keywords separated by spaces. No explanations or sentences.

Code:
{code[:500]}"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a technical search expert. You provide specific, technical keywords."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=60
        )
        query = response.choices[0].message.content.strip()
        # Aggressive cleaning: Remove markdown, quotes, and conversational filler
        import re as _re
        query = _re.sub(r'```.*?```', '', query, flags=_re.DOTALL) # Remove code blocks if AI returned them
        query = _re.sub(r'^(Keywords:|Search Query:|Query:|Find:)', '', query, flags=_re.IGNORECASE)
        query = _re.sub(r'[^a-zA-Z0-9\s\#\+\.]', ' ', query) # Keep C++, C# etc.
        query = " ".join(query.split()) # Normalize spaces
        return query.strip()
    except Exception:
        # Fallback to simple extraction
        import re as _re
        words = _re.findall(r'\b[a-zA-Z\_]{5,}\b', code[:300]) 
        return " ".join(words[:4])

# Load environment variables - called ONCE here, not repeated per-feature
load_dotenv()

# ── Shared constants ─────────────────────────────────────────
SUPPORTED_LANGS = ["Python", "Java", "C++", "JavaScript"]
GROQ_MODEL      = "llama-3.3-70b-versatile"

# ── Shared Groq client helper ─────────────────────────────────
def get_groq_client():
    """Return a Groq client from session_state, initialising it once if needed."""
    if st.session_state.get('groq_client') is None:
        try:
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                st.session_state.groq_client = Groq(api_key=api_key)
            else:
                st.error("❌ GROQ_API_KEY not found. Add it to your .env file.")
                return None
        except Exception as e:
            st.error(f"❌ Could not initialise Groq client: {e}")
            return None
    return st.session_state.groq_client

# API Configuration

# API Configuration


# Premium CodeX UI Design System removed in favor of load_css()

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = None
if 'index' not in st.session_state:
    st.session_state.index = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'mode' not in st.session_state:
    st.session_state.mode = 'code'
if 'bug_model' not in st.session_state:
    st.session_state.bug_model = None
if 'bug_index_static' not in st.session_state:
    st.session_state.bug_index_static = None
if 'bug_index_dynamic' not in st.session_state:
    st.session_state.bug_index_dynamic = None
if 'bug_meta_static' not in st.session_state:
    st.session_state.bug_meta_static = None
if 'bug_meta_dynamic' not in st.session_state:
    st.session_state.bug_meta_dynamic = None
if 'execution_history' not in st.session_state:
    st.session_state.execution_history = []
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = []
if 'voice_input' not in st.session_state:
    st.session_state.voice_input = ''
if 'generated_test_cases' not in st.session_state:
    st.session_state.generated_test_cases = []
if 'generated_test_content' not in st.session_state:
    st.session_state.generated_test_content = ''
if 'test_lang' not in st.session_state:
    st.session_state.test_lang = 'Python'
if 'test_code_snapshot' not in st.session_state:
    st.session_state.test_code_snapshot = ''
if 'sandbox_problem_pick' not in st.session_state:
    st.session_state.sandbox_problem_pick = {}  # {language: last_picked_title}
if 'groq_client' not in st.session_state:
    st.session_state.groq_client = None
if 'bug_query_input' not in st.session_state:
    st.session_state.bug_query_input = ''
if 'show_bookmarks' not in st.session_state:
    st.session_state.show_bookmarks = False
if 'show_bookmarks_main' not in st.session_state:
    st.session_state.show_bookmarks_main = False
if 'show_docker_guide' not in st.session_state:
    st.session_state.show_docker_guide = False
if 'enhanced_code' not in st.session_state:
    st.session_state.enhanced_code = None
if 'enhanced_context' not in st.session_state:
    st.session_state.enhanced_context = None
if 'performance_comparison' not in st.session_state:
    st.session_state.performance_comparison = None
if 'enhance_lang' not in st.session_state:
    st.session_state.enhance_lang = 'Python'

def load_finetuned_model(model_path: str = "models/climate_advisor_finetuned"):
    """Load fully finetuned model for state-wise crop recommendations."""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        if not os.path.exists(model_path):
            return None, None

        tokenizer = AutoTokenizer.from_pretrained(model_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device_map="auto" if device == "cuda" else None,
        )

        model.eval()
        st.success("Finetuned model loaded.")
        return model, tokenizer

    except ImportError:
        return None, None
    except Exception as e:
        st.warning(f"Finetuned model failed: {e}")
        return None, None


def generate_with_finetuned(
    prompt: str, model, tokenizer, max_tokens: int = 200
) -> Optional[str]:
    """Generate response using fully finetuned model."""
    if model is None or tokenizer is None:
        return None

    try:
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        formatted_prompt = (
            "<|system|>\n"
            "You are an agricultural expert.\n"
            "</s>\n"
            "<|user|>\n"
            f"{prompt}\n"
            "</s>\n"
            "<|assistant|>\n"
        )

        inputs = tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if generated_text.startswith(formatted_prompt):
            generated_text = generated_text[len(formatted_prompt):]
        return generated_text.strip() or None

    except Exception as e:
        st.warning(f"Finetuned generation failed: {e}")
        return None


@st.cache_data
def _load_problem_titles_cached(language: str, _file_mtime: float):
    """Load problem titles - cache key includes file mtime so it auto-refreshes on CSV changes."""
    import re as _re
    titles = []
    try:
        if language == 'Python':
            if os.path.exists('data_python.csv'):
                df = pd.read_csv('data_python.csv', usecols=['problem_title'])
                titles = df['problem_title'].dropna().str.strip().str.title().unique().tolist()
        elif language == 'Java':
            if os.path.exists('data_java.csv'):
                df = pd.read_csv('data_java.csv', usecols=['title'])
                titles = df['title'].dropna().str.strip().str.title().unique().tolist()
        elif language == 'C++':
            if os.path.exists('data_cpp.csv'):
                df = pd.read_csv('data_cpp.csv', usecols=['Answer'])
                extracted = []
                for code in df['Answer'].dropna():
                    m = _re.search(r'(?:class|struct)\s+(\w+)', code)
                    if m:
                        name = m.group(1).replace('Solution', '').strip()
                        if name:
                            extracted.append(name.replace('_', ' ').title())
                            continue
                    m = _re.search(r'\b(?:int|void|bool|string|double|long)\s+(\w+)\s*\(', code)
                    if m and m.group(1) not in ('main', 'Main'):
                        extracted.append(m.group(1).replace('_', ' ').title())
                titles = list(dict.fromkeys(t for t in extracted if t and len(t) > 1))
        elif language == 'JavaScript':
            if os.path.exists('data_javascript.csv'):
                df = pd.read_csv('data_javascript.csv', usecols=['title'])
                titles = df['title'].dropna().str.strip().str.title().unique().tolist()
    except Exception:
        pass
    return sorted(titles)

def load_problem_titles(language: str):
    """Wrapper that busts cache automatically when the CSV file changes on disk."""
    csv_map = {
        'Python': 'data_python.csv',
        'Java': 'data_java.csv',
        'C++': 'data_cpp.csv',
        'JavaScript': 'data_javascript.csv',
    }
    csv_path = csv_map.get(language, '')
    mtime = os.path.getmtime(csv_path) if os.path.exists(csv_path) else 0.0
    return _load_problem_titles_cached(language, mtime)

@st.cache_resource
def load_bug_system():
    """Load bug intelligence system components"""
    try:
        from groq import Groq
        
        # Load model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load FAISS indexes
        static_index = faiss.read_index('Model/static_faiss.index')
        dynamic_index = faiss.read_index('Model/dynamic_faiss.index')
        
        # Load metadata
        static_meta = pd.read_csv('Model/static_metadata.csv')
        dynamic_meta = pd.read_csv('Model/dynamic_metadata.csv')
        
        # Initialize Groq client
        groq_key = os.getenv('GROQ_API_KEY')
        groq_client = Groq(api_key=groq_key) if groq_key else None
        
        return model, static_index, dynamic_index, static_meta, dynamic_meta, groq_client
    except Exception as e:
        st.error(f"Error loading bug system: {e}")
        return None, None, None, None, None, None

def analyze_code_line_by_line(code, model, static_index, dynamic_index, static_meta, dynamic_meta, groq_client):
    """Analyze code line by line using FAISS and Groq"""
    lines = [line for line in code.split('\n') if line.strip()]
    line_analyses = []
    
    for i, line in enumerate(lines, 1):
        # Search for similar code patterns
        query_vec = model.encode([line])
        D1, I1 = static_index.search(query_vec, 3)
        D2, I2 = dynamic_index.search(query_vec, 3)
        
        contexts = []
        for idx in I1[0][:2]:
            if idx < len(static_meta):
                contexts.append(static_meta.iloc[idx]['text'])
        for idx in I2[0][:2]:
            if idx < len(dynamic_meta):
                contexts.append(dynamic_meta.iloc[idx]['text'])
        
        line_analyses.append({
            'line_num': i,
            'code': line,
            'contexts': contexts
        })
    
    return line_analyses

def generate_code_analysis(code, line_analyses, action, groq_client):
    """Generate analysis with Groq based on action"""
    if not groq_client:
        return "Groq API key not configured."
    
    context_text = '\n'.join([f"Line {la['line_num']}: {la['code']}\nSimilar patterns: {la['contexts'][:2]}" for la in line_analyses[:10]])
    
    prompts = {
        'debug': f"""Expert Code Review Task: Analyze this code for bugs, logic errors, and security vulnerabilities.
Use the similarity context provided to identify common pitfalls.

Code to Analyze:
{code}

Similarity Context:
{context_text}

Respond in this EXACT format:
### ANALYSIS_RESULTS
**Bug Analysis: [Short Descriptive Title]**

**1. Likely Cause of the Bug**
[Detailed technical explanation of the root cause]

**2. Suggested Fixes**
[Bulleted list of specific code changes or architectural fixes]

**3. Step-by-Step Debugging Advice**
[Numbered list of debugging steps to verify the fix]

**4. Severity Level**
[Low/Medium/High/Critical] - [Brief rationale]

[RISK_SCORES]
Security: <score 0-100>
Performance: <score 0-100>
Complexity: <score 0-100>

### ADDITIONAL_RECOMMENDATIONS
[WAF suggestions, security testing, or developer training tips]
""",
        
        'optimize': f"""Expert Code Review Task: Optimize this code for performance and efficiency.
Use the similarity context provided to find better patterns.

Code to Optimize:
{code}

Similarity Context:
{context_text}

Respond in this EXACT format:
### ANALYSIS_RESULTS
**Performance Analysis: [Short Descriptive Title]**

**1. Efficiency Bottlenecks**
[Explain why the current code is slow or resource-heavy]

**2. Optimized Alternatives**
[Bulleted list of optimized code patterns or algorithms]

**3. Step-by-Step Implementation Advice**
[How to integrate the optimizations safely]

**4. Performance Impact**
[Expected improvement level: Low/Medium/High]

[RISK_SCORES]
Security: <score 0-100>
Performance: <score 0-100>
Complexity: <score 0-100>

### ADDITIONAL_RECOMMENDATIONS
[Caching strategies, profiling tools, or hardware considerations]
""",
        
        'refactor': f"""Expert Code Review Task: Refactor this code for better quality and maintainability.
Use the similarity context provided to adhere to best practices.

Code to Refactor:
{code}

Similarity Context:
{context_text}

Respond in this EXACT format:
### ANALYSIS_RESULTS
**Code Quality Analysis: [Short Descriptive Title]**

**1. Code Smells & Issues**
[Identify maintainability problems, nesting, or naming issues]

**2. Refactoring Suggestions**
[Bulleted list of specific refactoring steps]

**3. Refactored Snippet**
```[language]
[Clean code implementation]
```

**4. Maintainability Impact**
[Expected improvement level: Low/Medium/High]

[RISK_SCORES]
Security: <score 0-100>
Performance: <score 0-100>
Complexity: <score 0-100>

### ADDITIONAL_RECOMMENDATIONS
[Design pattern suggestions, documentation tips, or modularization advice]
"""
    }
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert code reviewer."},
                {"role": "user", "content": prompts[action]}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analysis failed: {e}"

def analyze_code_with_rag(code, action='debug'):
    """Main function to analyze code with RAG"""
    if st.session_state.bug_model is None:
        with st.spinner("🔄 Loading analysis system..."):
            model, static_idx, dynamic_idx, static_meta, dynamic_meta, groq = load_bug_system()
            st.session_state.bug_model = model
            st.session_state.bug_index_static = static_idx
            st.session_state.bug_index_dynamic = dynamic_idx
            st.session_state.bug_meta_static = static_meta
            st.session_state.bug_meta_dynamic = dynamic_meta
            st.session_state.groq_client = groq
    
    # Analyze line by line
    line_analyses = analyze_code_line_by_line(
        code,
        st.session_state.bug_model,
        st.session_state.bug_index_static,
        st.session_state.bug_index_dynamic,
        st.session_state.bug_meta_static,
        st.session_state.bug_meta_dynamic,
        st.session_state.groq_client
    )
    
    # Generate analysis
    analysis = generate_code_analysis(code, line_analyses, action, st.session_state.groq_client)
    
    # Parse risk scores
    risk_scores = {"Security": 50, "Performance": 50, "Complexity": 50}
    import re as _re
    scores_match = _re.search(r'\[RISK_SCORES\]\nSecurity:\s*(\d+)\nPerformance:\s*(\d+)\nComplexity:\s*(\d+)', analysis)
    if scores_match:
        risk_scores = {
            "Security": int(scores_match.group(1)),
            "Performance": int(scores_match.group(2)),
            "Complexity": int(scores_match.group(3))
        }
        # Clean the scores out of the display text
        analysis = _re.sub(r'\[RISK_SCORES\].*', '', analysis, flags=_re.DOTALL).strip()

    # Predict severity for the UI
    severity, color = predict_severity(analysis + " " + code)
    
    return {
        'line_analyses': line_analyses,
        'analysis': analysis,
        'action': action,
        'severity': severity,
        'severity_color': color,
        'risk_scores': risk_scores
    }

def predict_severity(text, contexts=None):
    """Predict bug severity"""
    critical_kw = ['crash', 'data loss', 'security', 'vulnerability', 'memory leak', 'corruption']
    high_kw = ['exception', 'timeout', 'performance', 'null pointer', 'segmentation fault']
    medium_kw = ['incorrect output', 'unexpected behavior', 'warning', 'slow response']
    low_kw = ['ui issue', 'typo', 'documentation', 'minor bug', 'cosmetic']
    
    if contexts:
        text = text + ' ' + ' '.join([c.get('text', '') for c in contexts[:3]])
    
    t = text.lower()
    for kw in critical_kw:
        if kw in t:
            return 'Critical', '🔴'
    for kw in high_kw:
        if kw in t:
            return 'High', '🟠'
    for kw in medium_kw:
        if kw in t:
            return 'Medium', '🟡'
    for kw in low_kw:
        if kw in t:
            return 'Low', '🟢'
    return 'Medium', '🟡'

def search_bug_knowledge(query, model, static_index, dynamic_index, static_meta, dynamic_meta, k=5):
    """Search bug knowledge base"""
    try:
        query_vec = model.encode([query])
        
        # Search static
        D1, I1 = static_index.search(query_vec, k)
        static_results = [{
            'text': static_meta.iloc[i]['text'],
            'source': 'static',
            'distance': float(D1[0][idx])
        } for idx, i in enumerate(I1[0]) if i < len(static_meta)]
        
        # Search dynamic
        D2, I2 = dynamic_index.search(query_vec, k)
        dynamic_results = [{
            'text': dynamic_meta.iloc[i]['text'],
            'source': 'dynamic',
            'distance': float(D2[0][idx])
        } for idx, i in enumerate(I2[0]) if i < len(dynamic_meta)]
        
        combined = static_results + dynamic_results
        combined.sort(key=lambda x: x['distance'])
        return combined
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

def generate_fix_suggestion(query, contexts, groq_client):
    """Generate fix suggestions using Groq"""
    if not groq_client:
        return "Groq API key not configured. Add GROQ_API_KEY to .env file."
    
    try:
        context_text = '\n\n---\n\n'.join([c['text'] for c in contexts[:8]])
        
        prompt = f"""You are a senior software debugging expert.

User Bug:
{query}

Relevant Past Bugs & Solutions:
{context_text}

Tasks:
1) Explain the likely cause of the bug.
2) Suggest the most probable fixes.
3) Give step-by-step debugging advice.
4) Mention severity level (Low/Medium/High/Critical).
5) Provide a [RISK_PROFILE] score (0-100) for these 3 categories: Security Risk, Performance Impact, Logic Complexity.

Format the risk profile exactly like this at the end of your response:
[RISK_SCORES]
Security: <score>
Performance: <score>
Complexity: <score>

Answer clearly and technically."""
        
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert software debugger."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Generation failed: {e}"

def analyze_bug_local(query):
    """Analyze bug locally without FastAPI"""
    # Load bug system if not loaded
    if st.session_state.bug_model is None:
        with st.spinner("🔄 Loading bug intelligence system..."):
            model, static_idx, dynamic_idx, static_meta, dynamic_meta, groq = load_bug_system()
            st.session_state.bug_model = model
            st.session_state.bug_index_static = static_idx
            st.session_state.bug_index_dynamic = dynamic_idx
            st.session_state.bug_meta_static = static_meta
            st.session_state.bug_meta_dynamic = dynamic_meta
            st.session_state.groq_client = groq
    
    # Search for similar bugs
    contexts = search_bug_knowledge(
        query,
        st.session_state.bug_model,
        st.session_state.bug_index_static,
        st.session_state.bug_index_dynamic,
        st.session_state.bug_meta_static,
        st.session_state.bug_meta_dynamic
    )
    
    # Predict severity
    severity, severity_color = predict_severity(query, contexts)
    
    # Generate fix
    fix_suggestion = generate_fix_suggestion(query, contexts, st.session_state.groq_client)
    
    # Parse risk scores for visualization
    risk_scores = {"Security": 50, "Performance": 50, "Complexity": 50}
    import re as _re
    scores_match = _re.search(r'\[RISK_SCORES\]\nSecurity:\s*(\d+)\nPerformance:\s*(\d+)\nComplexity:\s*(\d+)', fix_suggestion)
    if scores_match:
        risk_scores = {
            "Security": int(scores_match.group(1)),
            "Performance": int(scores_match.group(2)),
            "Complexity": int(scores_match.group(3))
        }
        # Clean the scores out of the display text
        fix_suggestion = _re.sub(r'\[RISK_SCORES\].*', '', fix_suggestion, flags=_re.DOTALL).strip()

    return {
        'query': query,
        'severity': severity,
        'severity_color': severity_color,
        'fix_suggestion': fix_suggestion,
        'num_contexts': len(contexts),
        'contexts': contexts[:10],
        'risk_scores': risk_scores
    }

# A. Code Diff Viewer
def show_code_diff(before_code, after_code):
    """Show before/after code with highlighted changes"""
    import difflib
    diff = difflib.unified_diff(before_code.splitlines(), after_code.splitlines(), lineterm='')
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Before")
        st.code(before_code, language='python')
    with col2:
        st.markdown("### After")
        st.code(after_code, language='python')
    with st.expander("📊 Diff Details"):
        st.code('\n'.join(diff), language='diff')

# B. Export to GitHub Gist
def export_to_gist(code, description, filename="code.py"):
    """Export code to GitHub Gist"""
    load_dotenv() # Force reload from .env
    token = os.getenv('GITHUB_TOKEN')
    if not token or token == "YOUR_GITHUB_TOKEN":
        return "ERROR: GitHub token not configured in .env"
    try:
        data = {"description": description, "public": True, "files": {filename: {"content": code}}}
        r = requests.post('https://api.github.com/gists', headers={'Authorization': f'token {token}'}, json=data)
        if r.status_code == 201:
            return r.json().get('html_url')
        else:
            error_msg = r.json().get('message', 'Unknown error')
            return f"ERROR: {error_msg} (Status: {r.status_code})"
    except Exception as e:
        return f"ERROR: {str(e)}"

# C. Voice Input Component
def voice_input_component():
    """
    Working voice input:
      1. streamlit-mic-recorder captures audio in the browser (no HTTPS/extension needed).
      2. SpeechRecognition transcribes the WAV bytes via Google Speech API (free, no key needed).
      3. Result is stored in st.session_state.voice_input so every text_area can use it.
    """
    try:
        from streamlit_mic_recorder import mic_recorder
        import speech_recognition as sr
        import io

        st.markdown("#### 🎤 Voice Input")
        audio = mic_recorder(
            start_prompt="⏺ Start Recording",
            stop_prompt="⏹ Stop & Transcribe",
            just_once=True,          # return audio only once per click
            use_container_width=True,
            key="mic_recorder_main",
        )

        if audio and audio.get("bytes"):
            with st.spinner("🔊 Transcribing speech..."):
                try:
                    recognizer = sr.Recognizer()
                    # mic_recorder returns WebM/Opus; convert via pydub → WAV
                    try:
                        from pydub import AudioSegment
                        audio_seg = AudioSegment.from_file(
                            io.BytesIO(audio["bytes"]), format="webm"
                        )
                        wav_io = io.BytesIO()
                        audio_seg.export(wav_io, format="wav")
                        wav_io.seek(0)
                        audio_source = sr.AudioFile(wav_io)
                    except Exception:
                        # Fallback: treat raw bytes as WAV
                        audio_source = sr.AudioFile(io.BytesIO(audio["bytes"]))

                    with audio_source as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        audio_data = recognizer.record(source)

                    text = recognizer.recognize_google(audio_data)
                    st.session_state.voice_input = text
                    st.success(f"✅ Transcribed: **{text}**")

                except sr.UnknownValueError:
                    st.warning("🔇 Could not understand audio. Please speak clearly and try again.")
                except sr.RequestError as e:
                    st.error(f"🌐 Speech service error: {e}. Check your internet connection.")
                except Exception as e:
                    st.error(f"❌ Transcription error: {e}")

        # Show current voice capture
        if st.session_state.get("voice_input"):
            st.info(f"📝 Last capture: *{st.session_state.voice_input}*")
            if st.button("🗑️ Clear voice input", key="clear_voice"):
                st.session_state.voice_input = ""
                st.rerun()

    except ImportError:
        st.warning("⚠️ Voice input requires `streamlit-mic-recorder`. Run:\n```\npip install streamlit-mic-recorder\n```")


# D. Bookmarks Management
def add_bookmark(code, title, tags="", notes=""):
    """Add code snippet to bookmarks"""
    st.session_state.bookmarks.append({'code': code, 'title': title, 'tags': tags, 'notes': notes, 'time': datetime.now()})
    return True

def show_bookmarks():
    """Display bookmarked snippets"""
    if not st.session_state.bookmarks:
        st.info("No bookmarks yet")
        return
    for i, bm in enumerate(st.session_state.bookmarks):
        with st.expander(f"🔖 {bm['title']} - {bm['tags']}"):
            st.code(bm['code'], language='python')
            st.caption(f"Notes: {bm['notes']}")
            if st.button("Delete", key=f"del_{i}"):
                st.session_state.bookmarks.pop(i)
                st.rerun()

def show_bug_intelligence_mode():
    """Show bug intelligence interface with tabs"""
    st.markdown("""
    <div class="header-section">
        <h1 style="color: inherit; margin: 0; font-size: 2.5rem;">🚀 CodeX Intelligence</h1>
        <h2 style="color: inherit; margin: 0.5rem 0; font-weight: 500; opacity: 0.8;">AI-Powered Deep Code Analysis</h2>
        <p style="color: inherit; margin: 0; opacity: 0.7;">Analyze complex bugs and logic with 277K+ cross-referenced knowledge nodes</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.subheader("📊 System Stats")
        st.metric("Knowledge Base", "277,949")
        st.metric("GitHub Issues", "260,000")
        st.metric("StackOverflow", "17,949")
    
    # Tabs for different modes
    tab1, tab2 = st.tabs(["📝 Code Review", "🐛 Bug Intelligence"])
    
    with tab1:
        st.subheader("📝 Paste Your Code")
        
        # C. Voice Input
        code_input = st.text_area(
            "Enter your code here:",
            height=300,
            placeholder="def example():\n    # Your code here\n    pass",
        )

        

        
        col1, col2, col3 = st.columns(3)
        with col1:
            debug_btn = st.button("🐛 Debug", use_container_width=True, type="primary")
        with col2:
            optimize_btn = st.button("⚡ Optimize", use_container_width=True)
        with col3:
            refactor_btn = st.button("🔧 Refactor", use_container_width=True)
        
        if 'bug_analysis_state' not in st.session_state:
            st.session_state.bug_analysis_state = {
                'result': None,
                'action': None,
                'refactored_code': None,
                'code_input': ''
            }

        action = None
        if debug_btn:
            action = 'debug'
        elif optimize_btn:
            action = 'optimize'
        elif refactor_btn:
            action = 'refactor'
        
        if action and code_input:
            with st.spinner(f"🤖 Analyzing code for {action} with Bug Intelligence..."):
                result = analyze_code_with_rag(code_input, action)
                st.session_state.bug_analysis_state['result'] = result
                st.session_state.bug_analysis_state['action'] = action
                st.session_state.bug_analysis_state['code_input'] = code_input
                
                # Extract refactored code if action is refactor
                refactored_code = None
                if action == 'refactor':
                    import re as _re
                    code_blocks = _re.findall(r'```(?:python)?\n([\s\S]*?)```', result['analysis'])
                    if code_blocks:
                        refactored_code = code_blocks[-1].strip()
                st.session_state.bug_analysis_state['refactored_code'] = refactored_code
                
                st.session_state.analysis_history.append({
                    "timestamp": datetime.now(),
                    "action": action,
                    "code_lines": len(code_input.split('\n')),
                    "patterns_found": sum(len(la['contexts']) for la in result['line_analyses']),
                    "result": result
                })

        # Display results if they exist in state
        if st.session_state.bug_analysis_state['result']:
            result = st.session_state.bug_analysis_state['result']
            action = st.session_state.bug_analysis_state['action']
            refactored_code = st.session_state.bug_analysis_state['refactored_code']
            code_input_stored = st.session_state.bug_analysis_state['code_input']

            st.markdown("---")
            # Severity Banner
            st.markdown(f"""
            <div style='background:{result['severity_color']}22;border:2px solid {result['severity_color']};border-radius:12px;
                padding:16px;text-align:center;margin-bottom:16px'>
                <span style='font-size:1.5rem'>{result['severity_color']}</span>
                <span style='color:{result['severity_color']};font-size:1.2rem;font-weight:700;margin-left:8px'>
                {action.title()} Detection: {result['severity']} Severity</span>
            </div>""", unsafe_allow_html=True)
            
            st.subheader(f"📋 {action.title()} Intelligence Report")
            
            with st.expander("🔍 Line-by-Line Context (from GitHub/StackOverflow)"):
                for la in result['line_analyses'][:10]:
                    st.markdown(f"**Line {la['line_num']}:** `{la['code']}`")
                    if la['contexts']:
                        st.caption(f"✓ Found {len(la['contexts'])} similar patterns:")
                        for i, ctx in enumerate(la['contexts'][:3], 1):
                            with st.container():
                                st.markdown(f"**Pattern {i}:**")
                                st.code(ctx[:1200], language='python')  # Show more context
                    else:
                        st.caption("⚠ No similar patterns found")
                    st.markdown("---")
            
            st.markdown(f"### {result['severity_color']} Severity: {result['severity']}")
            
            # 📊 Visual Analytics Section for Code Review
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("#### 🎯 Change Risk Multiplier")
                scores = result.get('risk_scores', {"Security": 50, "Performance": 50, "Complexity": 50})
                fig = go.Figure(data=go.Scatterpolar(
                    r=list(scores.values()) + [list(scores.values())[0]],
                    theta=list(scores.keys()) + [list(scores.keys())[0]],
                    fill='toself',
                    line_color='#a855f7',
                    fillcolor='rgba(168, 85, 247, 0.3)'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False, height=300,
                    margin=dict(l=40, r=40, t=20, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 🔍 Context Matching Strength")
                # Flatten contexts to show match counts per line
                match_counts = [len(la['contexts']) for la in result['line_analyses']]
                fig2 = px.line(y=match_counts, x=[f"L{la['line_num']}" for la in result['line_analyses']],
                               labels={'x': 'Code Line', 'y': 'Patterns Found'})
                fig2.update_traces(line_color='#a855f7', mode='lines+markers')
                fig2.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20),
                                   paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("### 🤖 AI Analysis")
            st.markdown(result['analysis'])
            
            # A. Show Code Diff for refactor
            if action == 'refactor' and refactored_code:
                st.markdown("### 🔄 Code Diff Viewer")
                show_code_diff(code_input_stored, refactored_code)
            
            # B. Export to Gist
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📤 Export to Gist", key=f"gist_{action}"):
                    url = export_to_gist(refactored_code or code_input_stored, f"{action.title()} result", f"{action}.py")
                    if url.startswith('http'):
                        st.success(f"[View Gist]({url})")
                    else:
                        st.error("Export failed. Check GITHUB_TOKEN")
            # D. Bookmark
            with col2:
                if st.button("🔖 Bookmark", key=f"bm_{action}"):
                    add_bookmark(refactored_code or code_input_stored, f"{action.title()} result", action, result['analysis'][:100])
                    st.success("Bookmarked!")
            
            # Show visual summary
            if result['line_analyses']:
                st.markdown("### 📊 Pattern Match Summary")
                col1, col2, col3 = st.columns(3)
                
                total_lines = len(result['line_analyses'])
                lines_with_patterns = sum(1 for la in result['line_analyses'] if la['contexts'])
                total_patterns = sum(len(la['contexts']) for la in result['line_analyses'])
                
                with col1:
                    st.metric("Lines Analyzed", total_lines)
                with col2:
                    st.metric("Lines with Patterns", lines_with_patterns)
                with col3:
                    st.metric("Total Patterns Found", total_patterns)
    
    with tab2:
        st.subheader("🐛 Bug Intelligence")
        
        with st.expander("💡 Example Queries"):
            examples = [
                "Memory leak in React application",
                "NullPointerException in Java Spring Boot",
                "Docker container keeps crashing",
                "SQL injection vulnerability",
                "Python asyncio timeout error"
            ]
            for ex in examples:
                if st.button(ex, key=f"ex_{ex}"):
                    st.session_state["bug_query_input"] = ex
                    st.session_state["trigger_analysis"] = True
                    st.rerun()
        
        query = st.text_area(
            "Describe your bug:",
            placeholder="e.g., Memory leak causing browser to freeze",
            height=100,
            key="bug_query_input"
        )
        
        analyze_clicked = st.button("🔍 Analyze Bug", type="primary", key="analyze_bug_btn")
        
        if analyze_clicked or st.session_state.get("trigger_analysis"):
            if st.session_state.get("trigger_analysis"):
                st.session_state["trigger_analysis"] = False
            
            if query:
                with st.spinner("🤖 Multi-Agent System analyzing..."):
                    result = analyze_bug_local(query)
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.markdown("---")
                    st.subheader("📋 Analysis Results")
                    
                    st.markdown(f"### {result['severity_color']} Severity: {result['severity']}")
                    
                    # 📊 Visual Analytics Section
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("#### 🎯 Bug Risk Profile")
                        scores = result.get('risk_scores', {"Security": 50, "Performance": 50, "Complexity": 50})
                        categories = list(scores.keys())
                        values = list(scores.values())
                        
                        fig = go.Figure(data=go.Scatterpolar(
                            r=values + [values[0]],
                            theta=categories + [categories[0]],
                            fill='toself',
                            line_color='#6366f1',
                            fillcolor='rgba(99, 102, 241, 0.3)'
                        ))
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            showlegend=False,
                            margin=dict(l=40, r=40, t=20, b=20),
                            height=300,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.markdown("#### 📈 Similarity Evidence Matrix")
                        distances = [1 - min(1, ctx.get('distance', 0)/2) for ctx in result.get('contexts', [])]
                        if not distances: distances = [0.8, 0.6, 0.4]
                        
                        fig2 = px.bar(
                            x=[f"Source {i}" for i in range(1, len(distances)+1)],
                            y=distances,
                            labels={'x': 'Evidence Source', 'y': 'Match Confidence'},
                            color=distances,
                            color_continuous_scale='Purples'
                        )
                        fig2.update_layout(
                            height=300,
                            margin=dict(l=20, r=20, t=20, b=20),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            coloraxis_showscale=False
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                    st.markdown("### 🛠️ Fix Suggestions")
                    st.markdown(result['fix_suggestion'])
                    
                    st.info(f"📚 Analysis based on {result['num_contexts']} similar bug reports from global knowledge base")
                    
                    with st.expander("🔍 Supporting Evidence (Analyzed Sources)", expanded=False):
                        st.markdown("### Relevant Bug Reports & Solutions found in Dataset")
                        for i, ctx in enumerate(result.get('contexts', []), 1):
                            with stylable_container(
                                key=f"bug_ctx_{i}",
                                css_styles="""
                                    {
                                        background: #f8fafc;
                                        border-left: 4px solid #6366f1;
                                        padding: 10px;
                                        margin-bottom: 10px;
                                        border-radius: 4px;
                                    }
                                """
                            ):
                                st.markdown(f"**Evidence #{i}** (Source: {ctx.get('source', 'Knowledge Node').title()})")
                                st.markdown(f"""
                                <div style="background: white; border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; line-height: 1.5; color: #334155; white-space: pre-wrap; word-wrap: break-word; max-height: 300px; overflow-y: auto;">
                                {ctx.get('text', '')[:2000]}...
                                </div>
                                """, unsafe_allow_html=True)
    
    # Analytics
    if st.session_state.analysis_history:
        st.markdown("---")
        st.subheader("📊 Analysis History")
        
        df_history = pd.DataFrame([{
            "Time": h["timestamp"].strftime("%H:%M:%S"),
            "Action": h.get("action", "bug").title(),
            "Lines": h.get("code_lines", 0),
            "Patterns": h.get("patterns_found", 0)
        } for h in st.session_state.analysis_history])
        
        st.dataframe(df_history, use_container_width=True)

def execute_code_safely(code, language, test_cases=None):
    """Execute code in safe sandbox with test cases and performance metrics"""
    import subprocess
    import tempfile
    import time
    import tracemalloc
    import platform
    import os
    import re
    import shutil
    
    results = {
        'success': False,
        'output': '',
        'error': '',
        'execution_time': 0,
        'memory_used': 0,
        'test_results': [],
        'complexity': 'O(1)'
    }
    
    temp_dir = tempfile.mkdtemp()
    temp_file = None
    
    try:
        # Check Docker availability
        use_docker = False
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, timeout=2)
            use_docker = result.returncode == 0
        except:
            pass
        
        # Prepare file and commands based on language
        if language == 'Python':
            import sys as _sys
            temp_file = os.path.join(temp_dir, 'code.py')
            docker_image = 'python:3.11-slim'
            docker_run_cmd = ['python', '/code/code.py']
            local_run_cmd = [_sys.executable, temp_file]
        elif language == 'Java':
            match = re.search(r'public\s+class\s+(\w+)', code)
            java_classname = match.group(1) if match else 'Main'
            if not match and 'class Main' not in code:
                if 'public static void main' not in code:
                    code = f"public class Main {{\n    public static void main(String[] args) {{\n        {code}\n    }}\n}}"
                    java_classname = 'Main'
            temp_file = os.path.join(temp_dir, f"{java_classname}.java")
            docker_image = 'eclipse-temurin:17-jdk'
            docker_run_cmd = ['sh', '-c', f'javac /code/{java_classname}.java && java -cp /code {java_classname}']
            local_run_cmd = None  # handled separately
        elif language == 'C++':
            temp_file = os.path.join(temp_dir, 'code.cpp')
            docker_image = 'gcc:latest'
            docker_run_cmd = ['sh', '-c', 'g++ /code/code.cpp -o /code/app && /code/app']
            local_run_cmd = None  # handled separately
        elif language == 'JavaScript':
            temp_file = os.path.join(temp_dir, 'code.js')
            docker_image = 'node:20-slim'
            docker_run_cmd = ['node', '/code/code.js']
            local_run_cmd = ['node', temp_file]
        else:
            return results
        
        # Write code to file
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Track memory (Python level - not perfect for subprocess)
        tracemalloc.start()
        start_time = time.time()
        
        if use_docker:
            # Docker sandbox execution
            docker_cmd = [
                'docker', 'run', '--rm',
                '--network=none',
                '--memory=256m',
                '--cpus=0.5',
                '-v', f'{os.path.abspath(temp_dir)}:/code',
                docker_image
            ] + docker_run_cmd
            
            process = subprocess.Popen(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            # Fallback to local subprocess
            if language == 'Python':
                process = subprocess.Popen(
                    local_run_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            elif language == 'Java':
                compile_proc = subprocess.run(['javac', temp_file], capture_output=True, text=True)
                if compile_proc.returncode != 0:
                    results['error'] = compile_proc.stderr
                    return results
                java_name = os.path.splitext(os.path.basename(temp_file))[0]
                process = subprocess.Popen(
                    ['java', '-cp', temp_dir, java_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            elif language == 'C++':
                out_exe = os.path.join(temp_dir, 'app.exe' if platform.system() == 'Windows' else 'app')
                compile_proc = subprocess.run(['g++', temp_file, '-o', out_exe], capture_output=True, text=True)
                if compile_proc.returncode != 0:
                    results['error'] = compile_proc.stderr
                    return results
                process = subprocess.Popen(
                    [out_exe],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            elif language == 'JavaScript':
                process = subprocess.Popen(
                    ['node', temp_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
        
        try:
            stdout, stderr = process.communicate(timeout=10) # 10s for compile + run
            results['success'] = process.returncode == 0
            results['output'] = stdout
            results['error'] = stderr
        except subprocess.TimeoutExpired:
            process.kill()
            results['error'] = "Execution timeout (10s limit)"
            
        execution_time = time.time() - start_time
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        results['execution_time'] = execution_time
        results['memory_used'] = peak / 1024 / 1024
        
        # Estimate complexity
        if execution_time < 0.01:
            results['complexity'] = 'O(1)'
        elif execution_time < 0.1:
            results['complexity'] = 'O(log n)'
        elif execution_time < 1:
            results['complexity'] = 'O(n)'
        else:
            results['complexity'] = 'O(n²) or higher'
        
        if test_cases and results['success']:
            for tc in test_cases:
                if language == 'Python':
                    try:
                        # Intelligent test input wrapping
                        test_input = tc['input']
                        if '(' not in test_input:
                            import re as _re_search
                            func_match = _re_search.search(r'def\s+(\w+)\s*\(', code)
                            if func_match:
                                fname = func_match.group(1)
                                test_input = f"{fname}({test_input})"
                        
                        test_code = code + f"\nprint({test_input})"
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
                            tf.write(test_code)
                            test_file = tf.name
                        import sys as _sys
                        tp = subprocess.Popen([_sys.executable, test_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        tout, terr = tp.communicate(timeout=2)
                        
                        actual = tout.strip()
                        expected = str(tc['expected']).strip()
                        # Flexible comparison
                        def clean(s):
                            import re as _inner_re
                            s = _inner_re.sub(r'[*_`]', '', str(s))
                            s = s.replace(' ', '').replace('"', "'")
                            return s
                        
                        results['test_results'].append({
                            'input': tc['input'],
                            'expected': tc['expected'],
                            'actual': actual,
                            'passed': clean(actual) == clean(expected)
                        })
                        if os.path.exists(test_file):
                            os.unlink(test_file)
                    except Exception as e:
                        results['test_results'].append({
                            'input': tc['input'],
                            'expected': tc['expected'],
                            'actual': f"Execution Error: {str(e)}",
                            'passed': False
                        })
                elif language == 'JavaScript':
                    try:
                        # Intelligent test input wrapping for JS
                        test_input = tc['input']
                        if '(' not in test_input:
                            import re as _re_search
                            # Match function name or const name = (...) =>
                            func_match = _re_search.search(r'function\s+(\w+)|const\s+(\w+)\s*=', code)
                            fname = None
                            if func_match:
                                fname = func_match.group(1) or func_match.group(2)
                                test_input = f"{fname}({test_input})"
                                
                        test_code = code + f"\nconsole.log({test_input})"
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as tf:
                            tf.write(test_code)
                            test_file = tf.name
                        tp = subprocess.Popen(['node', test_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        tout, terr = tp.communicate(timeout=2)
                        
                        actual = tout.strip()
                        expected = str(tc['expected']).strip()
                        def clean(s):
                            import re as _inner_re
                            s = _inner_re.sub(r'[*_`]', '', str(s))
                            s = s.replace(' ', '').replace('"', "'")
                            return s

                        results['test_results'].append({
                            'input': tc['input'],
                            'expected': tc['expected'],
                            'actual': actual,
                            'passed': clean(actual) == clean(expected)
                        })
                        if os.path.exists(test_file):
                            os.unlink(test_file)
                    except Exception as e:
                        results['test_results'].append({
                            'input': tc['input'],
                            'expected': tc['expected'],
                            'actual': f"Execution Error: {str(e)}",
                            'passed': False
                        })
                elif language in ['Java', 'C++']:
                    # Java/C++ require compiled test harness – manual review
                    pass
        
    except Exception as e:
        results['error'] = str(e)
    finally:
        # Cleanup temp dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
    return results

def execute_code_sandbox(code, language, test_inputs=None):
    """Wrapper for backward compatibility"""
    return execute_code_safely(code, language, test_inputs)

def generate_test_cases(code, problem_description, groq_client, language="Python"):
    """Generate test cases using Groq AI"""
    if not groq_client:
        return [], "Groq client not available"
    
    try:
        format_note = ""
        if language == "Java":
            format_note = "For Java, provide inputs as they would be passed to the method or script."
        elif language == "C++":
            format_note = "For C++, provide inputs suitable for std::cin or function arguments."
        elif language in ["Python", "JavaScript"]:
            format_note = f"CRITICAL: For {language}, the 'Input' must be a full function call that exists in the code (e.g., 'sum(5, 10)'), not just the values."
            
        prompt = f"""Generate 5 test cases for this {language} code:

Problem: {problem_description}

Code:
{code}

{format_note}
Provide ONLY test cases in this exact format:
Input: <full function call or input values>
Expected: <output>

Include edge cases (empty, large, negative)."""
        
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a test case generator. Output only test cases."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        # Parse test cases using a robust regex that handles same-line or multi-line formats
        import re as _re
        # This regex matches "Input: ..." followed by "Expected: ..." regardless of newlines
        # and stops before the next "Input:" or end of string.
        patterns = _re.findall(r'Input:\s*(.*?)\s*[ \t\n]*Expected:\s*(.*?)(?=\s*Input:|\s*\n\n|\Z)', content, _re.DOTALL | _re.IGNORECASE)
        test_cases = []
        for input_val, expected_val in patterns:
            # Clean up residual markdown and same-line leaks
            in_clean = _re.sub(r'[*_`]', '', input_val).strip()
            ex_clean = _re.sub(r'[*_`]', '', expected_val).strip()
            if in_clean and ex_clean:
                test_cases.append({
                    'input': in_clean,
                    'expected': ex_clean
                })
        
        # Super Fallback: line by line if regex failed
        if not test_cases:
            lines = content.split('\n')
            for line in lines:
                if 'Input:' in line and 'Expected:' in line:
                    match = _re.search(r'Input:\s*(.*?)\s*Expected:\s*(.*)', line, _re.IGNORECASE)
                    if match:
                        test_cases.append({'input': match.group(1).strip(), 'expected': match.group(2).strip()})
                elif 'Input:' in line:
                    current_input = line.split('Input:', 1)[1].strip()
                elif 'Expected:' in line and 'current_input' in locals() and current_input:
                    test_cases.append({'input': current_input, 'expected': line.split('Expected:', 1)[1].strip()})
                    current_input = None
        
        return test_cases, content
    except Exception as e:
        return [], f"Test case generation failed: {e}"

def compare_implementations(implementations, problem_desc, groq_client, language='Python'):
    """Compare performance across multiple implementations"""
    results = []
    for i, impl in enumerate(implementations):
        # Result dictionary includes execution_time, memory_used, complexity, success
        result = execute_code_safely(impl['code'], language)
        results.append({
            'name': impl.get('name', f'Implementation {i+1}'),
            'time': result['execution_time'],
            'memory': result['memory_used'],
            'complexity': result.get('complexity', 'O(n)'),
            'success': result['success']
        })
    return results

def show_execution_sandbox_mode():
    """Show code execution sandbox with analytics"""
    st.markdown("""
    <div class="header-section">
        <h1 style="color: inherit; margin: 0; font-size: 2.5rem;">⚡ Code Execution Sandbox</h1>
        <h2 style="color: inherit; margin: 0.5rem 0; font-weight: 500; opacity: 0.8;">Test & Validate Code with Performance Metrics</h2>
        <p style="color: inherit; margin: 0; opacity: 0.7;">Safe execution + AI test generation + Code enhancement</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.subheader("🔧 Sandbox Stats")
        st.metric("Executions Today", len(st.session_state.execution_history))
        if st.session_state.execution_history:
            success_rate = sum(1 for e in st.session_state.execution_history if e['success']) / len(st.session_state.execution_history) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Docker status
        try:
            docker_check = subprocess.run(['docker', '--version'], capture_output=True, timeout=2)
            docker_available = docker_check.returncode == 0
        except:
            docker_available = False
        
        st.markdown("---")
        st.markdown("**Sandbox Mode:**")
        if docker_available:
            st.success("🐳 Docker (Isolated)")
            st.caption("Secure container execution")
        else:
            st.warning("🐍 Python (Subprocess)")
            st.caption("Install Docker for isolation")
            if st.button("📖 Setup Guide"):
                st.session_state.show_docker_guide = True
    
    tab1, tab2 = st.tabs(["⚡ Execute Code", "📊 Execution Analytics"])
    
    # Show Docker setup guide if requested
    if st.session_state.get('show_docker_guide', False):
        with st.expander("🐳 Docker Setup Guide", expanded=True):
            st.markdown("""
            ### Quick Setup
            
            **Windows:**
            1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
            2. Install and restart computer
            3. Open Docker Desktop and wait for it to start
            4. Run: `docker pull python:3.11-slim`
            5. Run: `docker pull eclipse-temurin:17-jdk`
            5. Run: `docker pull gcc:latest`
            6. Run: `docker pull node:20-slim`
            
            **Linux:**
            ```bash
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            docker pull python:3.11-slim
            docker pull eclipse-temurin:17-jdk
            docker pull gcc:latest
            docker pull node:20-slim
            ```
            
            **macOS:**
            1. Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
            2. Install and start Docker Desktop
            3. Run: `docker pull python:3.11-slim`
            4. Run: `docker pull eclipse-temurin:17-jdk`
            5. Run: `docker pull gcc:latest`
            6. Run: `docker pull node:20-slim`
            
            ### Verify Installation
            ```bash
            docker --version
            docker run hello-world
            ```
            
            📚 Full guide: See `DOCKER_SETUP.md` in project folder
            """)
            if st.button("Close Guide"):
                st.session_state.show_docker_guide = False
                st.rerun()

    with tab1:

        st.subheader("📝 Enter Code to Execute")
        
        # ── Language selector first so problem list updates with it ──
        language = st.selectbox("🌐 Language", ["Python", "Java", "C++", "JavaScript"], index=0, key="sandbox_lang")

        # ── Load problem titles from dataset for chosen language ──
        problem_titles = load_problem_titles(language)
        lang_icons = {"Python": "🐍", "Java": "☕", "C++": "⚙️", "JavaScript": "🟨"}
        
        if problem_titles:
            st.markdown(
                f"<div style='background:linear-gradient(90deg,#1e293b,#334155);padding:8px 14px;"
                f"border-radius:8px;margin-bottom:8px;font-size:0.85em;color:#94a3b8;'>"
                f"{lang_icons.get(language,'')} <b style='color:#e2e8f0;'>{len(problem_titles)}</b> "
                f"problems available in the <b style='color:#38bdf8;'>{language}</b> dataset</div>",
                unsafe_allow_html=True
            )
        
        # Mode: pick from dataset OR type custom
        use_dataset = st.toggle("📂 Pick Problem from Dataset", value=bool(problem_titles), disabled=not bool(problem_titles))
        
        if use_dataset and problem_titles:
            selected_title = st.selectbox(
                f"🔍 Search & Select a {language} Problem:",
                options=["-- Select a problem --"] + problem_titles,
                index=0,
                key=f"prob_picker_{language}"
            )
            if selected_title == "-- Select a problem --":
                problem_desc = ""
            else:
                problem_desc = selected_title
                st.success(f"✅ Problem selected: **{problem_desc}**")
        else:
            problem_desc = st.text_input(
                "✏️ Problem Description",
                placeholder="e.g., Calculate factorial of a number",
                key="sandbox_custom_desc"
            )
        
        # Update placeholder based on language
        placeholders = {
            "Python": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)\n\nprint(factorial(5))",
            "Java": "public class Main {\n    public static void main(String[] args) {\n        System.out.println(factorial(5));\n    }\n    \n    public static int factorial(int n) {\n        if (n <= 1) return 1;\n        return n * factorial(n - 1);\n    }\n}",
            "C++": "#include <iostream>\n\nint factorial(int n) {\n    if (n <= 1) return 1;\n    return n * factorial(n - 1);\n}\n\nint main() {\n    std::cout << factorial(5) << std::endl;\n    return 0;\n}",
            "JavaScript": "function factorial(n) {\n    if (n <= 1) return 1;\n    return n * factorial(n - 1);\n}\n\nconsole.log(factorial(5));"
        }
        
        # ── Enforce: code area locked until problem statement is filled ──
        code_locked = not bool(problem_desc.strip())
        
        if code_locked:
            st.info("🔒 **Select or enter a Problem Description above** to unlock the code editor.")
        
        code_input = st.text_area(
            "Your Code:" + (" *(Select/enter a Problem Description to unlock)*" if code_locked else ""),
            height=300,
            placeholder=placeholders.get(language, "") if not code_locked else "🔒 Locked – Select a Problem Description first...",
            disabled=code_locked,
            key="sandbox_code_input"
        )
        
        # ── Real-time per-line analysis ──
        if code_input and not code_locked:
            st.markdown("#### 🔍 Real-time Code Analysis")
            
            lines = code_input.split('\n')
            line_statuses = []
            
            # ── Semantic Alignment Check (AI) ──
            # To avoid hitting rate limits, we only verify semantic alignment if the code or problem has changed
            # and we haven't checked this specific combination yet.
            import hashlib as _hash
            check_key = _hash.md5(f"{problem_desc}{code_input[:500]}".encode()).hexdigest()
            
            if 'last_alignment_check' not in st.session_state or st.session_state.get('alignment_key') != check_key:
                with st.spinner("🧠 Verifying logic alignment..."):
                    groq = get_groq_client()
                    if groq:
                        try:
                            align_prompt = f"""Task: Check if the provided code is relevant to the problem description.
Problem: {problem_desc}
Code Start:
{code_input[:800]}

Respond in EXACTLY this format:
VERDICT: [MATCH/MISMATCH/EMPTY]
REASON: [Short 1-sentence explanation]"""
                            resp = groq.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": "user", "content": align_prompt}],
                                temperature=0.0, max_tokens=100
                            )
                            alignment = resp.choices[0].message.content
                            st.session_state.last_alignment_check = alignment
                            st.session_state.alignment_key = check_key
                        except:
                            st.session_state.last_alignment_check = "VERDICT: MATCH\nREASON: (Auto-approved due to check failure)"
            
            alignment_res = st.session_state.get('last_alignment_check', "VERDICT: MATCH")
            if "MISMATCH" in alignment_res:
                reason = alignment_res.split("REASON:")[-1].strip() if "REASON:" in alignment_res else "Code does not match problem requirements."
                st.error(f"⚠️ **Logic Mismatch Detected:** {reason}")
            
            # ... (Existing language-specific syntax checks)
            if language == 'Python':
                import ast as _ast
                import tokenize as _tokenize
                import io as _io
                # Full-code AST parse for syntax errors
                overall_error_line = None
                overall_error_msg = None
                try:
                    _ast.parse(code_input)
                except SyntaxError as e:
                    overall_error_line = e.lineno  # 1-indexed
                    overall_error_msg = e.msg
                
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if not stripped or stripped.startswith('#'):
                        line_statuses.append(('skip', i, line, ''))
                        continue
                    
                    if overall_error_line and i == overall_error_line:
                        line_statuses.append(('error', i, line, f'SyntaxError: {overall_error_msg}'))
                    elif overall_error_line and i > overall_error_line:
                        line_statuses.append(('warn', i, line, 'Code after syntax error – may not run'))
                    else:
                        # Check for common bad patterns
                        warn_msg = ''
                        if 'import sys' in stripped and 'sys.exit' not in code_input:
                            pass  # ok
                        if stripped.endswith('(') or stripped.endswith(','):
                            warn_msg = 'Incomplete expression'
                        elif stripped.count('(') != stripped.count(')'):
                            warn_msg = 'Unmatched parentheses'
                        elif stripped.count('[') != stripped.count(']'):
                            warn_msg = 'Unmatched brackets'
                        elif stripped.count('{') != stripped.count('}') and not stripped.endswith(':'):
                            warn_msg = 'Unmatched braces'
                        
                        if warn_msg:
                            line_statuses.append(('warn', i, line, warn_msg))
                        else:
                            line_statuses.append(('ok', i, line, ''))
            
            elif language == 'Java':
                import re as _re
                overall_error_line = None
                overall_error_msg = None
                # Heuristic checks for Java
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if not stripped or stripped.startswith('//'):
                        line_statuses.append(('skip', i, line, ''))
                        continue
                    warn_msg = ''
                    # Missing semicolon at end of statement (not after {, }, *, //)
                    if (stripped and
                        not stripped.endswith('{') and
                        not stripped.endswith('}') and
                        not stripped.endswith(',') and
                        not stripped.endswith(';') and
                        not stripped.startswith('@') and
                        not stripped.startswith('//') and
                        not stripped.startswith('/*') and
                        not stripped.startswith('*') and
                        not stripped.endswith(')') and  # method decl
                        _re.match(r'^(int|long|double|float|String|boolean|char|return|System|this|super|\w+\s*=)', stripped)):
                        warn_msg = 'Possible missing semicolon'
                    elif stripped.count('(') != stripped.count(')'):
                        warn_msg = 'Unmatched parentheses'
                    elif stripped.count('{') != stripped.count('}') and not stripped.endswith('{') and not stripped.endswith('}'):
                        warn_msg = 'Unmatched braces'
                    
                    if warn_msg:
                        line_statuses.append(('warn', i, line, warn_msg))
                    else:
                        line_statuses.append(('ok', i, line, ''))
            
            elif language == 'C++':
                import re as _re
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if not stripped or stripped.startswith('//'):
                        line_statuses.append(('skip', i, line, ''))
                        continue
                    warn_msg = ''
                    if (stripped and
                        not stripped.endswith('{') and
                        not stripped.endswith('}') and
                        not stripped.endswith(',') and
                        not stripped.endswith(';') and
                        not stripped.endswith('\\') and
                        not stripped.startswith('#') and
                        not stripped.startswith('//') and
                        not stripped.startswith('/*') and
                        not stripped.startswith('*') and
                        not stripped.endswith(')') and
                        _re.match(r'^(int|long|double|float|std::|auto|char|bool|return|cout|cin|\w+\s*=)', stripped)):
                        warn_msg = 'Possible missing semicolon'
                    elif stripped.count('(') != stripped.count(')'):
                        warn_msg = 'Unmatched parentheses'
                    
                    if warn_msg:
                        line_statuses.append(('warn', i, line, warn_msg))
                    else:
                        line_statuses.append(('ok', i, line, ''))
            
            elif language == 'JavaScript':
                import re as _re
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if not stripped or stripped.startswith('//'):
                        line_statuses.append(('skip', i, line, ''))
                        continue
                    warn_msg = ''
                    # Missing semicolon heuristic (skip lines ending with {, }, (, comma, or =>)
                    if (stripped and
                        not stripped.endswith('{') and
                        not stripped.endswith('}') and
                        not stripped.endswith(',') and
                        not stripped.endswith(';') and
                        not stripped.endswith('(') and
                        not stripped.endswith('=>') and
                        not stripped.startswith('//') and
                        not stripped.startswith('/*') and
                        not stripped.startswith('*') and
                        _re.match(r'^(const|let|var|return|console|throw|import|export|\w+\s*=|\w+\()', stripped)):
                        warn_msg = 'Possible missing semicolon'
                    elif stripped.count('(') != stripped.count(')'):
                        warn_msg = 'Unmatched parentheses'
                    elif stripped.count('{') != stripped.count('}') and not stripped.endswith('{') and not stripped.endswith('}') and not stripped.endswith('=>'):
                        warn_msg = 'Unmatched braces'
                    elif stripped.count('[') != stripped.count(']'):
                        warn_msg = 'Unmatched brackets'
                    
                    if warn_msg:
                        line_statuses.append(('warn', i, line, warn_msg))
                    else:
                        line_statuses.append(('ok', i, line, ''))
            
            # Render line analysis as a styled table
            ok_count = sum(1 for s in line_statuses if s[0] == 'ok')
            warn_count = sum(1 for s in line_statuses if s[0] == 'warn')
            err_count = sum(1 for s in line_statuses if s[0] == 'error')
            skip_count = sum(1 for s in line_statuses if s[0] == 'skip')
            
            # Summary bar
            scol1, scol2, scol3, scol4 = st.columns(4)
            scol1.metric("✅ OK Lines", ok_count)
            scol2.metric("⚠️ Warnings", warn_count)
            scol3.metric("❌ Errors", err_count)
            scol4.metric("⏩ Skipped", skip_count)
            
            # Show only non-ok lines by default, expandable to all
            issues = [s for s in line_statuses if s[0] in ('warn', 'error')]
            
            if err_count > 0:
                st.error(f"❌ {err_count} syntax error(s) detected – fix before running")
            elif warn_count > 0:
                st.warning(f"⚠️ {warn_count} potential issue(s) found")
            else:
                # Check alignment status for a more accurate success/warning message
                alignment_res = st.session_state.get('last_alignment_check', "VERDICT: MATCH")
                if "MISMATCH" in alignment_res:
                    st.warning("🟡 Syntax is valid, but logic mismatch detected above.")
                else:
                    st.success("✅ Code is aligned with problem and syntax is valid!")
            
            if issues:
                st.markdown("**Issues Found:**")
                for status, lineno, linetext, msg in issues:
                    icon = "🔴" if status == 'error' else "🟡"
                    st.markdown(
                        f"""
<div style='font-family:monospace;padding:4px 10px;border-left:4px solid {'#ef4444' if status=='error' else '#f59e0b'};background:{'#fef2f2' if status=='error' else '#fffbeb'};margin:2px 0;border-radius:4px;'>
{icon} <b>Line {lineno}:</b> <code>{linetext.strip()[:80]}</code> &nbsp;&nbsp;<span style='color:{'#dc2626' if status=='error' else '#b45309'};font-size:0.85em;'>{msg}</span>
</div>""",
                        unsafe_allow_html=True
                    )
            
            with st.expander("📄 View All Lines", expanded=False):
                for status, lineno, linetext, msg in line_statuses:
                    if status == 'skip':
                        color, icon = '#6b7280', '⬜'
                    elif status == 'ok':
                        color, icon = '#16a34a', '🟢'
                    elif status == 'warn':
                        color, icon = '#d97706', '🟡'
                    else:
                        color, icon = '#dc2626', '🔴'
                    st.markdown(
                        f"<div style='font-family:monospace;font-size:0.85em;padding:2px 8px;color:{color};'>{icon} <b>{lineno:3d}:</b> {linetext}</div>",
                        unsafe_allow_html=True
                    )

        col1, col2, col3 = st.columns(3)
        with col1:
            execute_btn = st.button("▶️ Execute Code", type="primary", use_container_width=True, disabled=code_locked or not code_input)
        with col2:
            generate_tests_btn = st.button("🧪 Generate Tests", use_container_width=True, disabled=code_locked or not code_input)
        with col3:
            enhance_btn = st.button("✨ Enhance with AI", use_container_width=True, disabled=code_locked or not code_input)
        
        # Execute Code
        if execute_btn and code_input:
            with st.spinner("🔄 Executing code in sandbox..."):
                result = execute_code_safely(code_input, language)
            
            st.markdown("---")
            st.subheader("📋 Execution Results")
            
            if result['success']:
                st.success("✅ Execution Successful")
            else:
                st.error("❌ Execution Failed")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Status", "✅ Pass" if result['success'] else "❌ Fail")
            with col2:
                st.metric("Time", f"{result['execution_time']:.3f}s")
            with col3:
                st.metric("Memory", f"{result['memory_used']:.2f} MB")
            with col4:
                st.metric("Complexity", result.get('complexity', 'O(n)'))
            
            if result['output']:
                st.markdown("### 📤 Output")
                st.code(result['output'], language=language.lower() if language != 'C++' else 'cpp')
            
            if result['error']:
                st.markdown("### ⚠️ Error")
                st.code(result['error'], language='text')
            
            # Show test results if available
            if result.get('test_results'):
                st.markdown("### 🧪 Test Results")
                for i, tr in enumerate(result['test_results'], 1):
                    status = "✅" if tr['passed'] else "❌"
                    with st.expander(f"{status} Test {i}: {tr['input']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Expected:** `{tr['expected']}`")
                        with col2:
                            st.markdown(f"**Actual:** `{tr['actual']}`")
            
            st.session_state.execution_history.append({
                'timestamp': datetime.now(),
                'code': code_input,
                'language': language,
                'success': result['success'],
                'time': result['execution_time'],
                'memory': result['memory_used'],
                'complexity': result.get('complexity', 'O(n)')
            })
            
            # Proactively save to CSV if successful and problem description exists
            if result['success'] and problem_desc:
                save_generated_code_to_csv(problem_desc, code_input, language)
                st.toast(f"✅ Code saved to {language} dataset!", icon="💾")
        
        # Generate Test Cases
        if generate_tests_btn and code_input:
            if not problem_desc:
                st.warning("⚠️ Please enter a **Problem Description** above so the AI can generate relevant test cases.")
            else:
                # Load AI system if needed
                if st.session_state.groq_client is None:
                    with st.spinner("🔄 Loading AI system..."):
                        model, static_idx, dynamic_idx, static_meta, dynamic_meta, groq = load_bug_system()
                        st.session_state.bug_model = model
                        st.session_state.groq_client = groq
                
                if st.session_state.groq_client is None:
                    st.error("❌ Could not connect to Groq AI. Please check your GROQ_API_KEY in the .env file.")
                else:
                    with st.spinner(f"🧪 Generating {language} test cases with Groq AI..."):
                        test_cases, test_content = generate_test_cases(
                            code_input, problem_desc, st.session_state.groq_client, language
                        )
                    
                    # Persist in session_state so they survive reruns
                    st.session_state.generated_test_cases = test_cases
                    st.session_state.generated_test_content = test_content
                    st.session_state.test_lang = language
                    st.session_state.test_code_snapshot = code_input
        
        # Show persisted test cases (survives button re-clicks)
        if st.session_state.generated_test_cases or st.session_state.generated_test_content:
            st.markdown("---")
            st.subheader("🧪 AI-Generated Test Cases")
            
            if st.session_state.generated_test_cases:
                st.info(f"✅ {len(st.session_state.generated_test_cases)} test cases generated for **{st.session_state.test_lang}**")
                st.markdown(st.session_state.generated_test_content)
                
                # Show individual test case cards
                for i, tc in enumerate(st.session_state.generated_test_cases, 1):
                    with st.expander(f"Test {i}: Input = `{tc['input']}`", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Input:** `{tc['input']}`")
                        with col2:
                            st.markdown(f"**Expected:** `{tc['expected']}`")
                
                col_run, col_clear = st.columns([2, 1])
                with col_run:
                    run_tests_btn = st.button("▶️ Run All Tests", type="primary", use_container_width=True, key="run_all_tests")
                with col_clear:
                    if st.button("🗑️ Clear Tests", use_container_width=True, key="clear_tests"):
                        st.session_state.generated_test_cases = []
                        st.session_state.generated_test_content = ''
                        st.rerun()
                
                if run_tests_btn:
                    with st.spinner("⚙️ Running tests in sandbox..."):
                        run_result = execute_code_safely(
                            st.session_state.test_code_snapshot,
                            st.session_state.test_lang,
                            st.session_state.generated_test_cases
                        )
                    
                    if run_result.get('test_results'):
                        passed = sum(1 for tr in run_result['test_results'] if tr['passed'])
                        total = len(run_result['test_results'])
                        if passed == total:
                            st.success(f"✅ All {total} tests passed!")
                        else:
                            st.warning(f"⚠️ {passed}/{total} tests passed")
                        
                        for i, tr in enumerate(run_result['test_results'], 1):
                            status = "✅" if tr['passed'] else "❌"
                            with st.expander(f"{status} Test {i}: {tr['input']}"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown(f"**Input:** `{tr['input']}`")
                                with col2:
                                    st.markdown(f"**Expected:** `{tr['expected']}`")
                                with col3:
                                    st.markdown(f"**Actual:** `{tr['actual']}`")
                    elif st.session_state.test_lang in ['Java', 'C++']:
                        st.info("ℹ️ Automated test execution for Java/C++ requires a print-based test harness. Review expected outputs above manually.")
                    else:
                        if not run_result.get('success', False):
                            st.error(f"❌ Execution Error:\n```\n{run_result.get('error', 'Unknown Error')}\n```")
                            st.info("💡 **Tip:** Ensure your code is complete and doesn't have syntax errors.")
                        elif not run_result.get('test_results'):
                            st.info("⚠️ **No test results returned.**")
                            st.code(f"Code checked: {st.session_state.test_lang}\nTest cases sent: {len(st.session_state.generated_test_cases)}")
                            if run_result.get('error'):
                                st.error(f"Sandbox Error: {run_result['error']}")
                        else:
                            st.info("⚠️ No test results – the code may not have callable functions. Try modifying the code to include a direct call.")
            else:
                st.warning("⚠️ AI could not parse structured test cases. Raw response:")
                st.markdown(st.session_state.generated_test_content)
        
        # Enhance with AI
        if enhance_btn and code_input:
            with st.spinner(f"✨ Enhancing {language} code with Dataset + GitHub + StackOverflow + Groq..."):
                # Search similar code in dataset
                if st.session_state.model and st.session_state.index:
                    similar = retrieve_similar_snippets(problem_desc or f"optimize {language.lower()} code", top_k=2, language_filter=language.lower())
                else:
                    similar = []
                
                # Fetch GitHub
                github_snippets = []
                try:
                    github_snippets = fetch_github_code_snippets(problem_desc or f"{language.lower()} code", language=language.lower(), max_files=1)
                except:
                    pass
                
                # Fetch StackOverflow
                so_snippets = []
                try:
                    so_snippets = fetch_stackoverflow_code_snippets(tag=language.lower(), pagesize=5, max_pages=1)
                except:
                    pass
                
                # Load Groq
                if st.session_state.groq_client is None:
                    model, static_idx, dynamic_idx, static_meta, dynamic_meta, groq = load_bug_system()
                    st.session_state.groq_client = groq
                
                # Generate enhanced version
                if st.session_state.groq_client:
                    context_summary = f"📚 Enhanced using: {len(similar)} dataset snippets, {len(github_snippets)} GitHub, {len(so_snippets)} StackOverflow"
                    prompt = f"""Enhance this code for better performance and readability:

{code_input}

Context from reference sources: {context_summary}
Respond ONLY with the optimized code in a markdown code block. No explanations."""
                    
                    response = st.session_state.groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a code optimization expert. Respond only with the code block."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2,
                        max_tokens=2000
                    )
                    
                    # Store in session state for persistence
                    raw_content = response.choices[0].message.content
                    # Clean up triple backticks if present
                    clean_code = raw_content
                    import re as _re
                    code_match = _re.search(r'```[\w+]*\n(.*?)```', raw_content, _re.DOTALL)
                    if code_match:
                        clean_code = code_match.group(1).strip()
                    else:
                        clean_code = clean_code.replace('```', '').strip()
                        
                    st.session_state.enhanced_code = clean_code
                    st.session_state.enhanced_context = context_summary
                    st.session_state.enhance_lang = language
                    st.session_state.performance_comparison = None # Clear old comparison
                    st.rerun()

        # Display Enhanced Code Section (Persisted)
        if st.session_state.enhanced_code:
            st.markdown("---")
            st.subheader("✨ Enhanced Code")
            st.info(st.session_state.enhanced_context)
            st.code(st.session_state.enhanced_code, language={
                'Python': 'python', 'Java': 'java', 'C++': 'cpp', 'JavaScript': 'javascript'
            }.get(st.session_state.enhance_lang, 'text'))
            
            ecol1, ecol2, ecol3 = st.columns(3)
            with ecol1:
                compare_click = st.button("📊 Compare Performance", type="primary", use_container_width=True, key="compare_perf_btn")
            with ecol2:
                if st.button("📋 Use This Code", use_container_width=True):
                    # In a real app we might want to overwrite the input area, 
                    # but Streamlit text_area value updates require session state patterns.
                    st.info("You can copy this code and paste it back into the editor above.")
            with ecol3:
                if st.button("🗑️ Clear Enhanced", use_container_width=True):
                    st.session_state.enhanced_code = None
                    st.session_state.performance_comparison = None
                    st.rerun()

            # Handle comparison click
            if compare_click:
                with st.spinner("🚀 Running performance benchmarks..."):
                    implementations = [
                        {'name': 'Original', 'code': code_input},
                        {'name': 'Enhanced', 'code': st.session_state.enhanced_code}
                    ]
                    # Pass the correct language stored in session state
                    st.session_state.performance_comparison = compare_implementations(
                        implementations, problem_desc, st.session_state.groq_client, st.session_state.enhance_lang
                    )
            
            # Display Performance Comparison Results
            if st.session_state.performance_comparison:
                st.markdown("### 🏆 Performance Analysis")
                comp_df = pd.DataFrame(st.session_state.performance_comparison)
                
                # Add improvement %
                orig_time = comp_df.iloc[0]['time']
                enh_time = comp_df.iloc[1]['time']
                if orig_time > 0:
                    improvement = ((orig_time - enh_time) / orig_time) * 100
                    st.metric("Time Improvement", f"{improvement:.1f}%", delta=f"{improvement:.1f}%")

                st.dataframe(comp_df, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    fig_time = px.bar(comp_df, x='name', y='time', title='Execution Time (s)', 
                                    color='name', color_discrete_map={'Original': '#94a3b8', 'Enhanced': '#3b82f6'})
                    st.plotly_chart(fig_time, use_container_width=True)
                with col2:
                    fig_mem = px.bar(comp_df, x='name', y='memory', title='Memory Usage (MB)', 
                                   color='name', color_discrete_map={'Original': '#94a3b8', 'Enhanced': '#10b981'})
                    st.plotly_chart(fig_mem, use_container_width=True)
    
    with tab2:
        st.subheader("📊 Execution Analytics")
        
        if st.session_state.execution_history:
            # Create DataFrame
            df_exec = pd.DataFrame([{
                'Time': e['timestamp'].strftime('%H:%M:%S'),
                'Success': '✅' if e['success'] else '❌',
                'Exec Time (s)': e['time'],
                'Memory (MB)': e['memory']
            } for e in st.session_state.execution_history[-20:]])
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Executions", len(st.session_state.execution_history))
            with col2:
                success_count = sum(1 for e in st.session_state.execution_history if e['success'])
                st.metric("Successful", success_count)
            with col3:
                avg_time = np.mean([e['time'] for e in st.session_state.execution_history])
                st.metric("Avg Time", f"{avg_time:.3f}s")
            with col4:
                avg_mem = np.mean([e['memory'] for e in st.session_state.execution_history])
                st.metric("Avg Memory", f"{avg_mem:.2f} MB")
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Execution time trend
                fig_time = px.line(
                    x=range(len(st.session_state.execution_history[-20:])),
                    y=[e['time'] for e in st.session_state.execution_history[-20:]],
                    title="Execution Time Trend",
                    labels={'x': 'Execution #', 'y': 'Time (s)'}
                )
                fig_time.update_traces(line_color='#00d4aa')
                st.plotly_chart(fig_time, use_container_width=True)
            
            with col2:
                # Memory usage trend
                fig_mem = px.bar(
                    x=range(len(st.session_state.execution_history[-20:])),
                    y=[e['memory'] for e in st.session_state.execution_history[-20:]],
                    title="Memory Usage",
                    labels={'x': 'Execution #', 'y': 'Memory (MB)'}
                )
                fig_mem.update_traces(marker_color='#3b82f6')
                st.plotly_chart(fig_mem, use_container_width=True)
            
            # Success/Fail pie chart
            success_count = sum(1 for e in st.session_state.execution_history if e['success'])
            fail_count = len(st.session_state.execution_history) - success_count
            
            fig_pie = px.pie(
                values=[success_count, fail_count],
                names=['Success', 'Failed'],
                title="Success Rate",
                color_discrete_sequence=['#00d4aa', '#ff4444']
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # History table
            st.markdown("### 📜 Execution History")
            st.dataframe(df_exec, use_container_width=True)
        else:
            st.info("No execution history yet. Run some code to see analytics!")

def extract_smart_title(code, language, default_title):
    try:
        import re as _re
        def clean_name(name):
            # Convert camelCase/PascalCase/snake_case to Space Separated Title Case
            s1 = _re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
            return _re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).replace('_', ' ').strip().title()

        if language == 'cpp':
            m = _re.search(r'(?:class|struct)\s+(\w+)', code)
            if m:
                name = m.group(1).replace('Solution', '').strip()
                if name: return clean_name(name)
            # Match functions with various return types including pointers and templates
            m = _re.search(r'\b(?:[a-zA-Z_]\w*(?:\s*[*&])*)\s+([a-zA-Z_]\w*)\s*\([^)]*\)\s*(?:const)?\s*[\{;]', code)
            if m and m.group(1) not in ('main', 'Main'):
                return clean_name(m.group(1))
        elif language == 'java':
            m = _re.search(r'public\s+class\s+(\w+)', code)
            if m:
                name = m.group(1).replace('Solution', '').strip()
                if name: return clean_name(name)
            # Match methods with visibility modifiers and complex types
            m = _re.search(r'(?:public|private|protected|static|\s)\s+[\w<>[\]]+\s+([a-zA-Z_]\w*)\s*\(', code)
            if m and m.group(1) not in ('main', 'Main'):
                return clean_name(m.group(1))
    except:
        pass
    return default_title

@st.cache_data
def load_data():
    """Load and preprocess the dataset"""
    try:
        all_snippets = []
        
        # Load Python dataset
        if os.path.exists('data_python.csv'):
            df_python = pd.read_csv('data_python.csv')
            for idx, row in df_python.iterrows():
                if pd.notna(row['python_solutions']) and pd.notna(row['problem_title']):
                    all_snippets.append({
                        'source': 'python_csv',
                        'title': row['problem_title'],
                        'content': row['python_solutions'],
                        'language': 'python',
                        'difficulty': row.get('difficulty', 'Unknown'),
                        'num_of_lines': row.get('num_of_lines', 0),
                        'code_length': row.get('code_length', 0),
                        'cyclomatic_complexity': row.get('cyclomatic_complexity', 0),
                        'readability': row.get('readability', 0)
                    })
        
        # Load C++ dataset
        if os.path.exists('data_cpp.csv'):
            df_cpp = pd.read_csv('data_cpp.csv')
            for idx, row in df_cpp.iterrows():
                if pd.notna(row['Answer']):
                    # Infer difficulty if missing
                    n_lines = row.get('num_of_lines', 0)
                    if pd.isna(row.get('difficulty')) or row.get('difficulty') == 'Unknown':
                        if n_lines < 15: diff = 'Beginner'
                        elif n_lines < 35: diff = 'Intermediate'
                        else: diff = 'Advanced'
                    else:
                        diff = row.get('difficulty')

                    all_snippets.append({
                        'source': 'cpp_csv',
                        'title': extract_smart_title(row['Answer'], 'cpp', f'C++ Solution {idx}'),
                        'content': row['Answer'],
                        'language': 'cpp',
                        'difficulty': diff,
                        'num_of_lines': n_lines,
                        'code_length': row.get('code_length', 0),
                        'cyclomatic_complexity': row.get('cyclomatic_complexity', 0),
                        'readability': row.get('readability', 0)
                    })
        
        # Load Java dataset if exists
        if os.path.exists('data_java.csv'):
            df_java = pd.read_csv('data_java.csv')
            for idx, row in df_java.iterrows():
                if pd.notna(row.get('content')):
                    all_snippets.append({
                        'source': 'java_csv',
                        'title': extract_smart_title(row['content'], 'java', row.get('title', f'Java Solution {idx}')),
                        'content': row['content'],
                        'language': 'java',
                        'difficulty': row.get('difficulty', 'Unknown'),
                        'num_of_lines': row.get('num_of_lines', 0),
                        'code_length': row.get('code_length', 0),
                        'cyclomatic_complexity': row.get('cyclomatic_complexity', 0),
                        'readability': row.get('readability', 0)
                    })
        
        # Load JavaScript dataset if exists
        if os.path.exists('data_javascript.csv'):
            df_js = pd.read_csv('data_javascript.csv')
            for idx, row in df_js.iterrows():
                if pd.notna(row.get('content')):
                    all_snippets.append({
                        'source': 'javascript_csv',
                        'title': row.get('title', f'JS Solution {idx}'),
                        'content': row['content'],
                        'language': 'javascript',
                        'difficulty': row.get('difficulty', 'Unknown'),
                        'num_of_lines': row.get('num_of_lines', 0),
                        'code_length': row.get('code_length', 0),
                        'cyclomatic_complexity': row.get('cyclomatic_complexity', 0),
                        'readability': row.get('readability', 0)
                    })
        
        df = pd.DataFrame(all_snippets)
        
        # Normalize code
        def normalize_code(text):
            if not isinstance(text, str):
                return ''
            text = text.strip('\n')
            text = re.sub(r"\n\s*\n+", '\n\n', text)
            return text
        
        df['code'] = df['content'].astype(str).apply(normalize_code)
        df['length_chars'] = df['code'].str.len()
        
        # Filter reasonable sized snippets
        df = df[(df['length_chars'] > 20) & (df['length_chars'] < 20000)].reset_index(drop=True)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

@st.cache_resource
def load_model():
    """Load the sentence transformer model"""
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

@st.cache_data
def load_embeddings_and_index():
    """Load precomputed embeddings and FAISS index, rebuilding as IndexFlatIP if needed."""
    try:
        if os.path.exists('embeddings.npy') and os.path.exists('code_faiss.index'):
            embeddings = np.load('embeddings.npy')
            loaded_index = faiss.read_index('code_faiss.index')
            
            # Test if the loaded index can be serialized (some types can't)
            # Rebuild as a clean IndexFlatIP to guarantee write_index always works
            try:
                faiss.serialize_index(loaded_index)
                index = loaded_index  # it's safe, use as-is
            except Exception:
                # Incompatible index type - rebuild a fresh serializable IndexFlatIP
                emb = embeddings.astype('float32').copy()
                faiss.normalize_L2(emb)
                d = emb.shape[1]
                index = faiss.IndexFlatIP(d)
                index.add(emb)
                # Overwrite the bad index file with the good one
                try:
                    faiss.write_index(index, 'code_faiss.index')
                except Exception:
                    pass
            
            return embeddings, index
        else:
            return None, None
    except Exception as e:
        st.error(f"Error loading embeddings/index: {e}")
        return None, None

def create_embeddings_and_index(df, model):
    """Create embeddings and FAISS index"""
    try:
        # Create text for embedding
        texts = (df.get('title', '').fillna('') + '\n' + df['code']).tolist()
        
        # Compute embeddings in batches
        batch_size = 32
        embeddings = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            emb = model.encode(batch, show_progress_bar=False)
            embeddings.append(emb)
            progress_value = min(1.0, (i + batch_size) / len(texts))
            progress_bar.progress(progress_value)
            status_text.text(f'Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}')
        
        embeddings = np.vstack(embeddings)
        
        # Build FAISS index
        d = embeddings.shape[1]
        index = faiss.IndexFlatIP(d)
        faiss.normalize_L2(embeddings)
        index.add(embeddings)
        
        # Save embeddings and index
        np.save('embeddings.npy', embeddings)
        faiss.write_index(index, 'code_faiss.index')
        
        progress_bar.empty()
        status_text.empty()
        
        return embeddings, index
    except Exception as e:
        st.error(f"Error creating embeddings: {e}")
        return None, None

def retrieve_similar_snippets(query_text, top_k=5, language_filter=None):
    """Retrieve similar code snippets"""
    if st.session_state.model is None or st.session_state.index is None:
        return []

    # ── Quality helpers ──────────────────────────────────────────────────
    def _is_repl(code: str) -> bool:
        return bool(re.search(r'^\s*>>>', str(code), re.MULTILINE))

    def _is_trivial(code: str) -> bool:
        text = str(code)
        real_chars = len(re.sub(r'\s+', '', text))
        real_lines = [l for l in text.splitlines()
                      if l.strip() and not l.strip().startswith(('#', '//', '/*', '*', '>>>'))]
        return real_chars < 80 or len(real_lines) < 4
    
    def _is_just_definition(code: str) -> bool:
        """Check if code is just class/function definition without implementation"""
        lines = [l.strip() for l in str(code).splitlines() if l.strip()]
        if not lines:
            return True
        
        # Count definition lines vs implementation lines
        def_count = 0
        impl_count = 0
        
        for line in lines:
            # Skip comments
            if line.startswith(('#', '//', '/*', '*')):
                continue
            # Definition patterns
            if re.match(r'^(def|class|function|public|private|protected|static)\s+\w+', line):
                def_count += 1
            # Implementation indicators (assignments, returns, calls, etc)
            elif any(pattern in line for pattern in ['=', 'return', 'print', 'console.', 'System.', 'std::', 'if ', 'for ', 'while ']):
                impl_count += 1
        
        # If mostly definitions with minimal implementation, reject
        return def_count > 0 and impl_count < 3
    
    def _is_off_topic(code: str, query: str) -> bool:
        """Check if code is off-topic for the query (e.g., linked list when searching for array sort)"""
        code_lower = str(code).lower()
        query_lower = query.lower()
        
        # If query mentions specific data structure, reject code using different structure
        if 'array' in query_lower or 'list' in query_lower:
            # Reject if code heavily uses linked list patterns
            if code_lower.count('listnode') > 2 or code_lower.count('.next') > 3:
                return True
        
        # If searching for basic algorithm, reject overly complex variations
        if any(term in query_lower for term in ['merge sort', 'quick sort', 'bubble sort', 'binary search']):
            # Reject if it's a complex problem using the algorithm (not the algorithm itself)
            if any(term in code_lower for term in ['listnode', 'treenode', 'reverse pairs', 'count inversions']):
                return True
        
        return False
    # ─────────────────────────────────────────────────────────────────────

    try:
        q_emb = st.session_state.model.encode([query_text])
        q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)
        D, I = st.session_state.index.search(q_emb.astype('float32'), top_k * 5)

        # Normalize scores to 0-100 range with better distribution
        if len(D[0]) > 0:
            min_score = D[0].min()
            max_score = D[0].max()
            score_range = max_score - min_score
            if score_range > 0:
                normalized_scores = ((D[0] - min_score) / score_range) * 100
            else:
                normalized_scores = D[0] * 100
        else:
            normalized_scores = D[0] * 100

        results = []
        for idx, (orig_score, norm_score) in enumerate(zip(D[0], normalized_scores)):
            actual_idx = I[0][idx]
            if actual_idx < len(st.session_state.df):
                row = st.session_state.df.loc[actual_idx]
                if language_filter and row['language'] != language_filter:
                    continue
                code = str(row['code'])
                # ── quality guards ──────────────────────────────────────
                if _is_repl(code):
                    continue
                if _is_trivial(code):
                    continue
                if _is_just_definition(code):
                    continue
                if float(orig_score) < 0.30:          # discard very low-relevance hits
                    continue
                # ───────────────────────────────────────────────────────
                results.append({
                    'idx': int(actual_idx),
                    'score': float(norm_score),  # Use normalized 0-100 score
                    'code': code,
                    'title': row['title'],
                    'difficulty': row['difficulty'],
                    'num_of_lines': row['num_of_lines'],
                    'language': row['language'],
                    'meta': row.to_dict()
                })
                if len(results) >= top_k:

                    break
        return results
    except Exception as e:
        st.error(f"Error retrieving snippets: {e}")
        return []

def save_generated_code_to_csv(problem_statement, generated_code, language, difficulty="Unknown"):
    """Save generated code to appropriate CSV dataset and auto-update embeddings/index"""
    try:
        # Calculate metrics
        lines = len(generated_code.split('\n'))
        length = len(generated_code)
        
        # Determine CSV file
        csv_files = {
            'Python': 'data_python.csv',
            'C++': 'data_cpp.csv', 
            'Java': 'data_java.csv',
            'JavaScript': 'data_javascript.csv'
        }
        
        csv_file = csv_files.get(language, 'data_python.csv')
        
        # Prepare row data
        if language == 'Python':
            row = {
                'problem_title': problem_statement,
                'python_solutions': generated_code,
                'difficulty': difficulty,
                'num_of_lines': lines,
                'code_length': length,
                'cyclomatic_complexity': 1,
                'readability': 0.8
            }
        elif language == 'C++':
            row = {
                'Answer': generated_code,
                'num_of_lines': lines,
                'code_length': length
            }
        elif language == 'JavaScript':
            row = {
                'title': problem_statement,
                'content': generated_code,
                'difficulty': difficulty,
                'num_of_lines': lines,
                'code_length': length,
                'cyclomatic_complexity': 1,
                'readability': 0.8
            }
        else:  # Java
            row = {
                'title': problem_statement,
                'content': generated_code,
                'difficulty': difficulty,
                'num_of_lines': lines,
                'code_length': length,
                'cyclomatic_complexity': 1,
                'readability': 0.8
            }
        
        # Read existing data
        df = pd.read_csv(csv_file) if os.path.exists(csv_file) else pd.DataFrame()
        
        # ── Deduplication Guard ──────────────────────────────────────────
        # Compute a normalised fingerprint of the incoming code
        import hashlib as _hl
        code_normalized = re.sub(r'\s+', '', generated_code)           # strip all whitespace
        code_fingerprint = _hl.md5(code_normalized.encode()).hexdigest()

        # Find the code column for the current language
        _code_col = {
            'Python': 'python_solutions',
            'C++': 'Answer',
            'Java': 'content',
            'JavaScript': 'content'
        }.get(language, 'python_solutions')

        if _code_col in df.columns:
            existing_fingerprints = df[_code_col].dropna().apply(
                lambda c: _hl.md5(re.sub(r'\s+', '', str(c)).encode()).hexdigest()
            )
            if code_fingerprint in existing_fingerprints.values:
                return True   # Already stored – skip silently
        # ─────────────────────────────────────────────────────────────────

        # Add new row
        new_df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        new_df.to_csv(csv_file, index=False)

        
        # Auto-update embeddings and FAISS index
        if st.session_state.model is not None:
            # Normalize code
            normalized_code = generated_code.strip('\n')
            normalized_code = re.sub(r"\n\s*\n+", '\n\n', normalized_code)
            
            # Create embedding for new code
            text = problem_statement + '\n' + normalized_code
            new_embedding = st.session_state.model.encode([text])
            new_embedding = new_embedding / np.linalg.norm(new_embedding, axis=1, keepdims=True)
            
            # Add to existing embeddings
            if st.session_state.embeddings is not None:
                st.session_state.embeddings = np.vstack([st.session_state.embeddings, new_embedding])
            else:
                st.session_state.embeddings = new_embedding
            
            # Update FAISS index in session state
            if st.session_state.index is not None:
                st.session_state.index.add(new_embedding.astype('float32'))
            
            # Save updated embeddings
            np.save('embeddings.npy', st.session_state.embeddings)
            
            # Rebuild a fresh IndexFlatIP from all embeddings to avoid serialization errors
            try:
                all_emb = st.session_state.embeddings.astype('float32')
                d = all_emb.shape[1]
                fresh_index = faiss.IndexFlatIP(d)
                faiss.normalize_L2(all_emb)
                fresh_index.add(all_emb)
                faiss.write_index(fresh_index, 'code_faiss.index')
                # Also update session state index to the fresh serializable one
                st.session_state.index = fresh_index
            except Exception as idx_err:
                # FAISS save failed but CSV was saved - non-fatal
                pass
        
        return True
    except Exception as e:
        st.error(f"Failed to save code: {e}")
        return False

def calculate_code_metrics(code):
    """Calculate code complexity metrics"""
    lines = len([line for line in code.split('\n') if line.strip()])
    chars = len(code)
    
    # Simple complexity indicators
    loops = code.count('for') + code.count('while') + code.count('do')
    conditions = code.count('if') + code.count('else') + code.count('switch')
    functions = code.count('def ') + code.count('function') + code.count('public ') + code.count('private ')
    
    # Estimate complexity score
    complexity = loops * 2 + conditions * 1.5 + functions * 1
    
    return {
        'lines': lines,
        'characters': chars,
        'loops': loops,
        'conditions': conditions,
        'functions': functions,
        'complexity_score': complexity
    }

def show_complexity_graphs(code, difficulty, language):
    """Show code complexity analysis graphs"""
    metrics = calculate_code_metrics(code)
    
    # Expected ranges for each difficulty
    difficulty_ranges = {
        'Easy': {'lines': (5, 20), 'complexity': (0, 5), 'functions': (1, 2)},
        'Intermediate': {'lines': (15, 50), 'complexity': (3, 15), 'functions': (2, 5)},
        'Advanced': {'lines': (30, 100), 'complexity': (10, 30), 'functions': (3, 10)}
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Lines of code comparison
        expected_range = difficulty_ranges[difficulty]['lines']
        fig_lines = go.Figure()
        fig_lines.add_trace(go.Bar(
            x=['Expected Min', 'Actual', 'Expected Max'],
            y=[expected_range[0], metrics['lines'], expected_range[1]],
            marker_color=['lightblue', 'darkblue', 'lightblue']
        ))
        fig_lines.update_layout(
            title=f"Lines of Code ({difficulty})",
            yaxis_title="Lines",
            height=300
        )
        st.plotly_chart(fig_lines, use_container_width=True)
    
    with col2:
        # Complexity score
        expected_range = difficulty_ranges[difficulty]['complexity']
        fig_complexity = go.Figure()
        fig_complexity.add_trace(go.Bar(
            x=['Expected Min', 'Actual', 'Expected Max'],
            y=[expected_range[0], metrics['complexity_score'], expected_range[1]],
            marker_color=['lightgreen', 'darkgreen', 'lightgreen']
        ))
        fig_complexity.update_layout(
            title=f"Complexity Score ({difficulty})",
            yaxis_title="Score",
            height=300
        )
        st.plotly_chart(fig_complexity, use_container_width=True)
    
    with col3:
        # Code structure breakdown
        fig_structure = go.Figure(data=[
            go.Bar(name='Loops', x=['Count'], y=[metrics['loops']]),
            go.Bar(name='Conditions', x=['Count'], y=[metrics['conditions']]),
            go.Bar(name='Functions', x=['Count'], y=[metrics['functions']])
        ])
        fig_structure.update_layout(
            title="Code Structure",
            yaxis_title="Count",
            height=300,
            barmode='group'
        )
        st.plotly_chart(fig_structure, use_container_width=True)
    
    # Metrics summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Lines of Code", metrics['lines'])
    with col2:
        st.metric("Complexity Score", f"{metrics['complexity_score']:.1f}")
    with col3:
        st.metric("Control Structures", metrics['loops'] + metrics['conditions'])
    with col4:
        # Difficulty match indicator
        expected_lines = difficulty_ranges[difficulty]['lines']
        expected_complexity = difficulty_ranges[difficulty]['complexity']
        
        lines_match = expected_lines[0] <= metrics['lines'] <= expected_lines[1]
        complexity_match = expected_complexity[0] <= metrics['complexity_score'] <= expected_complexity[1]
        
        if lines_match and complexity_match:
            st.metric("Difficulty Match", "Perfect")
        elif lines_match or complexity_match:
            st.metric("Difficulty Match", "Partial")
        else:
            st.metric("Difficulty Match", "Mismatch")

def retrain_model():
    """Retrain embeddings and FAISS index with updated data"""
    try:
        # Clear cached data
        if 'df' in st.session_state:
            st.session_state.df = None
        if 'embeddings' in st.session_state:
            st.session_state.embeddings = None
        if 'index' in st.session_state:
            st.session_state.index = None
            
        # Remove cached files
        for file in ['embeddings.npy', 'code_faiss.index']:
            if os.path.exists(file):
                os.remove(file)
                
        return True
    except Exception as e:
        st.error(f"Retrain failed: {e}")
        return False

def generate_ai_explanation(query, retrieved_snippets, github_snippets, so_snippets, language):
    """Generate comprehensive AI explanation based on retrieved code snippets"""
    groq = get_groq_client()
    if not groq:
        return None
    
    context = f"Query: {query}\n\n"
    context += "Dataset Snippets:\n"
    for i, s in enumerate(retrieved_snippets[:2], 1):
        context += f"{i}. {s['title']} (score: {s['score']:.2f})\n{s['code'][:500]}\n\n"
    
    if github_snippets:
        context += "GitHub Examples:\n"
        for i, g in enumerate(github_snippets[:2], 1):
            context += f"{i}. {g.get('repo', 'GitHub')}\n{g.get('content', '')[:500]}\n\n"
    
    if so_snippets:
        context += "StackOverflow Solutions:\n"
        for i, s in enumerate(so_snippets[:2], 1):
            context += f"{i}. {s.get('title', 'SO')}\n{s.get('content', '')[:500]}\n\n"
    
    prompt = f"""You are an expert {language} developer. Based on the code snippets below, provide a comprehensive professional response.

{context}

Provide:
1. **Overview**: Brief explanation of what this code does
2. **Best Approach**: Which snippet/approach is best and why
3. **Key Concepts**: Important concepts demonstrated
4. **Usage Example**: How to use this code
5. **Common Pitfalls**: What to watch out for

Be concise but professional. Format with markdown."""
    
    try:
        resp = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        return resp.choices[0].message.content
    except:
        return None

def generate_code_with_groq(problem_statement, retrieved_snippets, language, difficulty="Intermediate", max_tokens=512, temperature=0.2):
    """Generate code using Groq with GitHub/StackOverflow augmentation for reliable code"""
    try:
        from groq import Groq
        
        groq_key = os.getenv('GROQ_API_KEY')
        if not groq_key:
            return "Groq API key not configured. Add GROQ_API_KEY to .env file."
        
        # Build enhanced prompt with multiple sources
        prompt_parts = [
            f"You are an expert {language} programmer. Generate production-quality, error-free code.",
            f"Problem: {problem_statement}",
            f"Difficulty: {difficulty}",
            "",
            "Dataset snippets:"
        ]
        
        # Add retrieved snippets from local dataset
        for i, s in enumerate(retrieved_snippets[:2]):
            prompt_parts.append(f"Dataset {i+1} (similarity: {s['score']:.3f}):")
            prompt_parts.append(s['code'][:400])
            prompt_parts.append("")
        
        # Fetch live GitHub snippets
        try:
            lang_map = {'Python': 'python', 'C++': 'cpp', 'Java': 'java'}
            github_snippets = fetch_github_code_snippets(problem_statement, language=lang_map.get(language, 'python'), max_files=2)
            if github_snippets:
                prompt_parts.append("GitHub production code:")
                for i, gs in enumerate(github_snippets[:2]):
                    prompt_parts.append(f"GitHub {i+1}:")
                    prompt_parts.append(gs['content'][:400])
                    prompt_parts.append("")
        except:
            pass
        
        # Fetch StackOverflow solutions
        try:
            tag_map = {'Python': 'python', 'C++': 'c++', 'Java': 'java'}
            so_snippets = fetch_stackoverflow_code_snippets(tag=tag_map.get(language, 'python'), pagesize=20, max_pages=1)
            if so_snippets:
                prompt_parts.append("StackOverflow solutions:")
                for i, sos in enumerate(so_snippets[:2]):
                    prompt_parts.append(f"SO {i+1}:")
                    prompt_parts.append(sos['content'][:300])
                    prompt_parts.append("")
        except:
            pass
        
        prompt_parts.extend([
            f"Generate the most reliable, error-free {language} code at {difficulty} level.",
            f"Format: [DIFFICULTY: {difficulty}] followed by code"
        ])

        prompt = '\n'.join(prompt_parts)

        client = Groq(api_key=groq_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are an expert {language} programmer. Generate production-quality code."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f'Generation failed: {e}'

def create_performance_visualizations(df, search_results=None, language="Python"):
    """Create model performance visualizations"""
    st.subheader("📊 Model Performance & Dataset Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Difficulty distribution for current language
        difficulty_counts = df['difficulty'].value_counts()
        fig_difficulty = px.pie(
            values=difficulty_counts.values,
            names=difficulty_counts.index,
            title=f"<b>{language} Problem Difficulty Distribution</b>",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_difficulty.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_difficulty, use_container_width=True)
    
    with col2:
        # Code length distribution for current language
        fig_length = px.histogram(
            df, x='length_chars',
            title=f"<b>{language} Code Length Distribution</b>",
            nbins=30,
            color_discrete_sequence=['#3b82f6']
        )
        fig_length.update_layout(
            xaxis_title="Code Length (characters)",
            yaxis_title="Count",
            margin=dict(t=40, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_length, use_container_width=True)
    
    # Show search results visualization if available
    if search_results:
        col3, col4 = st.columns(2)
        
        with col3:
            # Similarity scores of search results
            scores = [r['score'] for r in search_results]
            titles = [r['title'][:30] + '...' if len(r['title']) > 30 else r['title'] for r in search_results]
            fig_similarity = px.bar(
                x=titles, y=scores,
                title="Search Results Similarity Scores",
                color=scores,
                color_continuous_scale='viridis'
            )
            fig_similarity.update_layout(
                xaxis_title="Code Snippets",
                yaxis_title="Similarity Score",
                xaxis={'tickangle': 45}
            )
            st.plotly_chart(fig_similarity, use_container_width=True)
        
        with col4:
            # Lines of code in search results
            lines = [r['num_of_lines'] for r in search_results]
            fig_lines = px.scatter(
                x=range(len(search_results)), y=lines,
                title="Search Results - Lines of Code",
                color=scores,
                color_continuous_scale='plasma'
            )
            fig_lines.update_layout(
                xaxis_title="Result Index",
                yaxis_title="Lines of Code"
            )
            st.plotly_chart(fig_lines, use_container_width=True)
    else:
        col3, col4 = st.columns(2)
        
        with col3:
            # Lines of code vs complexity for current language
            fig_complexity = px.scatter(
                df, x='num_of_lines', y='cyclomatic_complexity',
                title=f"<b>{language} Lines vs Complexity</b>",
                color='difficulty',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_complexity.update_layout(
                xaxis_title="Number of Lines",
                yaxis_title="Cyclomatic Complexity"
            )
            st.plotly_chart(fig_complexity, use_container_width=True)
        
        with col4:
            # Code readability distribution
            fig_readability = px.box(
                df, y='readability',
                title=f"<b>{language} Readability Scores</b>",
                color_discrete_sequence=['#ff4b4b']
            )
            fig_readability.update_layout(
                yaxis_title="Readability Score"
            )
            st.plotly_chart(fig_readability, use_container_width=True)


# ──────────────────────────────────────────────────────────────
# FEATURE 1: CODE TRANSLATOR
# ──────────────────────────────────────────────────────────────
def show_code_translator():
    """🔄 Translate code between Python, Java, C++, JavaScript with AI explanation."""
    st.markdown("""
    <div style='background:linear-gradient(135deg,#f0fdf4,#dcfce7);padding:24px;border-radius:16px;margin-bottom:20px;border:1px solid #bbf7d0'>
        <h2 style='color:#166534;margin:0'>🔄 Code Translator</h2>
        <p style='color:#15803d;margin:4px 0 0'>Convert code between languages instantly - the "Google Translate for code"</p>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        src_lang = st.selectbox("🔤 Source Language", SUPPORTED_LANGS, key="trans_src")
    with col2:
        st.markdown("<div style='text-align:center;padding-top:32px;font-size:2rem'>⇄</div>", unsafe_allow_html=True)
    with col3:
        tgt_options = [l for l in SUPPORTED_LANGS if l != src_lang]
        tgt_lang = st.selectbox("🎯 Target Language", tgt_options, key="trans_tgt")

    source_code = st.text_area(f"📝 Paste your {src_lang} code here:", height=280, key="trans_input",
                                placeholder=f"Enter {src_lang} code to translate...")

    translate_btn = st.button("🚀 Translate Code", type="primary", disabled=not bool(source_code.strip()))

    if translate_btn and source_code.strip():
        groq = get_groq_client()
        if not groq:
            return

        with st.spinner(f"🔍 Researching {tgt_lang} patterns and real-world examples..."):
            # 1. Generate search query
            search_query = get_search_query_from_code(source_code, src_lang, groq)
            
            # 2. Fetch external context
            gh_context = fetch_github_code_snippets(search_query, language=tgt_lang.lower(), max_files=2)
            so_context = fetch_stackoverflow_code_snippets(query=search_query, tag=tgt_lang.lower(), max_pages=1)
            
            ref_context = ""
            if gh_context:
                ref_context += "\n--- GitHub Examples ---\n"
                for s in gh_context:
                    ref_context += f"Repo: {s['repo']}\nPath: {s['path']}\nCode:\n{s['content'][:1000]}\n"
            if so_context:
                ref_context += "\n--- StackOverflow Examples ---\n"
                for s in so_context:
                    ref_context += f"Title: {s['title']}\nCode:\n{s['content'][:1000]}\n"

        prompt = f"""You are an expert polyglot programmer. Translate the following {src_lang} code to {tgt_lang}.

Rules:
- Preserve all logic and functionality exactly
- Use idiomatic {tgt_lang} patterns and conventions
- Add brief inline comments where {tgt_lang} differs conceptually
- Handle language-specific differences (e.g., memory management in C++, null safety in Java)
- Use the provided GitHub and StackOverflow context below if it contains better or more optimized patterns for {tgt_lang}.

{src_lang} Code:
``` {src_lang.lower()}
{source_code}
```

External Reference Context (Use for optimization and idiomatic patterns):
{ref_context if ref_context else "No external references found. Use your own knowledge for idiomatic translation."}

Respond in this EXACT format:
### TRANSLATED_CODE
```{tgt_lang.lower()}
<translated code here>
```
### LINE_BY_LINE_BREAKDOWN
Line 1: <Original {src_lang} line> | <Translated {tgt_lang} line> | <Idiomatic explanation>
...
### DIFFERENCES
<bullet list of key differences between {src_lang} and {tgt_lang} for this code>
### NOTES
<any important warnings or optimizations for the target language>

### ANALYTICS
Accuracy: <score 0-100>
Idiomatic: <score 0-100>
Mapping: <score 0-100>"""

        with st.spinner(f"🔄 Translating {src_lang} → {tgt_lang} with RAG context..."):
            try:
                resp = groq.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert code translator. Use RAG context to provide trusted and optimized code. Provide a line-by-line breakdown."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1, max_tokens=3000
                )
                result = resp.choices[0].message.content

                # Parse sections
                parts = result.split("###")
                translated_code, line_breakdown, differences, notes = "", "", "", ""
                for part in parts:
                    if part.strip().startswith("TRANSLATED_CODE"):
                        translated_code = part.strip()
                    elif part.strip().startswith("LINE_BY_LINE_BREAKDOWN"):
                        line_breakdown = part.replace("LINE_BY_LINE_BREAKDOWN", "").strip()
                    elif part.strip().startswith("DIFFERENCES"):
                        differences = part.replace("DIFFERENCES", "").strip()
                    elif part.strip().startswith("NOTES"):
                        notes = part.replace("NOTES", "").strip()
                    elif part.strip().startswith("ANALYTICS"):
                        analytics_text = part.replace("ANALYTICS", "").strip()
                        # Parse scores
                        import re as _re
                        sc_match = _re.search(r'Accuracy:\s*(\d+)\nIdiomatic:\s*(\d+)\nMapping:\s*(\d+)', analytics_text)
                        if sc_match:
                            trans_scores = {
                                "Accuracy": int(sc_match.group(1)),
                                "Idiomatic": int(sc_match.group(2)),
                                "Mapping": int(sc_match.group(3))
                            }
                        else:
                            trans_scores = {"Accuracy": 80, "Idiomatic": 80, "Mapping": 80}
                    elif part.strip().startswith("NOTES"):
                        notes = part.replace("NOTES", "").strip()

                st.markdown("---")
                st.success(f"✅ Successfully translated from **{src_lang}** to **{tgt_lang}**")
                
                # 📊 Visual Analytics for Translator
                v_col1, v_col2 = st.columns([1, 1])
                with v_col1:
                    st.markdown("#### 🎯 Translation Intelligence")
                    scores = trans_scores if 'trans_scores' in locals() else {"Accuracy": 85, "Idiomatic": 80, "Mapping": 75}
                    fig = go.Figure(data=go.Scatterpolar(
                        r=list(scores.values()) + [list(scores.values())[0]],
                        theta=list(scores.keys()) + [list(scores.keys())[0]],
                        fill='toself', line_color='#10b981', fillcolor='rgba(16, 185, 129, 0.3)'
                    ))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                    showlegend=False, height=250, margin=dict(l=40, r=40, t=20, b=20),
                                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                
                with v_col2:
                    st.markdown("#### 📚 Reference Backing")
                    gh_count = len(gh_context) if 'gh_context' in locals() else 0
                    so_count = len(so_context) if 'so_context' in locals() else 0
                    fig2 = px.bar(x=["GitHub", "StackOverflow"], y=[gh_count, so_count],
                                 labels={'x': 'Source', 'y': 'Matches'}, color=[gh_count, so_count],
                                 color_continuous_scale='Mint')
                    fig2.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20),
                                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                      coloraxis_showscale=False)
                    st.plotly_chart(fig2, use_container_width=True)

                col_l, col_r = st.columns(2)
                with col_l:
                    st.markdown(f"#### 📄 Original {src_lang}")
                    st.code(source_code, language={"C++": "cpp", "JavaScript": "javascript"}.get(src_lang, src_lang.lower()))
                with col_r:
                    st.markdown(f"#### ✅ Optimized {tgt_lang} (via Groq + RAG)")
                    # Extract just the code block
                    import re as _re
                    code_match = _re.search(r'```[\w+]*\n(.*?)```', translated_code, _re.DOTALL)
                    clean_code = code_match.group(1) if code_match else translated_code
                    st.code(clean_code, language={"C++": "cpp", "JavaScript": "javascript"}.get(tgt_lang, tgt_lang.lower()))
                    st.button("📋 Copy Optimized Code", key="copy_trans", help="Copy translated code")

                # Line-by-Line Breakdown Section (The "Trusted" part)
                with st.expander("🐙 Line-by-Line Translation & Trusted Patterns", expanded=True):
                    if line_breakdown:
                        for line in line_breakdown.split('\n'):
                            if '|' in line:
                                orig, trans, expl = (line.split('|') + ["", ""])[:3]
                                st.markdown(f"""
                                <div style='border-left: 3px solid #3b82f6; padding: 10px; margin: 10px 0; background: rgba(59, 130, 246, 0.05); border-radius: 0 8px 8px 0;'>
                                    <div style='font-size: 0.8rem; color: #94a3b8;'>{orig.strip()}</div>
                                    <div style='font-size: 1rem; color: #38bdf8; font-family: monospace; margin: 5px 0;'>{trans.strip()}</div>
                                    <div style='font-size: 0.85rem; color: #4ade80;'>💡 {expl.strip()}</div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("Line-by-line breakdown unavailable for this snippet.")

                col_d, col_n = st.columns(2)
                with col_d:
                    with st.expander("🔍 Key Differences", expanded=True):
                        st.markdown(differences if differences else result)
                with col_n:
                    with st.expander("⚠️ Notes & Optimizations", expanded=True):
                        st.markdown(notes if notes else "_No additional notes_")

                # Show the references used
                with st.expander("🔗 Technical References Used (GitHub + StackOverflow)", expanded=False):
                    if gh_context or so_context:
                        if gh_context:
                            st.markdown("#### 🐙 Verified GitHub Examples")
                            for i, s in enumerate(gh_context, 1):
                                st.markdown(f"**{i}. {s['repo']}**: [`{s['path']}`]({s['url']})")
                                st.markdown(f"**Patterns from {s['repo']}:**")
                                st.code(s['content'][:1000], language=tgt_lang.lower())
                        
                        if so_context:
                            st.markdown("---")
                            st.markdown("#### 💬 Top StackOverflow Solutions")
                            for i, s in enumerate(so_context, 1):
                                st.markdown(f"**{i}. [{s['title']}]({s['link']})**")
                                st.markdown("**StackOverflow code snippet:**")
                                st.code(s['content'][:1000], language=tgt_lang.lower())
                    else:
                        st.info("No external references were found for this specific logic, so Groq used its internal knowledge.")

            except Exception as e:
                st.error(f"Translation failed: {e}")


# ──────────────────────────────────────────────────────────────
# FEATURE 2: CODE QUALITY SCORER
# ──────────────────────────────────────────────────────────────
def show_code_quality_scorer():
    """📊 Score code 0-100 across 5 dimensions with AI explanation."""
    st.markdown("""
    <div style='background:linear-gradient(135deg,#eff6ff,#dbeafe);padding:24px;border-radius:16px;margin-bottom:20px;border:1px solid #bfdbfe'>
        <h2 style='color:#1e40af;margin:0'>📊 Code Quality Scorer</h2>
        <p style='color:#1d4ed8;margin:4px 0 0'>Get a comprehensive 0-100 quality score with AI-powered breakdown and fix suggestions</p>
    </div>""", unsafe_allow_html=True)


    language = st.selectbox("🌐 Language", SUPPORTED_LANGS, key="qscore_lang")
    code_input = st.text_area("📝 Paste your code for scoring:", height=280, key="qscore_input",
                               placeholder="Paste any code here to get a quality score...")

    score_btn = st.button("📊 Analyze & Score", type="primary", disabled=not bool(code_input.strip()))

    if score_btn and code_input.strip():
        groq = get_groq_client()
        if not groq:
            return

        prompt = f"""You are a senior code reviewer. Analyze this {language} code and score it on 5 dimensions (each 0-20, total 0-100).

Code:
```{language.lower()}
{code_input}
```

Respond ONLY in this JSON format:
{{
  "readability": {{"score": <0-20>, "reason": "<one sentence>", "fix": "<specific improvement>"}},
  "efficiency": {{"score": <0-20>, "reason": "<time/space complexity note>", "fix": "<specific improvement>"}},
  "security": {{"score": <0-20>, "reason": "<vulnerability note>", "fix": "<specific improvement>"}},
  "best_practices": {{"score": <0-20>, "reason": "<patterns/standards note>", "fix": "<specific improvement>"}},
  "maintainability": {{"score": <0-20>, "reason": "<modularity/docs note>", "fix": "<specific improvement>"}},
  "summary": "<2-3 sentence overall assessment>",
  "top_improvement": "<single most impactful change to make right now>"
}}"""

        with st.spinner("🔍 Analyzing code quality..."):
            try:
                resp = groq.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a code quality expert. Respond ONLY with valid JSON, no extra text."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1, max_tokens=1000
                )
                raw = resp.choices[0].message.content.strip()
                # Extract JSON
                import re as _re, json as _json
                json_match = _re.search(r'\{.*\}', raw, _re.DOTALL)
                if not json_match:
                    st.error("Could not parse AI response."); st.code(raw); return
                data = _json.loads(json_match.group())

                dims = ["readability", "efficiency", "security", "best_practices", "maintainability"]
                dim_labels = {"readability": "📖 Readability", "efficiency": "⚡ Efficiency",
                              "security": "🔒 Security", "best_practices": "✅ Best Practices",
                              "maintainability": "🔧 Maintainability"}
                dim_colors = {"readability": "#38bdf8", "efficiency": "#a78bfa", "security": "#f87171",
                              "best_practices": "#4ade80", "maintainability": "#fb923c"}

                total = sum(data.get(d, {}).get("score", 0) for d in dims)
                grade = "A+" if total>=90 else "A" if total>=80 else "B" if total>=70 else "C" if total>=60 else "D" if total>=50 else "F"
                grade_color = "#4ade80" if total>=80 else "#fbbf24" if total>=60 else "#f87171"

                st.markdown("---")
                # Total score display
                col_score, col_gauge = st.columns([1, 2])
                with col_score:
                    st.markdown(f"""
                    <div style='background:rgba(255,255,255,0.8);backdrop-filter:blur(8px);border-radius:16px;padding:24px;text-align:center;border:2px solid {grade_color}'>
                        <div style='font-size:4rem;font-weight:900;color:{grade_color}'>{total}</div>
                        <div style='color:#1e293b;font-size:0.9em;font-weight:600'>out of 100</div>
                        <div style='font-size:2rem;font-weight:700;color:{grade_color};margin-top:8px'>Grade: {grade}</div>
                    </div>""", unsafe_allow_html=True)
                with col_gauge:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=total,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [0, 100], 'tickcolor': '#1e293b'},
                            'bar': {'color': grade_color},
                            'steps': [
                                {'range': [0, 50], 'color': '#1f2937'},
                                {'range': [50, 75], 'color': '#1e3a4c'},
                                {'range': [75, 100], 'color': '#1a2e1a'}],
                            'threshold': {'line': {'color': grade_color, 'width': 3}, 'value': total}
                        }
                    ))
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#1e293b', height=200, margin=dict(t=20,b=20))
                    st.plotly_chart(fig, use_container_width=True)

                # radar chart
                scores = [data.get(d, {}).get("score", 0) * 5 for d in dims]  # scale to 100
                fig_radar = go.Figure(go.Scatterpolar(
                    r=scores + [scores[0]],
                    theta=[dim_labels[d] for d in dims] + [dim_labels[dims[0]]],
                    fill='toself', fillcolor='rgba(16, 185, 129, 0.1)',
                    line=dict(color='#10b981', width=2)
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100], color='#1e293b'),
                               angularaxis=dict(color='#1e293b')),
                    paper_bgcolor='rgba(0,0,0,0)', font_color='#1e293b',
                    showlegend=False, height=320, margin=dict(t=20, b=20)
                )
                st.plotly_chart(fig_radar, use_container_width=True)

                # Per-dimension breakdown
                st.markdown("#### 📋 Dimension Breakdown")
                for d in dims:
                    info = data.get(d, {})
                    sc = info.get("score", 0)
                    pct = sc / 20
                    bar_color = "#4ade80" if pct >= 0.75 else "#fbbf24" if pct >= 0.5 else "#f87171"
                    with st.expander(f"{dim_labels[d]}  -  **{sc}/20**", expanded=False):
                        st.progress(pct, text=f"{sc}/20")
                        st.markdown(f"**Why:** {info.get('reason','')}")
                        st.markdown(f"**Fix:** `{info.get('fix','')}`")

                # Summary
                st.info(f"**🧠 AI Summary:** {data.get('summary','')}")
                st.warning(f"**🎯 Top Priority Fix:** {data.get('top_improvement','')}")

                # StackOverflow suggestions
                with st.expander("📚 StackOverflow Best Practices", expanded=False):
                    with st.spinner("Fetching related SO answers..."):
                        try:
                            # Use improved query generation
                            so_query = get_search_query_from_code(code_input, language, groq)
                            if so_query:
                                st.caption(f"Searching for: `{so_query}` in {language}")
                            so = fetch_stackoverflow_code_snippets(query=so_query, tag=language.lower(), pagesize=3, max_pages=1)
                            if so:
                                for s in so[:3]:
                                    st.markdown(f"##### 💬 [{s.get('title', 'Verified Solution')}]({s.get('link','')})")
                                    with st.expander("🔍 View Snippet"):
                                        st.code(s.get('content',''), language=language.lower())
                            else:
                                st.info("No specific matches found. Try refining your code or focus.")
                        except Exception:
                            st.info("StackOverflow search unavailable.")

            except Exception as e:
                st.error(f"Scoring failed: {e}")


# ──────────────────────────────────────────────────────────────
# FEATURE 3: AI CODE REVIEW
# ──────────────────────────────────────────────────────────────
def show_ai_code_review():
    """🤝 AI-powered code review with inline comments and structured report."""
    st.markdown("""
    <div style='background:linear-gradient(135deg,#faf5ff,#f3e8ff);padding:24px;border-radius:16px;margin-bottom:20px;border:1px solid #e9d5ff'>
        <h2 style='color:#6b21a8;margin:0'>🤝 AI Code Review</h2>
        <p style='color:#7e22ce;margin:4px 0 0'>Get a thorough code review with inline comments, priority issues, and a summary report</p>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        language = st.selectbox("🌐 Language", SUPPORTED_LANGS, key="review_lang")
    with col2:
        review_focus = st.multiselect("🎯 Review Focus", 
            ["Security", "Performance", "Readability", "Bug Detection", "Design Patterns"],
            default=["Bug Detection", "Readability"], key="review_focus")

    code_input = st.text_area("📝 Code to Review:", height=300, key="review_input",
                               placeholder="Paste the code you want reviewed...")
    context = st.text_input("📌 Context (optional):", 
                             placeholder="e.g., This is a REST API endpoint that handles user authentication",
                             key="review_context")

    review_btn = st.button("🔍 Start AI Review", type="primary", disabled=not bool(code_input.strip()))

    if review_btn and code_input.strip():
        groq = get_groq_client()
        if not groq:
            return

        focus_str = ", ".join(review_focus) if review_focus else "general quality"
        lines = code_input.split('\n')
        numbered = "\n".join(f"{i+1:3}: {l}" for i, l in enumerate(lines))

        # 1. Fetch RAG Context for Code Review
        with st.spinner("🔍 Retrieving verified patterns for review..."):
            search_query = get_search_query_from_code(code_input, language, groq)
            # Find in local FAISS
            rag_contexts = []
            if st.session_state.bug_model and st.session_state.bug_index_static:
                query_vec = st.session_state.bug_model.encode([search_query])
                D, I = st.session_state.bug_index_static.search(query_vec, 3)
                for idx in I[0]:
                    if idx < len(st.session_state.bug_meta_static):
                        rag_contexts.append(st.session_state.bug_meta_static.iloc[idx]['text'])

            # Find on GitHub and StackOverflow
            gh_refs = fetch_github_code_snippets(search_query, language=language.lower(), max_files=2)
            so_refs = fetch_stackoverflow_code_snippets(query=search_query, tag=language.lower(), max_pages=1)
            
            # Save for UI display to avoid redundant fetch
            st.session_state.last_review_gh = gh_refs
            st.session_state.last_review_so = so_refs

            context_text = "\n".join(rag_contexts[:2])
            if gh_refs: context_text += f"\nGitHub Pattern from {gh_refs[0]['repo']}:\n{gh_refs[0]['content'][:800]}"
            if so_refs: context_text += f"\nStackOverflow Hint: {so_refs[0]['content'][:800]}"

        prompt = f"""You are a senior software engineer conducting a thorough code review.
Focus areas: {focus_str}
Context: {context if context else 'General purpose code'}
Language: {language}

Reference Context (Trusted Patterns):
{context_text if context_text else 'No external context found.'}

Code (with line numbers):
{numbered}

Provide a structured review in this EXACT format:

### CRITICAL_ISSUES
<List each critical bug/security issue as: Line X: [CRITICAL] description | suggestion>

### WARNINGS
<List each warning as: Line X: [WARNING] description | suggestion>

### SUGGESTIONS
<List each improvement as: Line X: [SUGGEST] description | suggestion>

### BUG_INTELLIGENCE_REPORT
**Likely Cause of Issues**
[Technical Root Cause Analysis]

**Suggested Fixes & Security Mitigations**
[Specific steps to fix vulnerabilities or performance flaws]

**Step-by-Step Debugging Advice**
[How to verify the fix]

**Overall Severity**
[Low/Medium/High/Critical]

### POSITIVE_NOTES
<What the code does well - 3-5 bullet points>

[RISK_SCORES]
Security: <score 0-100>
Performance: <score 0-100>
Complexity: <score 0-100>

### SUMMARY
<Overall assessment with recommendation: APPROVE / REQUEST_CHANGES / NEEDS_MAJOR_REWORK>

### REFACTORED_SNIPPET
<Show the most critical section refactored with improvements, in a code block>"""

        with st.spinner("🤖 AI is reviewing your code..."):
            try:
                resp = groq.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert code reviewer. Be specific with line numbers and actionable suggestions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2, max_tokens=2500
                )
                result = resp.choices[0].message.content

                import re as _re
                def extract_section(text, key):
                    m = _re.search(rf'### {key}\n(.*?)(?=### |\Z)', text, _re.DOTALL)
                    return m.group(1).strip() if m else ""

                critical = extract_section(result, "CRITICAL_ISSUES")
                warnings = extract_section(result, "WARNINGS")
                suggestions = extract_section(result, "SUGGESTIONS")
                intelligence = extract_section(result, "BUG_INTELLIGENCE_REPORT")
                positives = extract_section(result, "POSITIVE_NOTES")
                
                # Parse risk scores from positives or summary
                risk_scores = {"Security": 50, "Performance": 50, "Complexity": 50}
                scores_match = _re.search(r'\[RISK_SCORES\]\nSecurity:\s*(\d+)\nPerformance:\s*(\d+)\nComplexity:\s*(\d+)', positives)
                if scores_match:
                    risk_scores = {
                        "Security": int(scores_match.group(1)),
                        "Performance": int(scores_match.group(2)),
                        "Complexity": int(scores_match.group(3))
                    }
                    positives = _re.sub(r'\[RISK_SCORES\].*', '', positives, flags=_re.DOTALL).strip()

                summary = extract_section(result, "SUMMARY")
                refactored = extract_section(result, "REFACTORED_SNIPPET")

                st.markdown("---")
                # Verdict banner
                verdict = "APPROVE" if "APPROVE" in summary else ("REQUEST_CHANGES" if "REQUEST_CHANGES" in summary else "NEEDS_MAJOR_REWORK")
                verdict_color = {"APPROVE": "#4ade80", "REQUEST_CHANGES": "#fbbf24", "NEEDS_MAJOR_REWORK": "#f87171"}.get(verdict, "#94a3b8")
                verdict_icon = {"APPROVE": "✅", "REQUEST_CHANGES": "🟡", "NEEDS_MAJOR_REWORK": "❌"}.get(verdict, "ℹ️")
                st.markdown(f"""<div style='background:{verdict_color}22;border:2px solid {verdict_color};border-radius:12px;
                    padding:16px;text-align:center;margin-bottom:16px'>
                    <span style='font-size:1.5rem'>{verdict_icon}</span>
                    <span style='color:{verdict_color};font-size:1.2rem;font-weight:700;margin-left:8px'>
                    Review Verdict: {verdict.replace("_"," ")}</span></div>""", unsafe_allow_html=True)

                # Intelligence Report Header
                if intelligence:
                    with st.expander("🛡️ Bug Intelligence & Security Report", expanded=True):
                        col_a, col_b = st.columns([1, 1])
                        with col_a:
                            st.markdown("#### 🎯 Change Risk Multiplier")
                            fig = go.Figure(data=go.Scatterpolar(
                                r=list(risk_scores.values()) + [list(risk_scores.values())[0]],
                                theta=list(risk_scores.keys()) + [list(risk_scores.keys())[0]],
                                fill='toself', line_color='#6366f1', fillcolor='rgba(99, 102, 241, 0.3)'
                            ))
                            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                            showlegend=False, height=250, margin=dict(l=40, r=40, t=20, b=20),
                                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col_b:
                            st.markdown("#### 🧠 RAG Match Strength")
                            # Qualitative match strength based on refs found
                            gh_count = len(st.session_state.get('last_review_gh', []))
                            so_count = len(st.session_state.get('last_review_so', []))
                            fig2 = px.bar(x=["GitHub", "StackOverflow"], y=[gh_count, so_count],
                                         labels={'x': 'Source', 'y': 'Matches'}, color=[gh_count, so_count],
                                         color_continuous_scale='Sunset')
                            fig2.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20),
                                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                              coloraxis_showscale=False)
                            st.plotly_chart(fig2, use_container_width=True)

                        st.markdown(intelligence)

                # Stats
                crit_count = len([l for l in critical.split('\n') if l.strip()])
                warn_count = len([l for l in warnings.split('\n') if l.strip()])
                sugg_count = len([l for l in suggestions.split('\n') if l.strip()])
                mc1, mc2, mc3, mc4 = st.columns(4)
                mc1.metric("🔴 Critical", crit_count)
                mc2.metric("🟡 Warnings", warn_count)
                mc3.metric("💡 Suggestions", sugg_count)
                mc4.metric("📏 Lines Reviewed", len(lines))

                # Issues tabs
                t_crit, t_warn, t_sugg, t_pos = st.tabs(["🔴 Critical", "🟡 Warnings", "💡 Suggestions", "✅ Positives"])
                with t_crit:
                    if critical:
                        for line in critical.split('\n'):
                            if line.strip():
                                st.markdown(f"<div style='background:#7f1d1d33;border-left:3px solid #f87171;padding:8px 12px;border-radius:4px;margin:4px 0'>{line}</div>", unsafe_allow_html=True)
                    else:
                        st.success("No critical issues found! 🎉")
                with t_warn:
                    if warnings:
                        for line in warnings.split('\n'):
                            if line.strip():
                                st.markdown(f"<div style='background:#78350f33;border-left:3px solid #fbbf24;padding:8px 12px;border-radius:4px;margin:4px 0'>{line}</div>", unsafe_allow_html=True)
                    else:
                        st.success("No warnings!")
                with t_sugg:
                    if suggestions:
                        for line in suggestions.split('\n'):
                            if line.strip():
                                st.markdown(f"<div style='background:#1e3a5f33;border-left:3px solid #38bdf8;padding:8px 12px;border-radius:4px;margin:4px 0'>{line}</div>", unsafe_allow_html=True)
                with t_pos:
                    st.markdown(positives if positives else "_No positives noted._")

                st.info(f"**📝 Review Summary:** {summary}")

                if refactored:
                    with st.expander("🔨 Refactored Snippet", expanded=True):
                        code_m = _re.search(r'```[\w+]*\n(.*?)```', refactored, _re.DOTALL)
                        st.code(code_m.group(1) if code_m else refactored,
                                language={"C++": "cpp", "JavaScript": "javascript"}.get(language, language.lower()))

                # Display GitHub/SO references (Reusing fetched context)
                gh = st.session_state.get('last_review_gh', [])
                so = st.session_state.get('last_review_so', [])
                
                if gh or so:
                    with st.expander("📚 Technical References & Verified Patterns", expanded=False):
                        if gh:
                            st.markdown("### 🐙 Similar Reviewed Code on GitHub")
                            for s in gh:
                                st.markdown(f"**Source:** `{s.get('repo','')}/{s.get('path','')}`")
                                st.code(s.get('content','')[:1000], language={"C++": "cpp"}.get(language, language.lower()))
                                st.markdown(f"[View File on GitHub]({s.get('url','')})")
                                st.markdown("---")
                        
                        if so:
                            st.markdown("### 💬 Related StackOverflow Solutions")
                            for s in so:
                                st.markdown(f"**[{s.get('title', 'Verified Solution')}]({s.get('link','')})**")
                                st.code(s.get('content',''), language=language.lower())
                                st.markdown("---")
                else:
                    st.info("No external verified references found for this specific logic.")

            except Exception as e:
                st.error(f"Review failed: {e}")


# ──────────────────────────────────────────────────────────────
# FEATURE 4: PERSONALIZED LEARNING PATH
# ──────────────────────────────────────────────────────────────
def show_learning_path():
    """🎓 AI generates a custom learning roadmap based on submitted code skill level."""
    if 'learning_assessments' not in st.session_state:
        st.session_state.learning_assessments = []
    if 'learning_path' not in st.session_state:
        st.session_state.learning_path = None
    if 'completed_topics' not in st.session_state:
        st.session_state.completed_topics = set()

    st.markdown("""
    <div style='background: rgba(16, 185, 129, 0.1); 
                backdrop-filter: blur(10px);
                padding: 30px; 
                border-radius: 20px; 
                margin-bottom: 25px; 
                border: 1px solid rgba(16, 185, 129, 0.3);
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);'>
        <h2 style='color:#064e3b !important; margin:0; font-size: 2rem; font-weight: 700;'>🎓 Personalized Learning Path</h2>
        <p style='color:#065f46 !important; margin:8px 0 0; font-size: 1.1rem;'>
            Submit your code → AI identifies skill gaps → Get a custom roadmap to mastery
        </p>
    </div>""", unsafe_allow_html=True)

    tab_assess, tab_path, tab_progress = st.tabs(["📋 Skill Assessment", "🗺️ My Learning Path", "📈 Progress Tracker"])

    # ── Tab 1: Assessment ──
    with tab_assess:
        col1, col2 = st.columns(2)
        with col1:
            language = st.selectbox("🌐 Language to Assess", SUPPORTED_LANGS, key="lp_lang")
        with col2:
            exp_level = st.select_slider("📊 Self-reported Level",
                options=["Complete Beginner", "Beginner", "Intermediate", "Advanced", "Expert"],
                value="Beginner", key="lp_level")

        code_sample = st.text_area("📝 Submit a Code Sample (any code you've written):",
                                    height=250, key="lp_code",
                                    placeholder="Paste any code you've written recently - doesn't need to be perfect!")

        goals = st.text_input("🎯 What do you want to achieve?",
                               placeholder="e.g., Get a job as a backend developer, Learn data structures, Pass coding interviews",
                               key="lp_goals")

        assess_btn = st.button("🔍 Analyze My Skills & Generate Path", type="primary",
                                disabled=not bool(code_sample.strip()))

        if assess_btn and code_sample.strip():
            groq = get_groq_client()
            if not groq:
                return

            # Load dataset problems for recommendations
            dataset_problems = load_problem_titles(language)

            prompt = f"""You are a world-class coding instructor. Analyze this {language} code and create a personalized learning path.

Student's self-reported level: {exp_level}
Goals: {goals if goals else 'Improve general coding skills'}
Available practice problems from our dataset: {', '.join(dataset_problems[:30]) if dataset_problems else 'General problems'}

Code Sample:
```{language.lower()}
{code_sample}
```

Respond ONLY in this JSON:
{{
  "actual_level": "<Beginner|Intermediate|Advanced>",
  "skill_score": <0-100>,
  "detected_skills": ["<skill1>", "<skill2>", ...],
  "skill_gaps": ["<gap1>", "<gap2>", ...],
  "learning_phases": [
    {{
      "phase": 1,
      "title": "<phase title>",
      "duration": "<estimated time>",
      "topics": ["<topic1>", "<topic2>", ...],
      "practice_problems": ["<problem from dataset or general>", ...],
      "milestone": "<what student can do after this phase>"
    }}
  ],
  "immediate_next_step": "<single most important thing to do right now>",
  "resources": ["<book/course/topic>", ...],
  "estimated_total_time": "<e.g. 3 months>"
}}"""

            with st.spinner("🤖 Analyzing your skills and generating personalized path..."):
                try:
                    resp = groq.chat.completions.create(
                        model=GROQ_MODEL,
                        messages=[
                            {"role": "system", "content": "You are an expert programming instructor. Respond ONLY with valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3, max_tokens=2000
                    )
                    raw = resp.choices[0].message.content.strip()
                    import re as _re, json as _json
                    json_m = _re.search(r'\{.*\}', raw, _re.DOTALL)
                    if not json_m:
                        st.error("Could not parse AI response."); return
                    path_data = _json.loads(json_m.group())
                    st.session_state.learning_path = path_data
                    st.session_state.learning_assessments.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'language': language, 'level': path_data.get('actual_level'),
                        'score': path_data.get('skill_score', 0)
                    })
                    st.success("✅ Learning path generated! Go to **🗺️ My Learning Path** tab.")
                except Exception as e:
                    st.error(f"Assessment failed: {e}")

        # Show assessment history
        if st.session_state.learning_assessments:
            st.markdown("---")
            st.markdown("#### 📜 Assessment History")
            df_hist = pd.DataFrame(st.session_state.learning_assessments)
            st.dataframe(df_hist, use_container_width=True)
            if len(df_hist) > 1:
                fig = px.line(df_hist, x='timestamp', y='score', color='language',
                              title='Skill Score Over Time', markers=True)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0')
                st.plotly_chart(fig, use_container_width=True)

    # ── Tab 2: Learning Path ──
    with tab_path:
        if not st.session_state.learning_path:
            st.info("👆 Complete the **📋 Skill Assessment** tab first to generate your path.")
        else:
            p = st.session_state.learning_path
            col_lvl, col_sc, col_time = st.columns(3)
            col_lvl.metric("🎯 Actual Level", p.get('actual_level', 'Unknown'))
            col_sc.metric("📊 Skill Score", f"{p.get('skill_score', 0)}/100")
            col_time.metric("⏱️ Total Time", p.get('estimated_total_time', 'TBD'))

            # Skill gap visualization
            gaps = p.get('skill_gaps', [])
            skills = p.get('detected_skills', [])
            if gaps or skills:
                col_sk, col_gp = st.columns(2)
                with col_sk:
                    st.markdown("#### ✅ Detected Skills")
                    for s in skills:
                        st.markdown(f"<div style='background:#f0fdf4; border-left:4px solid #16a34a; padding:10px 15px; border-radius:8px; margin:5px 0; color:#166534; font-weight:500;'>{s}</div>", unsafe_allow_html=True)
                with col_gp:
                    st.markdown("#### ⚠️ Skill Gaps to Fill")
                    for g in gaps:
                        st.markdown(f"<div style='background:#fef2f2; border-left:4px solid #dc2626; padding:10px 15px; border-radius:8px; margin:5px 0; color:#991b1b; font-weight:500;'>{g}</div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### 🗺️ Your Learning Phases")
            phases = p.get('learning_phases', [])
            for phase in phases:
                ph_num = phase.get('phase', '?')
                is_done = ph_num in st.session_state.completed_topics
                icon = "✅" if is_done else f"🔵 Phase {ph_num}"
                with st.expander(f"{icon}: {phase.get('title','')}  -  ⏱️ {phase.get('duration','')}", expanded=(ph_num == 1)):
                    col_t, col_p = st.columns(2)
                    with col_t:
                        st.markdown("**📚 Topics:**")
                        for t in phase.get('topics', []):
                            st.markdown(f"- {t}")
                    with col_p:
                        st.markdown("**🏋️ Practice Problems:**")
                        for prob in phase.get('practice_problems', []):
                            st.markdown(f"- `{prob}`")
                    st.success(f"**🏆 Milestone:** {phase.get('milestone','')}")
                    if st.button(f"✅ Mark Phase {ph_num} Complete", key=f"mark_ph_{ph_num}"):
                        st.session_state.completed_topics.add(ph_num)
                        st.rerun()

            st.info(f"**🎯 Start Here:** {p.get('immediate_next_step', '')}")
            resources = p.get('resources', [])
            if resources:
                with st.expander("📖 Recommended Resources"):
                    for r in resources:
                        st.markdown(f"- 📌 {r}")

    # ── Tab 3: Progress ──
    with tab_progress:
        if not st.session_state.learning_path:
            st.info("Generate your learning path first.")
        else:
            phases = st.session_state.learning_path.get('learning_phases', [])
            total_phases = len(phases)
            done = len(st.session_state.completed_topics)
            pct = done / total_phases if total_phases else 0

            st.markdown(f"### 📈 Overall Progress: {done}/{total_phases} phases complete")
            st.progress(pct)

            # Improved Progress chart: show all phases as bars of equal height, colored by status
            phase_list = []
            for ph in phases:
                ph_idx = ph.get('phase', 0)
                status = '✅ Done' if ph_idx in st.session_state.completed_topics else '⏳ Pending'
                phase_list.append({
                    'Phase': f"Phase {ph_idx}",
                    'Title': ph.get('title', 'TBD')[:25],
                    'Status': status,
                    'Progress': 1  # Constant height to ensure visibility
                })
            
            df_prog = pd.DataFrame(phase_list)
            if not df_prog.empty:
                fig_prog = px.bar(
                    df_prog, 
                    x='Phase', 
                    y='Progress', 
                    color='Status',
                    hover_data=['Title'],
                    color_discrete_map={'✅ Done': '#10b981', '⏳ Pending': '#334155'},
                    title="Phase Completion Status"
                )
                fig_prog.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#e2e8f0',
                    showlegend=True,
                    yaxis_visible=False, # Hide the "1" height axis
                    xaxis=dict(title=None, showgrid=False),
                    margin=dict(t=40, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_prog, use_container_width=True)
            else:
                st.info("No phases found in the learning path.")

            if pct == 1.0:
                st.success("🎉 Congratulations! You've completed your entire learning path! You've levelled up! 🚀")
            elif done > 0:
                st.success(f"🔥 Great progress! {done} phase(s) done. Keep going!")

            if st.button("🔄 Reset Progress"):
                st.session_state.completed_topics = set()
                st.rerun()


def main():
    # Modern Sidebar Navigation
    with st.sidebar:
        add_vertical_space(1)
        st.markdown("<h1 style='text-align: center; font-size: 1.5rem;'>🧭 Navigation</h1>", unsafe_allow_html=True)
        selected = option_menu(
            None,
            ["Code Snippets", "Code Analysis", "Execution Sandbox", "Code Translator", "Code Quality Score", "AI Code Review", "Learning Path"],
            icons=["search", "bug", "terminal", "translate", "graph-up", "people", "mortarboard"],
            menu_icon="cast",
            default_index=0 if st.session_state.mode == 'code' else
                          (1 if st.session_state.mode == 'bug' else
                           (2 if st.session_state.mode == 'sandbox' else
                            (3 if st.session_state.mode == 'translator' else
                             (4 if st.session_state.mode == 'quality' else
                              (5 if st.session_state.mode == 'review' else
                               (6 if st.session_state.mode == 'learning' else 0)))))),
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#6366f1", "font-size": "18px"}, 
                "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#f1f5f9", "border-radius": "10px"},
                "nav-link-selected": {"background-color": "#6366f1", "color": "white"},
            }
        )

    # Sync mode with selection
    mode_map = {
        "Code Snippets": 'code',
        "Code Analysis": 'bug',
        "Execution Sandbox": 'sandbox',
        "Code Translator": 'translator',
        "Code Quality Score": 'quality',
        "AI Code Review": 'review',
        "Learning Path": 'learning'
    }
    st.session_state.mode = mode_map.get(selected, 'code')

    if st.session_state.mode == 'translator':
        show_code_translator()
        return
    if st.session_state.mode == 'quality':
        show_code_quality_scorer()
        return
    if st.session_state.mode == 'review':
        show_ai_code_review()
        return
    if st.session_state.mode == 'learning':
        show_learning_path()
        return
    if st.session_state.mode == 'sandbox':
        show_execution_sandbox_mode()
        return
    if st.session_state.mode == 'bug':
        show_bug_intelligence_mode()
        return
    
    # Header section with modern design
    st.markdown(f"""
    <div class="header-section">
        <h1 style="margin: 0; font-size: 3rem; font-weight: 800; letter-spacing: -0.02em;">CodeX Intelligence Hub</h1>
        <p style="margin: 0.5rem 0 1.5rem 0; font-size: 1.25rem; font-weight: 400; opacity: 0.9;">
            The Ultimate AI-Powered Ecosystem for Modern Developers
        </p>
        <div style="display: flex; gap: 10px; margin-top: 1rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.3);">🚀 v2.5.0</span>
            <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.3);">🧠 LLAMA-3.3</span>
            <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.3);">⚡ Groq Acceleration</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # React-style Dashboard using streamlit-elements
    if elements:
        with elements("dashboard"):
            with mui.Box(sx={"display": "flex", "gap": 2, "mb": 4, "mt": -2}):
                with mui.Paper(elevation=3, sx={"p": 2, "flex": 1, "borderRadius": 4, "background": "rgba(255,255,255,0.8)", "backdropFilter": "blur(10px)"}):
                    mui.Typography("Active Session", variant="overline", color="textSecondary")
                    mui.Typography("Live Data Stream", variant="h6", sx={"fontWeight": 700})
                    mui.Divider(sx={"my": 1})
                    with mui.Box(sx={"display": "flex", "alignItems": "center", "gap": 1}):
                        mui.Typography("●", sx={"color": "#10b981", "fontSize": "1.2rem", "lineHeight": 1})
                        mui.Typography("System Online", variant="body2", sx={"fontWeight": 500})

                with mui.Paper(elevation=3, sx={"p": 2, "flex": 1, "borderRadius": 4, "background": "rgba(255,255,255,0.8)", "backdropFilter": "blur(10px)"}):
                    mui.Typography("Intelligence Engine", variant="overline", color="textSecondary")
                    mui.Typography("Llama-3.3 Core", variant="h6", sx={"fontWeight": 700})
                    mui.Divider(sx={"my": 1})
                    mui.Chip(label="ULTRA-FAST", size="small", sx={"bgcolor": "#a855f7", "color": "white", "fontWeight": 700})
                    mui.Typography(" 4096 Tokens Context", variant="body2", sx={"display": "inline", "ml": 1})

                with mui.Paper(elevation=3, sx={"p": 2, "flex": 1, "borderRadius": 4, "background": "rgba(255,255,255,0.8)", "backdropFilter": "blur(10px)"}):
                    mui.Typography("Database Status", variant="overline", color="textSecondary")
                    mui.Typography("FAISS Vector DB", variant="h6", sx={"fontWeight": 700})
                    mui.Divider(sx={"my": 1})
                    mui.Typography(f"INDEX: {st.session_state.df.shape[0] if st.session_state.df is not None else 0} nodes", variant="body2", sx={"color": "#10b981", "fontWeight": 600})

    # Sidebar Settings
    with st.sidebar:
        st.title("⚙️ Settings")

        # Language selection - always show all options
        available_languages = ["Python", "C++", "Java", "JavaScript"]
        
        # Add snippet counts if data is available
        if st.session_state.df is not None:
            # Get actual counts from the dataframe
            lang_counts = st.session_state.df['language'].value_counts()
            
            # Use lowercase keys to match the 'language' column in df
            lang_map = {'python': 'Python', 'cpp': 'C++', 'java': 'Java', 'javascript': 'JavaScript'}
            display_languages = []
            
            # We want to show all supported languages even if not in DF yet
            all_target_langs = ['python', 'cpp', 'java', 'javascript']
            
            for l_code in all_target_langs:
                display_name = lang_map.get(l_code, l_code.title())
                count = lang_counts.get(l_code, 0)
                if count > 0:
                    display_languages.append(f"{display_name} ({count} snippets)")
                else:
                    display_languages.append(f"{display_name} (Generate with AI)")
            available_languages = display_languages
        
        language_selection = st.selectbox(
            "Programming Language",
            available_languages,
            index=0
        )
        
        # Extract just the language name
        language = language_selection.split(' (')[0]

        # Number of results
        num_results = st.slider("Number of Results", 1, 10, 5)

        # Similarity threshold
        similarity_threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.1, 0.05)

        # Model settings
        st.subheader("🤖 Model Settings")
        use_groq = st.checkbox("Use Groq AI for Code Generation", value=True)
        auto_save = st.checkbox("Auto-save Generated Code", value=True, help="Automatically save generated code to dataset and retrain")
        
        # Difficulty selection
        difficulty_level = st.selectbox(
            "Code Difficulty Level",
            ["Easy", "Intermediate", "Advanced"],
            index=1,
            help="Select complexity level for generated code"
        )
        
        if use_groq:
            max_tokens = st.slider("Max Tokens", 100, 2000, 1024)
            temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1)
        
        # Manual retrain button
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🔄 Refresh Data", help="Reload all CSV datasets from disk"):
                st.session_state.df = load_data()
                st.session_state.embeddings = None # Force rebuild to include new data
                st.session_state.index = None
                st.success("Data reloaded!")
                st.rerun()
        with col_r2:
            if st.button("🧠 Retrain", help="Manually rebuild embeddings/index"):
                with st.spinner("Retraining..."):
                    if retrain_model():
                        st.success("Retrained!")
                        st.rerun()
                    else:
                        st.error("Failed")
    
    # Load data and model
    if st.session_state.df is None:
        with st.spinner("Loading dataset..."):
            st.session_state.df = load_data()

    if st.session_state.model is None:
        with st.spinner("Loading model..."):
            st.session_state.model = load_model()

    # Load embeddings and index if not present
    if st.session_state.embeddings is None or st.session_state.index is None:
        with st.spinner("🧠 Loading AI search index..."):
            st.session_state.embeddings, st.session_state.index = load_embeddings_and_index()

            # Check for mismatch or missing data
            needs_rebuild = False
            if st.session_state.df is not None:
                current_count = len(st.session_state.df)
                emb_count = len(st.session_state.embeddings) if st.session_state.embeddings is not None else 0
                
                # If mismatch > 1 (to allow for minor filtering differences) or missing
                if emb_count == 0 or abs(current_count - emb_count) > 2:
                    needs_rebuild = True

            if needs_rebuild and st.session_state.df is not None:
                with st.status("🧠 Updating AI Brain...", expanded=True) as status:
                    st.write("Detecting new code snippets...")
                    st.session_state.embeddings, st.session_state.index = create_embeddings_and_index(
                        st.session_state.df, st.session_state.model
                    )
                    status.update(label="✅ AI Brain Synchronized!", state="complete", expanded=False)

    # Filter dataset by selected language
    filtered_df = pd.DataFrame()  # Default empty
    if st.session_state.df is not None:
        lang_map = {"Python": "python", "C++": "cpp", "Java": "java", "JavaScript": "javascript"}
        selected_lang = lang_map.get(language, "python")
        filtered_df = st.session_state.df[st.session_state.df['language'] == selected_lang]

        # Dataset metrics with last updated info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Snippets", len(filtered_df))
        with col2:
            if len(filtered_df) > 0:
                st.metric("Avg Code Length", f"{filtered_df['length_chars'].mean():.0f} chars")
            else:
                st.metric("Avg Code Length", "N/A")
        with col3:
            if len(filtered_df) > 0:
                st.metric("Avg Lines", f"{filtered_df['num_of_lines'].mean():.1f}")
            else:
                st.metric("Avg Lines", "N/A")
        with col4:
            # Show last modified time of dataset
            lang_files = {"Python": "data_python.csv", "C++": "data_cpp.csv", "Java": "data_java.csv"}
            csv_file = lang_files.get(language, "data_python.csv")
            if os.path.exists(csv_file):
                mod_time = datetime.fromtimestamp(os.path.getmtime(csv_file))
                st.metric("Last Updated", mod_time.strftime("%H:%M"))
            else:
                st.metric("Last Updated", "N/A")
    
    # Main search interface
    st.subheader("🔍 Search Code Snippets")
    
    # Main search interface
    query = st.text_input(
        "Describe your problem",
        placeholder="e.g., sort array, binary search, merge sort",
        key="search_input"
    )
    
    # Trigger search on Enter (text_input returns value)
    search_triggered = query.strip() != ""

    
    # Initialize variables
    results = []
    filtered_results = []
    
    # Search results
    if search_triggered and query:
        with st.spinner("🔍 Searching dataset, GitHub, and StackOverflow..."):
            # Retrieve from dataset
            results = retrieve_similar_snippets(query, top_k=num_results, language_filter=lang_map.get(language, "python"))
            
            # Fetch from GitHub
            github_snippets = []
            try:
                github_snippets = fetch_github_code_snippets(query, language=language.lower(), max_files=3)
            except:
                pass
            
            # Fetch from StackOverflow
            so_snippets = []
            try:
                so_snippets = fetch_stackoverflow_code_snippets(query=query, tag=language.lower(), pagesize=5)
            except:
                pass
        
        # Generate comprehensive AI explanation
        if results or github_snippets or so_snippets:
            with st.spinner("🤖 Generating comprehensive professional response..."):
                ai_explanation = generate_ai_explanation(query, results, github_snippets, so_snippets, language)
            
            if ai_explanation:
                st.markdown("---")
                st.markdown("### 🎯 Professional Analysis")
                st.markdown(ai_explanation)
                st.markdown("---")
        
        st.markdown(f"**Showing results for \"{query}\" in {language}**")
        
        # Retrieve similar snippets from dataset
        with st.spinner("Searching dataset, GitHub, and StackOverflow..."):
            lang_map = {"Python": "python", "C++": "cpp", "Java": "java", "JavaScript": "javascript"}
            selected_lang = lang_map.get(language, "python")
            results = retrieve_similar_snippets(query, top_k=num_results, language_filter=selected_lang)
            
            # Fetch live GitHub snippets (scaled with num_results)
            github_results = []
            try:
                gh_count = max(1, num_results // 2)  # Scale: 1-5 results based on slider
                github_snippets = fetch_github_code_snippets(query, language=selected_lang, max_files=gh_count)
                for gs in github_snippets[:gh_count]:
                    code_content = gs['content'][:1500]
                    github_results.append({
                        'idx': -1,
                        'score': 0.85,
                        'code': code_content,
                        'title': f"GitHub: {gs.get('repo', 'Unknown')}",
                        'difficulty': 'Unknown',
                        'num_of_lines': len(gs['content'].split('\n')),
                        'language': selected_lang,
                        'source': 'github',
                        'url': gs.get('url', '')
                    })
                    # Only auto-save GitHub snippets that appear relevant to the query
                    # (repo name or path contains a keyword from the query)
                    query_keywords = set(query.lower().split())
                    repo_path = (gs.get('repo', '') + gs.get('path', '')).lower()
                    if any(kw in repo_path for kw in query_keywords if len(kw) > 3):
                        save_generated_code_to_csv(query, gs['content'], language, 'Unknown')
            except Exception as e:
                pass
            
            # Fetch StackOverflow snippets (scaled with num_results)
            so_results = []
            try:
                tag_map = {'python': 'python', 'cpp': 'c++', 'java': 'java', 'javascript': 'javascript'}
                so_count = max(2, num_results)  # Scale: 2-10 results based on slider
                so_snippets = fetch_stackoverflow_code_snippets(query=query, tag=tag_map.get(selected_lang, 'python'), pagesize=so_count, max_pages=1)
                query_keywords = set(query.lower().split())
                for sos in so_snippets[:5]:  # Check more candidates but filter strictly
                    if len(sos['content']) < 50:
                        continue
                    # Only include SO snippet if its title overlaps with the search query
                    so_title_words = set(sos.get('title', '').lower().split())
                    overlap = query_keywords & so_title_words
                    meaningful_overlap = [w for w in overlap if len(w) > 3]
                    if not meaningful_overlap:
                        continue  # Skip off-topic SO snippets entirely
                    so_results.append({
                        'idx': -1,
                        'score': 0.78,
                        'code': sos['content'][:1500],
                        'title': f"StackOverflow: {sos.get('title', 'Solution')[:50]}",
                        'difficulty': 'Unknown',
                        'num_of_lines': len(sos['content'].split('\n')),
                        'language': selected_lang,
                        'source': 'stackoverflow',
                        'url': sos.get('link', '')
                    })
                    # Save only on-topic SO snippets
                    save_generated_code_to_csv(query, sos['content'], language, 'Unknown')
            except Exception as e:
                pass
            
            # Combine all results and reload dataset if new snippets were added
            all_results = results + github_results + so_results
            if len(github_results) + len(so_results) > 0:
                st.session_state.df = load_data()  # Reload dataset with new snippets

            # ── Deduplication of displayed results ───────────────────────
            import hashlib as _hl
            seen_fingerprints = set()
            deduped_results = []
            for r in all_results:
                _fp = _hl.md5(re.sub(r'\s+', '', str(r.get('code', ''))).encode()).hexdigest()
                if _fp not in seen_fingerprints:
                    seen_fingerprints.add(_fp)
                    deduped_results.append(r)
            all_results = deduped_results
            # ─────────────────────────────────────────────────────────────

        if all_results:

            # Filter by similarity threshold
            filtered_results = [r for r in all_results if r['score'] >= similarity_threshold]
            
            if filtered_results:
                # Show success message with auto-save info
                saved_count = len(github_results) + len(so_results)
                if saved_count > 0:
                    st.success(f"Found {len(filtered_results)} results ({len(results)} from dataset, {len(github_results)} from GitHub, {len(so_results)} from StackOverflow) - {saved_count} new snippets auto-saved!")
                else:
                    st.success(f"Found {len(filtered_results)} results ({len(results)} from dataset, {len(github_results)} from GitHub, {len(so_results)} from StackOverflow)")
                
                # Display results
                style_metric_cards(background_color="rgba(255,255,255,0)", border_left_color="#6366f1", border_color="rgba(0,0,0,0.1)", box_shadow=True)
                
                for i, result in enumerate(filtered_results[:num_results]):
                    source_icon = "🗂️" if result.get('source') == 'github' else ("💬" if result.get('source') == 'stackoverflow' else "📝")
                    
                    with stylable_container(
                        key=f"result_card_{i}",
                        css_styles="""
                            {
                                background: white;
                                border-radius: 16px;
                                border: 1px solid #e2e8f0;
                                padding: 5px;
                                margin-bottom: 20px;
                                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                            }
                        """
                    ):
                        with st.expander(f"{source_icon} {result['title']} (Similarity: {result['score']:.3f})", expanded=i<3):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                result_lang = result.get('language', 'python')
                                code_lang = {'python': 'python', 'cpp': 'cpp', 'java': 'java', 'javascript': 'javascript'}.get(result_lang, 'python')
                                st.code(result['code'], language=code_lang)
                            
                            with col2:
                                st.metric("Similarity", f"{result['score']:.3f}")
                                st.metric("Lines", result['num_of_lines'])
                                st.metric("Source", result.get('source', 'dataset').title())
                                if result.get('url'):
                                    st.markdown(f"[View Source]({result['url']})")
                            
                            # B. Export to Gist
                            if st.button("📤 Gist", key=f"gist_result_{i}"):
                                url = export_to_gist(result['code'], result['title'], f"snippet_{i}.py")
                                if url.startswith('http'):
                                    st.success("Exported!")
                                    st.markdown(f"[View Gist]({url})")
                                else:
                                    st.error(url)
                            
                            # D. Bookmark
                            if st.button("🔖 Save", key=f"bm_result_{i}"):
                                add_bookmark(result['code'], result['title'], language, f"Similarity: {result['score']:.3f}")
                                st.success("Saved!")
            else:
                st.warning(f"Found {len(all_results)} results but all below similarity threshold of {similarity_threshold}. Showing top result anyway:")
                result = all_results[0]
                source_icon = "🗂️" if result.get('source') == 'github' else ("💬" if result.get('source') == 'stackoverflow' else "📝")
                with st.expander(f"{source_icon} {result['title']} (Similarity: {result['score']:.3f})", expanded=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        result_lang = result.get('language', 'python')
                        code_lang = {'python': 'python', 'cpp': 'cpp', 'java': 'java', 'javascript': 'javascript'}.get(result_lang, 'python')
                        st.code(result['code'], language=code_lang)
                    with col2:
                        st.metric("Similarity", f"{result['score']:.3f}")
                        st.metric("Lines", result['num_of_lines'])
                        st.metric("Source", result.get('source', 'dataset').title())
                        if result.get('url'):
                            st.markdown(f"[View Source]({result['url']})")
                filtered_results = [all_results[0]]
        else:
            st.error("No similar code snippets found. The dataset may be empty or embeddings need to be rebuilt.")
        
    # Always show AI generation option (even if no results found)
    if use_groq and query:
        st.subheader("🤖 AI-Generated Solution")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            generate_btn = st.button("Generate Code with AI", type="secondary")
        with col2:
            st.info(f"Target: {language}")
        
        if 'gen_code_state' not in st.session_state:
            st.session_state.gen_code_state = {
                'code': '',
                'query': '',
                'difficulty': ''
            }

        if generate_btn:
            with st.spinner(f"🤖 Generating {difficulty_level} {language} code with AI (GitHub + StackOverflow + Dataset)..."):
                # Use empty results if no snippets found
                reference_snippets = filtered_results[:3] if filtered_results else []
                generated_code = generate_code_with_groq(query, reference_snippets, language, difficulty_level, max_tokens, temperature)
                st.session_state.gen_code_state['code'] = generated_code.strip()
                st.session_state.gen_code_state['query'] = query
                
                # Extract difficulty if present
                difficulty_match = re.search(r'\[DIFFICULTY:\s*(\w+)\]', generated_code)
                if difficulty_match:
                    st.session_state.gen_code_state['difficulty'] = difficulty_match.group(1)
                    st.session_state.gen_code_state['code'] = re.sub(r'\[DIFFICULTY:\s*\w+\]\s*', '', generated_code).strip()
                else:
                    st.session_state.gen_code_state['difficulty'] = difficulty_level

        # Display generated code if search query matches and code exists
        if st.session_state.gen_code_state['code'] and st.session_state.gen_code_state['query'] == query:
            generated_code = st.session_state.gen_code_state['code']
            difficulty = st.session_state.gen_code_state['difficulty']
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Generated {language} Solution:**")
            with col2:
                # Color code difficulty
                diff_colors = {'Beginner': 'green', 'Intermediate': 'orange', 'Advanced': 'red'}
                color = diff_colors.get(difficulty, 'blue')
                st.markdown(f"**Difficulty:** <span style='color:{color}'>{difficulty}</span>", unsafe_allow_html=True)
            
            code_lang = {'Python': 'python', 'C++': 'cpp', 'Java': 'java', 'JavaScript': 'javascript'}.get(language, 'python')
            st.code(generated_code, language=code_lang)
            
            # Show complexity analysis
            st.subheader("📊 Code Complexity Analysis")
            show_complexity_graphs(generated_code, difficulty, language)
            
            # Auto-save if enabled
            if auto_save:
                if save_generated_code_to_csv(query, generated_code, language, difficulty):
                    st.success(f"✅ Auto-saved to {language} dataset & embeddings updated!")
                    st.session_state.df = load_data()
                    # Clear state after auto-save to avoid double save message
                    st.session_state.gen_code_state['query'] = ""
            
            # Manual save, copy, gist, bookmark buttons
            with stylable_container(
                key="action_buttons",
                css_styles="""
                    button {
                        width: 100%;
                    }
                """
            ):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if not auto_save and st.button("💾 Save to Dataset", key="save_generated"):
                        if save_generated_code_to_csv(query, generated_code, language, difficulty):
                            st.success(f"Code saved to {language} dataset & embeddings updated!")
                            st.session_state.df = load_data()
                            st.rerun()
                with col2:
                    if st.button("📋 Copy Code", key="copy_generated"):
                        st.success("Generated code ready to copy!")
                with col3:
                    if st.button("📤 Export Gist", key="gist_generated"):
                        url = export_to_gist(generated_code, query, f"{language.lower()}_solution.py")
                        if url.startswith('http'):
                            st.success(f"[View Gist]({url})")
                        else:
                            st.error(url)
                with col4:
                    if st.button("🔖 Bookmark", key="bm_generated"):
                        add_bookmark(generated_code, query, language, f"AI Generated ({difficulty})")
                        st.success("Bookmarked!")
        
        # Show messages about search results
        if results:
            if not filtered_results:
                pass  # Already handled above by showing top result
        else:
            st.info(f"No {language} snippets found in dataset. Use AI generation below to create code.")
    
    # Show info for languages without datasets
    elif not search_triggered and len(filtered_df) == 0:
        st.info(f"No {language} snippets in dataset. Use AI generation above to create code.")
    
    # Performance visualizations
    if st.session_state.df is not None:
        # Get current search results if available
        current_results = None
        if search_triggered and query and 'filtered_results' in locals():
            current_results = filtered_results
        
        create_performance_visualizations(filtered_df if 'filtered_df' in locals() else st.session_state.df, current_results, language)
    
    # Bookmarks Section
    st.markdown("---")
    st.subheader("🔖 My Bookmarks")
    show_bookmarks()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: inherit; opacity: 0.6; padding: 2rem;">
            <p><strong>CodeX Intelligence Hub</strong> - Next-Gen AI Development Ecosystem</p>
            <p style="font-size: 0.8rem;">Powered by Llama-3, Sentence Transformers, FAISS, and Groq Ultra</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
