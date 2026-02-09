from thefuzz import process, fuzz
import openai
import os
import json

# Predefined Categories for SMEs
CATEGORIES = {
    "Revenue": [
        "sales", "revenue", "income", "deposit", "credit", "payment received", "client payment", "invoice", "upwork", "stripe", "razorpay"
    ],
    "Operating Expenses": [
        "uber", "ola", "amazon", "aws", "google cloud", "salary", "payroll", "rent", "office", "wework", "electricity", "utility", "wifi", "internet", "software", "subscription", "marketing", "ads", "facebook", "linkedin", "travel", "food", "swiggy", "zomato"
    ],
    "Loan Repayment": [
        "emi", "loan", "interest", "bank charges", "credit card payment", "repayment"
    ],
    "Personal/Other": [
        "netflix", "spotify", "gym", "personal", "withdrawal", "atm", "cash"
    ]
}

def categorize_transaction_heuristic(description):
    """
    Categorizes a transaction string using fuzzy matching against predefined keywords.
    """
    description = str(description).lower()
    
    best_category = "Uncategorized"
    highest_score = 0
    
    for category, keywords in CATEGORIES.items():
        # process.extractOne returns (match, score)
        match, score = process.extractOne(description, keywords, scorer=fuzz.partial_ratio)
        if score > highest_score:
            highest_score = score
            best_category = category
            
    # Threshold for confidence
    if highest_score > 60:
        return best_category
    return "Operating Expenses" # Default conservative assumption for unknowns (usually expenses)

def categorize_transaction_llm(description):
    """
    Uses OpenAI GPT-4o-mini to categorize transaction.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        full_prompt = (
            "You are a financial classifier. Classify the transaction description into one of: "
            "['Revenue', 'Operating Expenses', 'Loan Repayment', 'Personal/Other']. "
            "Return ONLY the category name.\n\n"
            f"Transaction: {description}"
        )
        
        from gemini_utils import get_gemini_model_name
        model_name = get_gemini_model_name()
        
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt
        )
        category = response.text.strip()
        
        # Validate output
        valid_cats = ["Revenue", "Operating Expenses", "Loan Repayment", "Personal/Other"]
        if category not in valid_cats:
            # Fallback to fuzzy mapping if LLM hallucinates
             return categorize_transaction_heuristic(description)
             
        return category
    except Exception as e:
        print(f"LLM Categorization Failed: {e}")
        return None

def enrich_financial_data(df):
    """
    Enriches the dataframe by categorizing transactions based on 'Description' column.
    If 'Description' exists, it attempts to fill missing 'Revenue'/'Operating Expenses'.
    """
    if 'Description' not in df.columns:
        return df
        
    print("running enrichment on Description column...")
    
    # Check if we need to derive Revenue/Expenses or just categorize for insights
    # Scenario: User uploads raw bank statement with [Date, Description, Debit, Credit] OR [Date, Description, Amount]
    
    # Case 1: Debit/Credit columns exist
    if 'Debit' in df.columns and 'Credit' in df.columns:
        df['Debit'] = df['Debit'].fillna(0)
        df['Credit'] = df['Credit'].fillna(0)
        
        # Logic: Credit is Revenue. Debit is Expense (need to split into Opex vs Loan)
        df['Revenue'] = df['Credit']
        
        # For Debits, classify into Opex or Loan
        def classify_debit(row):
            if row['Debit'] == 0: return 0, 0
            
            # Hybrid approach: Try LLM first if key exists (simulated here as we might not want to burn tokens on every row in a loop for this demo. 
            # Ideally, batch processing. For now, let's use Heuristic for speed/demo safety).
            category = categorize_transaction_heuristic(row['Description'])
            
            if category == 'Loan Repayment':
                return 0, row['Debit']
            else:
                return row['Debit'], 0 # Default to Opex
        
        # Apply classification
        # Zip to iterate faster or use apply
        classifications = df.apply(classify_debit, axis=1, result_type='expand')
        df['Operating Expenses'] = classifications[0]
        df['Loan Repayment'] = classifications[1]
        
    # Case 2: Only Description and Amount exist (sign determines in/out) but usually bank statements have Debit/Credit.
    # Let's handle the specific case where user asks for "Zero-Shot Transaction Categorization" implies we create a "Category" column.
    
    df['Category_AI'] = df['Description'].apply(categorize_transaction_heuristic)
    
    return df
