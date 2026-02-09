from database import engine, Base
from sqlalchemy import text

def add_column():
    print(f"🔌 Connecting to Database...")
    with engine.connect() as conn:
        try:
            # Check if column exists, if not adds it
            print("Attempting to add 'transaction_data' column to 'reports' table...")
            conn.execute(text("ALTER TABLE reports ADD COLUMN IF NOT EXISTS transaction_data JSON;"))
            conn.commit()
            print("✅ SUCCESS: Column 'transaction_data' added (or already existed).")
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    add_column()
