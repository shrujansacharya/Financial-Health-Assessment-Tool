from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
import pandas as pd
import io
from engine import analyze_financials
import os
import traceback
from database import SessionLocal, init_db, save_report
from report_generator import generate_pdf_report
from llm_service import generate_llm_insight

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

# Store report buffers in memory for demo simplicity (or could save to disk)
report_cache = {}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    language: str = Form("en"),
    industry: str = Form("Retail"),
    db: Session = Depends(get_db)
):
    print(f"Received file: {file.filename}, language: {language}, industry: {industry}")
    
    # 1. File Parsing
    try:
        contents = await file.read()
        df = None
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        elif file.filename.endswith('.pdf'):
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(contents)) as pdf:
                    all_text = ""
                    data = []
                    for page in pdf.pages:
                        tables = page.extract_tables()
                        for table in tables:
                            for row in table:
                                # Clean mock strategy: assume row is [Date, Description, Amount, ...]
                                # This is a heuristic for hackathon demo purposes
                                if row and len(row) >= 2:
                                    data.append(row)
                
                # Convert list to DataFrame
                if data:
                    df = pd.DataFrame(data[1:], columns=data[0])
                    print("Extracted PDF Table Data")
                else:
                    raise ValueError("No tabular data found in PDF")

            except Exception as e:
                print(f"PDF extraction error: {e}")
                raise HTTPException(status_code=400, detail="Could not parse PDF table data. Please ensure it is a standard bank statement format.")
        else:
             raise HTTPException(status_code=400, detail="Invalid file format. Only CSV, XLSX, or PDF allowed.")
            
        print(f"Dataframe loaded. Columns: {df.columns.tolist() if df is not None else 'None'}")
        
        # 2. Analysis
        result = analyze_financials(df)
        
        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])
             
        # 3. AI Insights (Real LLM or Mock)
        score = result['score']
        flags = result['flags']
        metrics = result['metrics']
        
        # Try Real LLM
        real_insight_en = generate_llm_insight(score, flags, industry, metrics, "en")
        
        if real_insight_en:
            result['ai_insights'] = real_insight_en
            result['ai_insights_en'] = real_insight_en
            # If we had a Hindi LLM call, we'd do it here. For now, mock fallback for Hindi if needed, or same.
            result['ai_insights_hi'] = "Hindi translation pending real API support." 
        else:
            # Fallback to Rule-Based Mock
            narrative_data = generate_narrative(score, flags, metrics, "en")
            
            # Construct formatted string for Frontend/DB
            if isinstance(narrative_data, dict) and "summary" in narrative_data:
                full_text = f"EXECUTIVE SUMMARY\n{narrative_data['summary']}\n\nSTRATEGIC DIAGNOSIS\n{narrative_data['diagnosis']}\n\nRECOMMENDATIONS\n"
                for i, rec in enumerate(narrative_data['recommendations'], 1):
                    full_text += f"{i}. {rec}\n"
                
                result['ai_insights'] = full_text
                result['structured_insights'] = narrative_data
            else:
                 result['ai_insights'] = str(narrative_data)

            # Hindi Mock
            narrative_hi = generate_narrative(score, flags, metrics, "hi")
            result['ai_insights_hi'] = narrative_hi.get('full_text', '')
            result['ai_insights_en'] = result['ai_insights']

        if language == 'hi':
            result['ai_insights'] = result['ai_insights_hi']
            
        # 4. Generate PDF Report
        pdf_bytes = generate_pdf_report(result)
        report_id = f"{file.filename}_{score}" # Simple ID
        report_cache[report_id] = pdf_bytes
        result['report_id'] = report_id
            
        # 5. Save to DB
        save_report(db, result, file.filename)
            
        print("Analysis successful")
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        print("ERROR PROCESSING REQUEST:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/report/{report_id}")
async def get_report(report_id: str):
    if report_id in report_cache:
        return Response(content=report_cache[report_id], media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"})
    return HTTPException(status_code=404, detail="Report not found")

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
