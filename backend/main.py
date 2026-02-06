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
        else:
             raise HTTPException(status_code=400, detail="Invalid file format. Only CSV or XLSX allowed.")
            
        print(f"Dataframe loaded. Columns: {df.columns.tolist()}")
        
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
            narrative_en = generate_narrative(score, flags, "en")
            narrative_hi = generate_narrative(score, flags, "hi")
            result['ai_insights'] = narrative_en
            result['ai_insights_en'] = narrative_en
            result['ai_insights_hi'] = narrative_hi

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

def generate_narrative(score, flags, lang):
    if lang == 'hi':
        # Simple Hindi templates
        narrative = "विश्लेषण के आधार पर, व्यवसाय "
        if score > 80: narrative += "मजबूत वित्तीय स्थिति में है।"
        elif score > 50: narrative += "मध्यम वित्तीय स्थिति में है।"
        else: narrative += "गंभीर वित्तीय अस्थिरता का सामना कर रहा है।"
        
        narrative += "\n\n**यह महत्वपूर्ण क्यों है:**\n"
        if len(flags) > 0:
            narrative += f"पहचानी गई जोखिम ({', '.join([f['type'] for f in flags])}) सीधे आपके वित्त पोषण को प्रभावित करती है।"
        else:
            narrative += "मजबूत मेट्रिक्स विस्तार के लिए एक प्रधान स्थिति दर्शाते हैं।"
            
        narrative += "\n\n**सिफारिशें:**\n"
        if score < 60:
            narrative += "1. आपूर्तिकर्ताओं के साथ भुगतान शर्तों पर फिर से बातचीत करें।\n2. अनावश्यक खर्चों में 10% की कटौती करें।\n3. ऋण बोझ स्थिर होने तक नया उधार रोकें।"
        else:
            narrative += "1. उच्च उपज वाली अल्पकालिक संपत्तियों में अधिशेष नकदी का पुनर्निवेश करें।\n2. आपूर्तिकर्ताओं के साथ थोक खरीद छूट का अन्वेषण करें।\n3. उत्पाद लाइनों या विपणन पहुंच का विस्तार करने पर विचार करें।"
        return narrative
    else:
        # English
        narrative = "Based on the analysis, the business is demonstrating "
        if score > 80: narrative += "strong financial health with robust liquidity and growth."
        elif score > 50: narrative += "moderate financial health. While stable, there are areas of inefficiency."
        else: narrative += "critical financial instability. Immediate structural changes are required."
        
        narrative += "\n\n**Why it matters:**\n"
        if len(flags) > 0:
            narrative += f"The identified risks ({', '.join([f['type'] for f in flags])}) directly impact your ability to secure future financing and maintain operations."
        else:
            narrative += "Strong metrics indicate a prime position for expansion or reinvestment."
            
        narrative += "\n\n**Recommendations:**\n"
        if score < 60:
            narrative += "1. Immediately renegotiate payment terms with suppliers to improve cash flow.\n2. Audit operating expenses to cut 10% of non-essential costs.\n3. Pause new borrowing until debt burden stabilizes."
        else:
            narrative += "1. Reinvest surplus cash into high-yield short-term assets.\n2. Explore bulk-purchase discounts with suppliers using strong liquidity.\n3. Consider expanding product lines or marketing reach."
        return narrative

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
