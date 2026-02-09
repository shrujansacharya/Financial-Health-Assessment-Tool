from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI as PandasAI_OpenAI # distinct from check
import os
from engine import analyze_financials, normalize_columns

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    context_data: list # Ideally this would be a session ID or similar, but for hackathon we pass light data context or re-load. 
                       # Actually, we should use the cached dataframe.

# In-memory storage for the latest dataframe per user (simplified)
# In production, use Redis or database lookup
latest_dfs = {} 

def get_smart_df():
    # Helper to return the smart dataframe wrapper
    pass

@router.post("/chat")
async def chat_with_data(request: ChatRequest):
    """
    Endpoint for RAG-style chat with financial data using PandasAI.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"answer": "I am in offline mode. Please add an OpenAI API Key to enable chat."}

    # Hack: We need the dataframe. 
    # Option 1: Client sends the full JSON data back (heavy).
    # Option 2: We use a global cache (not thread safe but okay for demo).
    # Option 3: We save temp csvs by ID.
    
    # We will assume 'latest' for single user demo
    global latest_dfs
    df = latest_dfs.get('latest')
    
    if df is None:
         return {"answer": "Please upload a file first to analyze."}
         
    try:
        llm = PandasAI_OpenAI(api_token=api_key)
        sdf = SmartDataframe(df, config={"llm": llm, "enable_cache": False})
        
        response = sdf.chat(request.question)
        
        # PandasAI sometimes returns a plot path or dataframe. We want text.
        if isinstance(response, str):
            return {"answer": response}
        else:
            return {"answer": str(response)}
            
    except Exception as e:
        print(f"Chat Error: {e}")
        return {"answer": "Sorry, I couldn't process that query."}

def set_latest_df(df):
    global latest_dfs
    latest_dfs['latest'] = df
