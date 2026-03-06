from duckduckgo_search import DDGS
import json

def get_market_trends(query: str, max_results: int = 3):
    """
    Performs a real-time search to gather market trends and in-demand skills.
    """
    results = []
    try:
        with DDGS() as ddgs:
            # Search for the query and get a few results
            ddgs_gen = ddgs.text(query, region='wt-wt', safesearch='moderate', timelimit='y')
            for i, r in enumerate(ddgs_gen):
                results.append({
                    "title": r['title'],
                    "snippet": r['body'],
                    "link": r['href']
                })
                if i >= max_results - 1:
                    break
                    
        if not results:
            return "No recent market data found for this specific query."
            
        research_summary = "\n".join([f"- {r['title']}: {r['snippet']}" for r in results])
        return research_summary
    except Exception as e:
        print(f"Market Research Error: {e}")
        return "Market research service temporarily unavailable."

if __name__ == "__main__":
    # Test
    print(get_market_trends("Fullstack Developer in-demand skills 2026"))
