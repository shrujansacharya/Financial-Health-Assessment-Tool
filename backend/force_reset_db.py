from database import init_db, engine, Base
import os

# Force delete
db_path = "financial_health.db"
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print("Existing DB deleted.")
    except Exception as e:
        print(f"Could not delete DB: {e}")

print("Initializing new DB schema...")
init_db()
print("Database reset successful.")
