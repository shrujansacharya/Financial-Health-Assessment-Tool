import pandas as pd
import numpy as np

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Smartly rename columns to match expected schema based on keywords.
    Expected: Date, Revenue, Operating Expenses, Loan Repayment, Accounts Receivable, Accounts Payable
    """
    df.columns = [str(c).strip() for c in df.columns]
    
    mappings = {
        'Date': ['date', 'period', 'month', 'year', 'time', 'order date', 'invoice date', 'transaction date', 'purchase date', 'billing date'],
        'Revenue': ['revenue', 'sales', 'gross sales', 'income', 'turnover', 'top line', 'total sales', 'net sales', 'amount', 'total amount'],
        'Operating Expenses': ['operating expenses', 'expenses', 'opex', 'costs', 'expenditure', 'cogs', 'total expenses', 'manufacturing price'],
        'Loan Repayment': ['loan', 'repayment', 'emi', 'debt', 'interest', 'liabilities'],
        'Accounts Receivable': ['receivable', 'ar', 'debtors', 'due from'],
        'Accounts Payable': ['payable', 'ap', 'creditors', 'due to', 'owed']
    }
    
    rename_map = {}
    lower_cols = {c.lower(): c for c in df.columns}
    
    for target, aliases in mappings.items():
        if target in df.columns: continue
        
        # 1. Exact match check
        if target.lower() in lower_cols:
            rename_map[lower_cols[target.lower()]] = target
            continue 
        
        # 2. Alias match check
        aliases.sort(key=len, reverse=True)
        for alias in aliases:
            match_found = False
            for col_name_lower, col_name_original in lower_cols.items():
                if alias == col_name_lower or alias in col_name_lower: 
                    if col_name_original not in rename_map.values(): # Avoid stealing confirmed cols
                         rename_map[col_name_original] = target
                         match_found = True
                         break
            if match_found: break
                
    if rename_map:
        df = df.rename(columns=rename_map)
        
    return df

def analyze_financials(df: pd.DataFrame):
    try:
        # Phase 1: Intelligent Normalization
        df = normalize_columns(df)
        
        # Phase 2: Logic Derivation (if standard cols missing)
        # Fallback: Revenue = Quantity * Unit Price 
        if 'Revenue' not in df.columns:
            # Look for quantity and price candidates
            lower_cols = {c.lower(): c for c in df.columns}
            qty_col = next((c for c in df.columns if 'quantity' in c.lower() or 'units' in c.lower() or 'qty' in c.lower()), None)
            price_col = next((c for c in df.columns if 'price' in c.lower() or 'rate' in c.lower() or 'unit cost' in c.lower()), None)
            
            if qty_col and price_col:
                print(f"Deriving Revenue from {qty_col} * {price_col}")
                # Ensure numeric
                df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce').fillna(0)
                df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
                df['Revenue'] = df[qty_col] * df[price_col]

        # Phase 3: Semantic Validation
        if 'Date' not in df.columns or 'Revenue' not in df.columns:
            # Check if it looks like a credit file (contains 'CreditScore' or 'Customer')
            cols_str = " ".join(df.columns.astype(str))
            
            is_credit_file = 'credit' in cols_str.lower() or 'customer' in cols_str.lower()
            
            msg = "This dataset appears to be a credit or customer profile file." if is_credit_file else "This dataset does not seem to contain time-series financial data."
            
            return {
                "error": (
                    f"{msg}\n"
                    "FinHealth AI’s financial analysis requires time-based revenue or sales data.\n"
                    "Please upload a dataset containing at least: Date + Revenue (or Sales)."
                )
            }
            
        optional_defaults = {
            'Operating Expenses': 0.0,
            'Loan Repayment': 0.0,
            'Accounts Receivable': 0.0,
            'Accounts Payable': 0.0
        }
        
        for col, default_val in optional_defaults.items():
            if col not in df.columns:
                df[col] = default_val
        
        # Parsing data types
        cols_to_parse = ['Revenue', 'Operating Expenses', 'Loan Repayment', 'Accounts Receivable', 'Accounts Payable']
        for col in cols_to_parse:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                 df[col] = df[col].fillna(0)
        
        # Ensure date sorting
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date']) 
        df = df.sort_values(by='Date')
        
        if len(df) == 0:
             return {"error": "No valid rows with dates found."}
        
        # calculate derived columns
        df['Net Cash Flow'] = df['Revenue'] - df['Operating Expenses'] - df['Loan Repayment']
        
        # 1. Metrics Computation
        total_revenue = df['Revenue'].sum()
        total_expenses = df['Operating Expenses'].sum()
        total_loan_repayment = df['Loan Repayment'].sum()
        
        # Revenue Growth (CAGR or Simple Growth)
        if len(df) > 1:
            start_rev = df['Revenue'].iloc[0]
            end_rev = df['Revenue'].iloc[-1]
            rev_growth_pct = ((end_rev - start_rev) / start_rev) * 100 if start_rev != 0 else 0.0
        else:
            rev_growth_pct = 0.0
            
        expense_ratio = total_expenses / total_revenue if total_revenue != 0 else 0.0
        total_net_cash_flow = df['Net Cash Flow'].sum()
        avg_ar = df['Accounts Receivable'].mean()
        avg_ap = df['Accounts Payable'].mean()
        working_capital = avg_ar - avg_ap
        debt_burden_ratio = total_loan_repayment / total_revenue if total_revenue != 0 else 0.0
        cash_flow_volatility = df['Net Cash Flow'].std()
        if pd.isna(cash_flow_volatility): cash_flow_volatility = 0.0
        
        # 2. Score Calculation (0-100)
        score = 50
        if rev_growth_pct > 0: score += 10
        if rev_growth_pct > 15: score += 5
        if expense_ratio < 0.5: score += 15
        elif expense_ratio > 0.9: score -= 10
        if total_net_cash_flow > 0: score += 15
        else: score -= 10
        if working_capital > 0: score += 5
        if debt_burden_ratio < 0.1: score += 10
        elif debt_burden_ratio > 0.3: score -= 10
        
        score = max(0, min(100, int(round(score))))
        
        # 3. Risk Flags
        flags = []
        if total_net_cash_flow < 0:
            flags.append({"type": "Liquidity Risk", "severity": "High"})
        if expense_ratio > 0.8:
            flags.append({"type": "High Expense Risk", "severity": "Medium"})
        if debt_burden_ratio > 0.3:
            flags.append({"type": "Debt Stress", "severity": "High"})
            
        # --- NEW ADVANCED FEATURES (SIMULATED) ---
        
        # 1. Credit Score Simulation (300-900)
        # Base credit score 650
        credit_score = 650
        if score > 70: credit_score += 100
        if debt_burden_ratio < 0.1: credit_score += 50
        if total_net_cash_flow > 0: credit_score += 50
        if flags: credit_score -= (len(flags) * 30)
        credit_score = max(300, min(900, credit_score))
        
        # 2. Tax Compliance Check (Rule based)
        # If Revenue > 0 and Expenses > 0, we assume records exist.
        tax_status = "Compliant" if total_revenue > 0 else "Review Needed"
        if expense_ratio > 1.0: tax_status = "Audit Risk (High Loss)"
        
        # 3. Forecasting (Simple Moving Average for next month)
        # Predict next month revenue based on last 3 months average
        if len(df) >= 3:
            forecast_next_month = df['Revenue'].iloc[-3:].mean()
        elif len(df) > 0:
            forecast_next_month = df['Revenue'].mean()
        else:
            forecast_next_month = 0.0
        
        metrics = {
            "rev_growth_pct": float(round(rev_growth_pct, 2)),
            "expense_ratio": float(round(expense_ratio, 2)),
            "net_cash_flow": float(round(total_net_cash_flow, 2)),
            "working_capital": float(round(working_capital, 2)),
            "debt_burden_ratio": float(round(debt_burden_ratio, 2)),
            "cash_flow_volatility": float(round(cash_flow_volatility, 2))
        }
        
        df['Month'] = df['Date'].dt.strftime('%Y-%m')
        monthly_data = df.groupby('Month')[['Revenue', 'Operating Expenses', 'Net Cash Flow']].sum().reset_index().to_dict('records')
        monthly_data.sort(key=lambda x: x['Month'])
        
        return {
            "score": score,
            "metrics": metrics,
            "flags": flags,
            "charts_data": monthly_data,
            "ai_prompt": "Prompt...",
            
            # New Keys
            "credit_score": int(credit_score),
            "tax_status": tax_status,
            "forecast_next_month": float(round(forecast_next_month, 2))
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Analysis failed: {str(e)}"}
