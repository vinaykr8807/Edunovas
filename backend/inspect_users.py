from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        print("Querying users table via direct SQL...")
        result = conn.execute(text("SELECT count(*) FROM users"))
        print(f"User count (SQL): {result.scalar()}")
        
        print("Checking users table structure...")
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"))
        for row in result:
            print(f"Col: {row[0]}")
    except Exception as e:
        print(f"SQL investigation failed: {e}")
