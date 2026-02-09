from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
import pandas as pd
import io
from engine import analyze_financials
import os
import traceback
from database import SessionLocal, init_db, save_report
from report_generator import generate_pdf_report
from llm_service import generate_llm_insight
# New Imports
import json

app = FastAPI()

# Init Database
init_db()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store report buffers in memory
report_cache = {}

# SINGLE USER SESSION CACHE FOR RAG CHAT
active_df = None 

class ChatRequest(BaseModel):
    message: str

# ... (Upload Endpoint remains mostly the same, but updates active_df)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    language: str = Form("en"),
    industry: str = Form("Retail"),
    db: Session = Depends(get_db)
):
    global active_df
    # ... (File parsing logic remains the same)
    # ... (Dataframe loading logic remains the same)
    
    # ... (File parsing logic) ...
    try:
        # Use file.file directly...
        df = None
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file.file)
        elif file.filename.endswith('.pdf'):
            # ... (PDF logic) ...
            try:
                import pdfplumber
                with pdfplumber.open(file.file) as pdf:
                    all_text = ""
                    data = []
                    for page in pdf.pages:
                        tables = page.extract_tables()
                        for table in tables:
                            for row in table:
                                if row and len(row) >= 2:
                                    data.append(row)
                if data:
                    df = pd.DataFrame(data[1:], columns=data[0])
            except Exception:
                raise HTTPException(status_code=400, detail="PDF Error")
        else:
             raise HTTPException(status_code=400, detail="Invalid Format")

        # SAVE TO DISK FOR CHAT PERSISTENCE
        if df is not None:
             save_path = os.path.abspath("latest_upload.csv")
             df.to_csv(save_path, index=False)
             print(f"DEBUG: Successfully saved dataframe to {save_path}")
             print(f"DEBUG: File exists check: {os.path.exists(save_path)}")


        # 2. Analysis
        result = analyze_financials(df)
        
        # --- RAG PREPARATION ---
        # Update the global dataframe for chat
        from engine import normalize_columns
        active_df = normalize_columns(df.copy())
        # Ensure we have numeric types for calculation
        cols_to_parse = ['Revenue', 'Operating Expenses', 'Loan Repayment', 'Accounts Receivable', 'Accounts Payable']
        for col in cols_to_parse:
            if col in active_df.columns:
                 active_df[col] = pd.to_numeric(active_df[col], errors='coerce').fillna(0)
        print("Initialized Chat Context in Memory")
        # -----------------------

        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])

        # ... (Rest of Analysis logic) ...


        # ... (Rest of Analysis/mock logic remains same)
        # 3. AI Insights
        score = result['score']
        flags = result['flags']
        metrics = result['metrics']
        
        # Try Real LLM
        real_insight_en = generate_llm_insight(score, flags, industry, metrics, "en")
        
        if real_insight_en:
            result['ai_insights'] = real_insight_en
            result['ai_insights_en'] = real_insight_en
            result['ai_insights_hi'] = "Hindi translation pending real API support." 
        else:
            # Fallback
            narrative_data = generate_narrative(score, flags, metrics, "en")
            if isinstance(narrative_data, dict) and "summary" in narrative_data:
                full_text = f"EXECUTIVE SUMMARY\n{narrative_data['summary']}\n\nSTRATEGIC DIAGNOSIS\n{narrative_data['diagnosis']}\n\nRECOMMENDATIONS\n"
                for i, rec in enumerate(narrative_data['recommendations'], 1):
                    full_text += f"{i}. {rec}\n"
                result['ai_insights'] = full_text
            else:
                 result['ai_insights'] = str(narrative_data)

            narrative_hi = generate_narrative(score, flags, metrics, "hi")
            result['ai_insights_hi'] = narrative_hi.get('full_text', '')
            result['ai_insights_en'] = result['ai_insights']

        if language == 'hi':
            result['ai_insights'] = result['ai_insights_hi']
            
        # 4. Generate PDF Report
        pdf_bytes = generate_pdf_report(result)
        report_id = f"{file.filename}_{score}" 
        if len(report_cache) > 50: report_cache.clear() 
        report_cache[report_id] = pdf_bytes
        result['report_id'] = report_id
            
        # 5. Save to DB with Transaction Data
        if df is not None:
             # handle NaNs for JSON (Postgres doesn't like NaN)
             result['transaction_data'] = df.where(pd.notnull(df), None).to_dict(orient='records')
        
        save_report(db, result, file.filename)
            
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/report/{report_id}")
async def get_report(report_id: str):
    if report_id in report_cache:
        return Response(content=report_cache[report_id], media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"})
    return HTTPException(status_code=404, detail="Report not found")

@app.post("/chat")
async def chat_with_data(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Financial Copilot Endpoint
    Role: Explainer & Advisor (No raw data calculation)
    """
    from database import Report
    from gemini_utils import get_gemini_model_name
    from google import genai
    
    # 1. Fetch Latest Context from DB
    last_report = db.query(Report).order_by(Report.upload_date.desc()).first()
    
    if not last_report:
        return JSONResponse(content={"answer": "I don't have any financial analysis yet. Please upload a Bank Statement on the dashboard first!"})

    # 2. Build Knowledge Base (Context)
    # This is the "computed financial summary" the user requested
    context_summary = {
        "Health Score": f"{last_report.score}/100",
        "Revenue Growth": f"{last_report.revenue_growth}%",
        "Expense Ratio": f"{last_report.expense_ratio}",
        "Net Cash Flow": f"{last_report.net_cash_flow}",
        "Identified Risks": last_report.risk_flags, # List of strings
        "Tax Status": last_report.tax_status,
        "Credit Score Est": last_report.credit_score,
        "AI Insights": last_report.ai_insights
    }

    print(f"DEBUG: Chat Context Loaded: {context_summary}")
    
    # 3. Setup GenAI Client
    api_key = os.getenv("GEMINI_API_KEY") # Prioritize Gemini as per recent setup
    if not api_key:
        return JSONResponse(content={"answer": "Offline Mode: API Key missing."})

    try:
        client = genai.Client(api_key=api_key)
        model_name = get_gemini_model_name()
        
        # 4. Construct System Prompt (The "Brain")
        system_prompt = f"""
        You are a **Financial Analysis Assistant** for SMEs.
        Your role is to explain the user's financial health based ONLY on the provided summary.
        
        ### 📊 Financial Context (ALREADY COMPUTED):
        {context_summary}
        
        ### 👑 Guidelines:
        1. **Explain, Don't Calculate**: The numbers are already there. Explain WHAT they mean.
        2. **Be Insightful**: If the score is low, explain why (look at risks). If high, congratulate them.
        3. **Simple Business Language**: Avoid jargon. Speak to a business owner.
        4. **Safety & Compliance**: 
           - Do NOT give legal, tax, or investment advice.
           - Always imply these are "indicative insights".
        5. **Scope**: Answer questions about the score, cash flow, risks, and improvements.
        
        ### 🚫 Restrictions:
        - Do not analyze raw CSV rows (you don't have them).
        - Do not output Python code.
        - Do not make up numbers not in the context.
        
        User Question: "{request.message}"
        
        Answer (Short, Professional, Helpful):
        """
        
        # 5. Generate Answer (Text Only)
        response = client.models.generate_content(
            model=model_name, 
            contents=system_prompt
        )
        
        answer = response.text.strip()
        return JSONResponse(content={"answer": answer})
        
    except Exception as e:
        print(f"Chat Consultant Error: {e}")
        # MOCK FALLBACK for Demo Resilience
        return JSONResponse(content={"answer": f"I can see your Financial Score is {last_report.score}/100. (API Connection Issue: {str(e)})"})

def generate_narrative(score, flags, metrics, lang):
    if lang == 'hi':
        return {"full_text": "विश्लेषण के आधार पर, वित्तीय स्थिति का मूल्यांकन किया गया है। विस्तृत रिपोर्ट के लिए कृपया अंग्रेजी संस्करण देखें।"}
    
    # English - Structured Investor-Grade Insight
    expense_ratio = metrics.get('expense_ratio', 0)
    net_margin = metrics.get('net_profit_margin', 0)
    dscr = metrics.get('dscr', 0)
    burn_rate = metrics.get('burn_rate', 0)
    
    # 1. Executive Summary
    status = "Robust Financial Health" if score > 80 else "Moderate Stability" if score > 50 else "Critical Financial Instability"
    summary = (f"The business indicates {status} (Score: {score}/100) with a Net Profit Margin of {net_margin:.1f}%. "
               f"{'Operations are highly profitable.' if net_margin > 15 else 'Margins are tight; volume growth is essential.' if net_margin > 0 else 'The business is operating at a loss, prioritizing immediate efficiency audits.'}")

    # 2. Strategic Diagnosis
    diagnosis_parts = []
    
    # Liquidity Check
    if metrics.get('net_cash_flow', 0) > 0:
        diagnosis_parts.append("Liquidity is strong, providing a buffer for reinvestment.")
    else:
        diagnosis_parts.append(f"Liquidity is under pressure with an average monthly burn rate of ₹{burn_rate:,.0f}. Immediate cash preservation is required.")
        
    # Solvency Check (DSCR)
    if dscr < 1.2:
        diagnosis_parts.append(f"Solvency Risk: Debt Service Coverage Ratio (DSCR) is {dscr:.2f}, indicating difficulty in meeting debt obligations.")
    elif dscr > 2.0:
        diagnosis_parts.append("Solvency is robust; the balance sheet has capacity for additional leverage to fund expansion.")
        
    diagnosis = " ".join(diagnosis_parts)

    # 3. Actionable Recommendations
    recs = []
    
    if score < 60:
        # Turnaround Focus
        recs.append("Immediate OPEX Audit: Target a 15% reduction in fixed costs to restore positive Net Margins.")
        if burn_rate > 0:
            recs.append(f"Burn Rate Control: Extend vendor payment terms (DPO) to preserve roughly ₹{burn_rate*.5:,.0f} in monthly working capital.")
        
        if dscr < 1.0:
            recs.append("Debt Restructuring: Renegotiate EMI schedules to align with current cash inflow velocity.")
        else:
            recs.append("Revenue Diversification: Launch a low-cost pilot to activate a secondary revenue stream.")
            
    else:
        # Growth Focus
        recs.append("Capital Efficiency: Reinvest retained earnings into efficiency automation to improve Net Margins by 2-3%.")
        if dscr > 2.0:
            recs.append("Leverage Strategy: Utilize strong debt coverage to secure a low-interest credit line for inventory expansion.")
        recs.append("Market Penetration: Allocate 10-15% of surplus liquidity towards aggressively acquiring market share in high-margin segments.")
        
    return {
        "summary": summary,
        "diagnosis": diagnosis,
        "recommendations": recs
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
