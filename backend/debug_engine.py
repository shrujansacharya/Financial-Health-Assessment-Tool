import pandas as pd
import io
import traceback
import os
from engine import analyze_financials

try:
    print("CWD:", os.getcwd())
    path = 'sample_data.csv'
    if not os.path.exists(path):
        print(f"File not found at {path}, trying ../sample_data.csv")
        path = '../sample_data.csv'
        
    print(f"Loading sample data from {path}...")
    df = pd.read_csv(path)
    print("Columns:", df.columns.tolist())
    
    print("Running analysis...")
    result = analyze_financials(df)
    
    print("Analysis complete.")
    print("Result keys:", result.keys())
    
    if "error" in result:
        print("Analysis returned error:", result['error'])
    else:
        print("Score:", result.get('score'))
        # Simulate Main.py logic for narrative
        score = result['score']
        flags = result['flags']
        narrative = "Based on the analysis..."
        result['ai_insights'] = narrative
        print("AI Mock Generation success")
        
except Exception as e:
    print("CRASHED:")
    traceback.print_exc()
