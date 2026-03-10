try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
import json

def get_market_trends(query: str, max_results: int = 3):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            return results
    except Exception as e:
        print(f"Error fetching trends: {e}")
        return []
