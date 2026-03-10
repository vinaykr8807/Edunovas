import asyncio
import sys
import os

# Add the parent directory to sys.path so we can import modules from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import supabase
from datetime import datetime, timezone
from services.career_pathfinder import _search_jobs_multi_source
from services.notification_service import notification_service

def run_job_crawler_task():
    """Manually trigger the background crawler to find jobs for all active subscribers."""
    try:
        print("🔍 [Crawler] Fetching active subscribers...")
        subs = supabase.table('job_notifications').select('*, users(email)').eq('is_active', True).execute()
        if not subs.data:
            print("ℹ️ [Crawler] No active subscribers found.")
            return {"success": True, "message": "No active subscribers."}
            
        print(f"👥 [Crawler] Found {len(subs.data)} active subscribers.")
        notifications_sent: int = 0
        for sub in subs.data:
            user_id = sub['user_id']
            user_email = sub['users']['email']
            role = sub['role']
            city = sub['city']
            min_score = sub['min_score']
            
            print(f"👤 [Crawler] Processing {user_email} (Role: {role}, City: {city})...")
            
            # Fetch user's latest resume to extract skills
            resume_res = supabase.table('student_profiles').select('skills').eq('user_id', user_id).execute()
            user_skills = resume_res.data[0]['skills'] if resume_res.data and resume_res.data[0].get('skills') else []
            
            print(f"🔎 [Crawler] Searching jobs for {role} in {city}...")
            jobs = _search_jobs_multi_source(role, "Mid-Level", city, user_skills)
            print(f"🎯 [Crawler] Found {len(jobs)} potential matches for {user_email}.")
            
            high_matches = []
            for job in jobs:
                score = job.get('suitability_score', 0)
                link = job.get('link', '')
                if score >= min_score and link:
                    if not notification_service.was_notified(supabase, user_id, link):
                        high_matches.append(job)
                        notification_service.record_match(supabase, user_id, link, score)
                        
            if high_matches:
                print(f"✉️ [Crawler] Sending {len(high_matches)} notifications to {user_email}...")
                if notification_service.send_job_notification(user_email, high_matches):
                    notifications_sent += 1
                    supabase.table('job_notifications').update({
                        'last_notified_at': datetime.now(timezone.utc).isoformat()
                    }).eq('id', sub['id']).execute()
            else:
                print(f"⏭️ [Crawler] No new high-match jobs for {user_email}.")
                    
        print(f"✅ [Crawler] Finished. Sent {notifications_sent} notifications.")
        return {"success": True, "message": f"Sent {notifications_sent} notifications."}
    except Exception as e:
        print(f"❌ [Crawler] Error: {e}")
        return {"success": False, "error": str(e)}

async def main():
    print("🚀 [Standalone Crawler] Started.")
    while True:
        print(f"🕒 [Crawler Loop] Triggering scan at {datetime.now()}...")
        run_job_crawler_task()
        print("💤 [Crawler Loop] Sleeping for 24 hours...")
        await asyncio.sleep(86400) # 24 hours

if __name__ == "__main__":
    asyncio.run(main())
