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
    if not OPENAI_API_KEY:
        print("No OpenAI Key found. Using Mock.")
        return None 
        
    try:
        system_prompt = f"""
        You are an expert financial consultant for a {industry} SME. 
        Analyze the provided financial metrics and give a professional, investor-grade assessment.
        Output language: {lang}.
        Tone: Professional, direct, actionable.
        MaxLength: 150 words.
        """
        
        user_prompt = f"""
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
        
        response = openai.ChatCompletion.create(
            model="gpt-4o", # or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI Call Failed: {e}")
        return None
