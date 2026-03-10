import os
import faiss
import numpy as np
import trafilatura
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
from sentence_transformers import SentenceTransformer
from playwright.sync_api import sync_playwright

# Initialize models
try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"Failed to load sentence transformer: {e}")
    embedding_model = None

def get_search_results(query: str, max_results: int = 5) -> list[str]:
    print(f"Searching DuckDuckGo for: {query}")
    urls = []
    try:
        results = DDGS().text(query, max_results=max_results)
        for r in results:
            if 'href' in r:
                urls.append(r['href'])
    except Exception as e:
        print(f"DDGS error: {e}")
    return urls

def scrape_pages(urls: list[str]) -> str:
    combined_text = ""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
            page = context.new_page()
            page.set_default_timeout(10000)
            
            for url in urls:
                try:
                    print(f"Scraping: {url}")
                    page.goto(url)
                    html = page.content()
                    text = trafilatura.extract(html)
                    if text:
                        combined_text += f"\n\nSource: {url}\n{text}"
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
            
            browser.close()
    except Exception as e:
        print(f"Playwright error: {e}")
    
    return combined_text

def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

def retrieve_context(query: str, combined_text: str, top_k: int = 4) -> str:
    if not combined_text.strip() or embedding_model is None:
        return ""
    
    chunks = chunk_text(combined_text)
    if not chunks:
        return ""

    try:
        # Embed chunks
        chunk_embeddings = embedding_model.encode(chunks)
        
        # Build FAISS index
        dimension = chunk_embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(chunk_embeddings).astype('float32'))
        
        # Embed query and search
        query_embedding = embedding_model.encode([query])
        distances, indices = index.search(np.array(query_embedding).astype('float32'), top_k)
        
        # Retrieve texts
        relevant_chunks = []
        for idx in indices[0]:
            if idx != -1 and idx < len(chunks):
                relevant_chunks.append(chunks[idx])
        
        return "\n\n... ".join(relevant_chunks)
    except Exception as e:
        print(f"RAG Retrieval Error: {e}")
        return ""

def generate_rag_context(topic: str, subtopic: str, domain: str) -> str:
    query = f"{subtopic} in {topic} for {domain} architecture detailed explanation"
    urls = get_search_results(query, max_results=5)
    if not urls:
        return ""
    
    scraped_text = scrape_pages(urls)
    
    # Retrieve relevant parts
    relevant_context = retrieve_context(query, scraped_text, top_k=5)
    return relevant_context
