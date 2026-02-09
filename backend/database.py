from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# 1. Read from Environment Variable (Best Practice for User's Own DB)
# Example: postgresql://user:password@localhost/dbname
env_db_url = os.getenv("FINANCIAL_DB_URL")
if env_db_url and env_db_url.startswith("postgres://"):
    env_db_url = env_db_url.replace("postgres://", "postgresql://", 1)

if env_db_url:
    DATABASE_URL = env_db_url
    print(f"🔌 Connecting to Custom Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'HIDDEN'}")
else:
    # Fallback to local SQLite if no custom DB provided
    DATABASE_URL = "sqlite:///./financial_health_v2.db"
    print(f"📁 Connecting to Default SQLite: {DATABASE_URL}")

engine_args = {}
if "sqlite" in DATABASE_URL:
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    # Production DB (Postgres) Optimization
    engine_args["pool_pre_ping"] = True  # Check connection liveness before usage (Critical fix for "server closed connection")
    engine_args["pool_recycle"] = 1800   # Recycle connections every 30 mins to avoid stale timeouts
    engine_args["pool_size"] = 10        # Maximum number of connections in the pool
    engine_args["max_overflow"] = 20     # Max extra connections if pool is full

engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    score = Column(Float)
    revenue_growth = Column(Float)
    expense_ratio = Column(Float)
    net_cash_flow = Column(Float)
    raw_metrics = Column(JSON) 
    risk_flags = Column(JSON)
    ai_insights = Column(Text)
    language = Column(String, default="en")

    # New Fields for Advanced Features
    credit_score = Column(Integer) # Simulated 300-900 score
    tax_status = Column(String) # Compliant / Non-Compliant
    forecast_next_month = Column(Float) # Predicted Revenue
    transaction_data = Column(JSON) # Persistence for Chatbot (New)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # --- AUTO MIGRATION (Fix for Render Deployment) ---
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            # Check if transaction_data column exists
            # This query works for PostgreSQL (Render)
            if 'postgres' in str(engine.url):
                print("Checking for schema updates (Postgres)...")
                result = connection.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name='reports' AND column_name='transaction_data';"
                ))
                if not result.fetchone():
                    print("⚠️ Migration: Adding missing 'transaction_data' column...")
                    connection.execute(text("ALTER TABLE reports ADD COLUMN transaction_data JSON;"))
                    connection.commit()
                    print("✅ Migration: Column added successfully.")
                else:
                    print("Schema is up to date.")
    except Exception as e:
        print(f"Migration Warning: {e}")
    # --------------------------------------------------

def save_report(db, data, filename):
    db_report = Report(
        filename=filename,
        score=data['score'],
        revenue_growth=data['metrics']['rev_growth_pct'],
        expense_ratio=data['metrics']['expense_ratio'],
        net_cash_flow=data['metrics']['net_cash_flow'],
        raw_metrics=data['metrics'],
        risk_flags=data['flags'],
        ai_insights=data.get('ai_insights', ''),
        credit_score=data.get('credit_score', 0),
        tax_status=data.get('tax_status', 'Pending'),
        forecast_next_month=data.get('forecast_next_month', 0.0),
        transaction_data=data.get('transaction_data', []) # New field
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    print(f"Report saved to DB with ID: {db_report.id}")
    return db_report

def get_recent_reports(db, limit=5):
    return db.query(Report).order_by(Report.upload_date.desc()).limit(limit).all()
