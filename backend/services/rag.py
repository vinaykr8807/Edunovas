import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize the model (L6 is fast and small)
print("🚀 Loading RAG Knowledge Model...")
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except:
    print("⚠️ RAG Model failed to load.")
    model = None

# In-memory document store
DOC_STORE = []
INDEX = None
DIMENSION = 384 # For all-MiniLM-L6-v2

def initialize_knowledge_base():
    global INDEX, DOC_STORE
    
    # Sample Knowledge Data
    sample_data = [
        {"text": "B-Trees are self-balancing search trees commonly used in databases.", "source": "Lesson: Data Structures"},
        {"text": "A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble an image.", "source": "Lesson: DevOps"},
        {"text": "Interview Tips: Always explain your brute-force solution first before optimizing to O(n) or O(log n).", "source": "Interview Prep"},
        {"text": "RESTful APIs use HTTP requests to GET, PUT, POST and DELETE data. They are stateless.", "source": "Lesson: Backend"},
    ]
    
    DOC_STORE = sample_data
    texts = [d['text'] for d in sample_data]
    
    if model:
        embeddings = model.encode(texts)
        INDEX = faiss.IndexFlatL2(DIMENSION)
        INDEX.add(np.array(embeddings).astype('float32'))
        print(f"✅ Knowledge base initialized with {len(texts)} documents.")

def search_knowledge(query, top_k=3):
    if not model or not INDEX or not DOC_STORE:
        return []
        
    query_vec = model.encode([query])
    D, I = INDEX.search(np.array(query_vec).astype('float32'), top_k)
    
    results = []
    for idx in I[0]:
        if idx != -1 and idx < len(DOC_STORE):
            results.append(DOC_STORE[idx])
            
    return results

def inject_rag_context(prompt, query):
    knowledge = search_knowledge(query)
    if not knowledge: return prompt
    
    context_str = "\n".join([f"- {k['text']} (Source: {k['source']})" for k in knowledge])
    
    rag_prompt = f"""
    CONTEXT FROM EDUNOVAS KNOWLEDGE BASE:
    {context_str}
    
    ---
    
    Using the context above (if relevant), please address the following user query.
    
    USER QUERY: {query}
    """
    return rag_prompt

# Initial run
initialize_knowledge_base()
