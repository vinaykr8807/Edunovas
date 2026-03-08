import os
import requests

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def get_pexels_image(query, page=1):
    if not PEXELS_API_KEY:
        return None
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 1, "page": page}
    try:
        r = requests.get(url, headers=headers, params=params)
        data = r.json()
        if data.get("photos"):
            return data["photos"][0]["src"]["large"]
    except:
        pass
    return None

def get_pexels_video(query, page=1):
    # Fallback to YouTube for sound and longer duration as requested
    return get_youtube_video(query)

def get_youtube_video(query):
    """Search YouTube and return an embed URL."""
    try:
        import urllib.request
        import re
        search_query = query.replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={search_query}+tutorial+educational"
        
        # User agent to avoid blocks
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            html = response.read().decode()
            video_ids = re.findall(r"watch\?v=(\S{11})", html)
            if video_ids:
                return f"https://www.youtube.com/embed/{video_ids[0]}"
    except Exception as e:
        print(f"YouTube search error: {e}")
    return None
