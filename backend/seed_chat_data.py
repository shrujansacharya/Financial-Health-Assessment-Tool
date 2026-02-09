import pandas as pd
import os

# Path to the anomalous data we created earlier
source_file = "../anomalous_data.csv"
target_file = "latest_upload.csv"

if os.path.exists(source_file):
    print(f"Readinng from {source_file}...")
    df = pd.read_csv(source_file)
    
    # Save to backend folder for the chat app
    df.to_csv(target_file, index=False)
    print(f"SUCCESS: Created {target_file} manually.")
    print("You can now chat with the bot immediately!")
else:
    print(f"ERROR: Could not find {source_file}. Please upload a file via the dashboard.")
