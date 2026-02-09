
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load .env locally
load_dotenv()

# Get DB URL
env_db_url = os.getenv("FINANCIAL_DB_URL")
if env_db_url and env_db_url.startswith("postgres://"):
    env_db_url = env_db_url.replace("postgres://", "postgresql://", 1)

if not env_db_url:
    print("No FINANCIAL_DB_URL found. Please set it in your environment or .env file.")
    exit(1)

print(f"Connecting to database: {env_db_url.split('@')[-1]}")

engine = create_engine(env_db_url)

with engine.connect() as connection:
    try:
        # Check if column exists
        result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='reports' AND column_name='transaction_data';"))
        if result.fetchone():
            print("Column 'transaction_data' already exists.")
        else:
            print("Adding column 'transaction_data'...")
            connection.execute(text("ALTER TABLE reports ADD COLUMN transaction_data JSON;"))
            connection.commit()
            print("Successfully added 'transaction_data' column.")
            
    except Exception as e:
        print(f"Error: {e}")
