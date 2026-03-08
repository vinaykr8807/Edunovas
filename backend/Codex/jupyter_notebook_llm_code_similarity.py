# Jupyter-ready Python script (cells separated by '# %%')
# Notebook: Build dataset from GitHub + StackOverflow, create embeddings, index with FAISS,
# retrieve relevant code snippets and generate code with Ollama, evaluate similarity.

# %%
# 1) Prerequisites (run in a notebook cell)
# !pip install requests pandas beautifulsoup4 sentence-transformers faiss-cpu tqdm python-dotenv

# %%
# 2) Configuration: Use environment variables for secrets
import os
from dotenv import load_dotenv
load_dotenv()  # optional .env file support

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')      # set this to your GitHub PAT
STACK_KEY = os.getenv('STACK_KEY')            # set this to your StackExchange key (optional but recommended)
GROQ_API_KEY = os.getenv('GROQ_API_KEY')      # Groq API key for LLM generation

# Basic checks
print('GitHub token present?', bool(GITHUB_TOKEN))
print('Stack key present?', bool(STACK_KEY))
print('Groq API key present?', bool(GROQ_API_KEY))

# %%
# 3) Helper functions: GitHub API & StackExchange API collectors
import requests
import time
from tqdm import tqdm
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {'Accept': 'application/vnd.github.v3+json'}
if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'


def fetch_github_code_snippets(query, language=None, max_files=200):
    """Search public code on GitHub matching query and language.
    NOTE: GitHub Search API has rate-limits and different behavior for code search.
    This function uses the code search endpoint. Return list of dicts: {source, repo, path, url, content, language}
    """
    items = []
    per_page = 30
    page = 1
    fetched = 0
    q = query
    if language:
        q += f' language:{language}'

    while fetched < max_files:
        url = f'https://api.github.com/search/code?q={requests.utils.quote(q)}&per_page={per_page}&page={page}'
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            print('GitHub search error', r.status_code, r.text[:200])
            break
        resp = r.json()
        results = resp.get('items', [])
        if not results:
            break
        for item in results:
            if fetched >= max_files:
                break
            # Fetch raw content via contents API
            try:
                download_url = item.get('html_url').replace('https://github.com', 'https://raw.githubusercontent.com')
                # html_url: https://github.com/user/repo/blob/branch/path -> raw: https://raw.githubusercontent.com/user/repo/branch/path
                # naive conversion: replace '/blob/' with '/'
                download_url = download_url.replace('/blob/', '/')
                cr = requests.get(download_url, headers=HEADERS, timeout=10)
                if cr.status_code == 200:
                    content = cr.text
                    items.append({
                        'source': 'github',
                        'repo': item.get('repository', {}).get('full_name'),
                        'path': item.get('path'),
                        'url': item.get('html_url'),
                        'content': content,
                        'language': item.get('language') or language
                    })
                    fetched += 1
            except Exception as e:
                # skip problematic files
                continue
        # paging
        page += 1
        # respect rate limits
        time.sleep(1)
    return items


def fetch_stackoverflow_code_snippets(tag=None, pagesize=100, max_pages=5):
    """Fetch answers from StackOverflow and extract code blocks from answers.
    Returns list of dicts: {source, question_id, answer_id, title, link, code}
    """
    base = 'https://api.stackexchange.com/2.3'
    page = 1
    snippets = []
    while page <= max_pages:
        params = {
            'order': 'desc',
            'sort': 'activity',
            'site': 'stackoverflow',
            'pagesize': pagesize,
            'page': page,
            'filter': 'withbody'
        }
        if STACK_KEY:
            params['key'] = STACK_KEY
        if tag:
            params['tagged'] = tag
        url = f"{base}/questions"
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print('Stack API error', r.status_code, r.text[:200])
            break
        data = r.json()
        for q in data.get('items', []):
            question_id = q['question_id']
            title = q.get('title')
            link = q.get('link')
            # fetch answers
            ar = requests.get(f"{base}/questions/{question_id}/answers", params={'order':'desc','sort':'votes','site':'stackoverflow','filter':'withbody', **({'key': STACK_KEY} if STACK_KEY else {})})
            if ar.status_code != 200:
                continue
            answers = ar.json().get('items', [])
            for a in answers:
                body = a.get('body', '')
                soup = BeautifulSoup(body, 'html.parser')
                code_blocks = [c.get_text() for c in soup.find_all('code')]
                for cb in code_blocks:
                    snippets.append({
                        'source':'stackoverflow',
                        'question_id': question_id,
                        'answer_id': a.get('answer_id'),
                        'title': title,
                        'link': link,
                        'content': cb
                    })
        if not data.get('has_more'):
            break
        page += 1
        time.sleep(1)
    return snippets

# %%
# 4) Load existing CSV datasets for training
# Load Python and C++ code snippets from CSV files

print('Loading Python dataset...')
df_python = pd.read_csv('data_python.csv')
print(f'Python dataset shape: {df_python.shape}')
print('Python columns:', df_python.columns.tolist())

print('Loading C++ dataset...')
df_cpp = pd.read_csv('data_cpp.csv')
print(f'C++ dataset shape: {df_cpp.shape}')
print('C++ columns:', df_cpp.columns.tolist())

# Prepare Python dataset
python_snippets = []
for idx, row in df_python.iterrows():
    if pd.notna(row['python_solutions']) and pd.notna(row['problem_title']):
        python_snippets.append({
            'source': 'python_csv',
            'title': row['problem_title'],
            'content': row['python_solutions'],
            'language': 'python',
            'difficulty': row.get('difficulty', 'Unknown'),
            'num_of_lines': row.get('num_of_lines', 0),
            'code_length': row.get('code_length', 0)
        })

# Prepare C++ dataset
cpp_snippets = []
for idx, row in df_cpp.iterrows():
    if pd.notna(row['Answer']):
        cpp_snippets.append({
            'source': 'cpp_csv',
            'title': f'C++ Solution {idx}',
            'content': row['Answer'],
            'language': 'cpp',
            'num_of_lines': row.get('num_of_lines', 0),
            'code_length': row.get('code_length', 0)
        })

# Combine datasets
collected = python_snippets + cpp_snippets
print(f'Total snippets collected: {len(collected)}')
print(f'Python snippets: {len(python_snippets)}')
print(f'C++ snippets: {len(cpp_snippets)}')

# Create combined DataFrame
df = pd.DataFrame(collected)
print('Combined dataset columns:', df.columns.tolist())

# Save combined dataset
out_path = 'code_snippets_dataset.csv'
df.to_csv(out_path, index=False)
print('Saved combined dataset to', out_path)

# %%
# 5) Preprocessing: normalize code (strip leading/trailing whitespace), keep short snippets, language tag
import re

def normalize_code(text):
    # remove trailing whitespace, unify line endings
    if not isinstance(text, str):
        return ''
    text = text.strip('\n')
    # replace multiple blank lines with single
    text = re.sub(r"\n\s*\n+", '\n\n', text)
    return text

if 'content' in df.columns:
    df['code'] = df['content'].astype(str).apply(normalize_code)
    df['length_chars'] = df['code'].str.len()
    # keep only reasonable sized snippets
    df = df[(df['length_chars'] > 20) & (df['length_chars'] < 20000)].reset_index(drop=True)
    print('After length filter', len(df))
    df.to_csv('code_snippets_preprocessed.csv', index=False)

# %%
# 6) Create embeddings for snippets using sentence-transformers
from sentence_transformers import SentenceTransformer
import numpy as np

model_name = 'all-MiniLM-L6-v2'  # small and fast; good for semantic similarity
embed_model = SentenceTransformer(model_name)

# Create text for embedding: combine title/context + code
texts = (df.get('title', '').fillna('') + '\n' + df['code']).tolist()

# Compute embeddings in batches
batch_size = 32
embeddings = []
for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    emb = embed_model.encode(batch, show_progress_bar=False)
    embeddings.append(emb)
embeddings = np.vstack(embeddings)
print('Embeddings shape:', embeddings.shape)

# Save embeddings
np.save('embeddings.npy', embeddings)

# %%
# 7) Build FAISS index for nearest-neighbor search
try:
    import faiss
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)  # inner product (cosine if vectors normalized)
    # normalize embeddings
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    faiss.write_index(index, 'code_faiss.index')
    print('FAISS index built, total vectors:', index.ntotal)
except Exception as e:
    print('FAISS not available or error:', e)

# %%
# 8) Helper: retrieve top-k similar snippets for a query
import numpy as np

# ensure we have index and normalized embeddings

def retrieve_similar_snippets(query_text, top_k=5):
    q_emb = embed_model.encode([query_text])
    # normalize
    q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)
    D, I = index.search(q_emb.astype('float32'), top_k)
    results = []
    for idx, score in zip(I[0], D[0]):
        results.append({'idx': int(idx), 'score': float(score), 'code': df.loc[idx, 'code'], 'meta': df.loc[idx].to_dict()})
    return results

# %%
# 9) Generate code using Groq with retrieved context as RAG
from groq import Groq

def generate_code_with_groq(problem_statement, retrieved_snippets, max_tokens=512, temperature=0.2):
    if not GROQ_API_KEY:
        raise RuntimeError('GROQ_API_KEY not configured')
    
    # Build prompt with retrieved snippets + fetch live GitHub/StackOverflow examples
    prompt_parts = [
        "Use the following code snippets as references. Synthesize the most reliable, error-free solution.",
        f"Problem: {problem_statement}",
        "\nRetrieved snippets from dataset:"
    ]
    
    # Add retrieved snippets from local dataset
    for i, s in enumerate(retrieved_snippets[:3]):
        prompt_parts.append(f"--- Dataset snippet {i+1} (score={s['score']:.4f}) ---\n{s['code']}\n")
    
    # Fetch live GitHub snippets
    try:
        github_snippets = fetch_github_code_snippets(problem_statement, max_files=3)
        if github_snippets:
            prompt_parts.append("\nLive GitHub examples (production code):")
            for i, gs in enumerate(github_snippets[:2]):
                prompt_parts.append(f"--- GitHub {i+1} ({gs.get('repo', 'unknown')}) ---\n{gs['content'][:500]}\n")
    except:
        pass
    
    # Fetch live StackOverflow snippets
    try:
        so_snippets = fetch_stackoverflow_code_snippets(tag='python', pagesize=30, max_pages=1)
        if so_snippets:
            prompt_parts.append("\nStackOverflow solutions (verified answers):")
            for i, sos in enumerate(so_snippets[:2]):
                prompt_parts.append(f"--- SO {i+1} ---\n{sos['content'][:300]}\n")
    except:
        pass
    
    prompt_parts.append('\nGenerate the most reliable, error-free code based on these references. Provide only the solution code and brief explanation.')
    
    prompt = '\n'.join(prompt_parts)
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert programmer. Generate production-quality, error-free code based on multiple reliable sources."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f'Groq generation error: {e}')

# %%
# 10) Example: end-to-end: provide problem statement, retrieve, generate
problem = "Write a Python function to perform binary search on a sorted list of integers that returns the index of the target or -1 if not found."
retrieved = retrieve_similar_snippets(problem, top_k=5)
print('Retrieved top snippet scores:', [r['score'] for r in retrieved])

# Generate (this will call Groq API)
try:
    gen = generate_code_with_groq(problem, retrieved)
    print('Generation result (raw):')
    print(gen)
except Exception as e:
    print('Generation error:', e)

# %%
# 11) Evaluation strategy (automated)
# - Exact match vs reference (if you have ground-truth solutions)
# - BLEU / ROUGE on tokens between generated code and references
# - Semantic similarity: embed generated code and compare with top retrieved/reference embeddings
# - (Optional) Run unit tests: create small test harness (safer to sandbox)

from sklearn.metrics import pairwise_distances
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

smooth = SmoothingFunction().method4

def bleu_score(ref_code, gen_code):
    # naive tokenization by whitespace
    ref_tokens = ref_code.split()
    gen_tokens = gen_code.split()
    return sentence_bleu([ref_tokens], gen_tokens, smoothing_function=smooth)

# Example: if you have ground truth
# ground_truth = 'def binary_search(...): ...'
# gen_text = extract text from generation response

# Semantic similarity evaluation

def semantic_similarity(a_text, b_text):
    a_emb = embed_model.encode([a_text])
    b_emb = embed_model.encode([b_text])
    a_emb = a_emb / np.linalg.norm(a_emb)
    b_emb = b_emb / np.linalg.norm(b_emb)
    return float(np.dot(a_emb, b_emb.T))

# %%
# 12) Putting it together: a function to produce final code + top-k similar snippets and scores

def produce_solution(problem_statement, lang_hint=None, top_k=5):
    query_text = (problem_statement + (f' language:{lang_hint}' if lang_hint else ''))
    retrieved = retrieve_similar_snippets(query_text, top_k=top_k)
    try:
        gen_text = generate_code_with_groq(problem_statement, retrieved)
    except Exception as e:
        gen_text = f'Generation failed: {e}'

    return {'problem': problem_statement, 'generated': gen_text, 'retrieved': retrieved}

# %%
# 13) Environment testing and validation
def test_environment():
    """Test all components of the environment setup"""
    print("=== Environment Test ===")
    
    # Test 1: Environment variables
    print(f"✓ GitHub token loaded: {bool(GITHUB_TOKEN)}")
    print(f"✓ StackOverflow API key loaded: {bool(STACK_KEY)}")
    print(f"✓ Groq API key loaded: {bool(GROQ_API_KEY)}")
    
    # Test 2: CSV files
    try:
        df_python = pd.read_csv('data_python.csv')
        df_cpp = pd.read_csv('data_cpp.csv')
        print(f"✓ Python CSV loaded: {df_python.shape[0]} rows")
        print(f"✓ C++ CSV loaded: {df_cpp.shape[0]} rows")
    except Exception as e:
        print(f"✗ CSV loading failed: {e}")
        return False
    
    # Test 3: Groq API connection
    try:
        from groq import Groq
        if GROQ_API_KEY:
            client = Groq(api_key=GROQ_API_KEY)
            # Test with a simple request
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            print(f"✓ Groq API connection successful")
            print(f"✓ Model: llama-3.3-70b-versatile")
        else:
            print(f"✗ Groq API key not configured")
            return False
    except Exception as e:
        print(f"✗ Groq API test failed: {e}")
        return False
    
    print("=== Environment Test Complete ===")
    return True

# Run environment test
test_environment()

# %%
# 14) Notes and next steps
# - This notebook uses RAG (retrieve + generate) with Groq API for code generation.
# - For embeddings, you can swap to larger models (e.g., all-mpnet-base-v2) if you need better semantic quality.
# - For evaluation, consider building a small set of held-out problem->reference pairs and running unit tests
#   (execute the generated code in a sandboxed subprocess or separate environment).

# End of notebook
