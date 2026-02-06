from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON
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

if env_db_url:
    DATABASE_URL = env_db_url
    print(f"🔌 Connecting to Custom Database: {DATABASE_URL}")
else:
    # Fallback to local SQLite if no custom DB provided
    DATABASE_URL = "sqlite:///./financial_health_v2.db"
    print(f"📁 Connecting to Default SQLite: {DATABASE_URL}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
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

def init_db():
    Base.metadata.create_all(bind=engine)

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
        forecast_next_month=data.get('forecast_next_month', 0.0)
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    print(f"Report saved to DB with ID: {db_report.id}")
    return db_report

def get_recent_reports(db, limit=5):
    return db.query(Report).order_by(Report.upload_date.desc()).limit(limit).all()
