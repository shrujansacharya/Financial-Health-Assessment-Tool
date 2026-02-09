import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Check for API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def generate_llm_insight(score, flags, industry, metrics, lang="en"):
    """
    Calls OpenAI to generate a sophisticated financial insight.
    Falls back to mock if no key or error.
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("No Gemini Key found. Using Mock.")
        return None 
        
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""
        You are an expert financial consultant for a {industry} SME. 
        Analyze the provided financial metrics and give a professional, investor-grade assessment.
        Output language: {lang}.
        Tone: Professional, direct, actionable.
        MaxLength: 150 words.
        
        Business Score: {score}/100.
        Industry: {industry}.
        Key Metrics:
        - Expense Ratio: {metrics.get('expense_ratio')}
        - Debt Burden: {metrics.get('debt_burden_ratio')}
        - Net Cash Flow: {metrics.get('net_cash_flow')}
        
        Risks Identified: {flags}
        
        Provide:
        1. Executive Summary
        2. Diagnosis of financial health
        3. 2 Specific banking products in India (specific bank names) that would help (e.g. OD, Working Capital Loan)
        """
        
        from gemini_utils import get_gemini_model_name
        model_name = get_gemini_model_name()

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Gemini Call Failed: {e}")
        return None
