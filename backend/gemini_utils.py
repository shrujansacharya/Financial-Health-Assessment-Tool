
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

_CACHED_MODEL_NAME = None

def get_gemini_model_name():
    global _CACHED_MODEL_NAME
    if _CACHED_MODEL_NAME:
        return _CACHED_MODEL_NAME
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "gemini-1.5-flash" # Default fallback
    
    try:
        client = genai.Client(api_key=api_key)
        # Priority list
        preferred = ["gemini-2.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-pro"]
        
        available_models = []
        # Fetch available models
        for m in client.models.list():
            name = m.name.split("/")[-1] # remove 'models/' prefix
            available_models.append(name)
            
        print(f"DEBUG: Available Gemini Models: {available_models}")
        
        # Check priority
        for p in preferred:
            if p in available_models:
                print(f"DEBUG: Selected Model: {p}")
                _CACHED_MODEL_NAME = p
                return p
        
        # If none of preferred found, pick first gemini model
        for m in available_models:
            if "gemini" in m and "flash" in m:
                print(f"DEBUG: Fallback Selected Model: {m}")
                _CACHED_MODEL_NAME = m
                return m
        
        # Absolute fallback
        if available_models:
             fallback = available_models[0]
             print(f"DEBUG: Absolute Fallback Model: {fallback}")
             _CACHED_MODEL_NAME = fallback
             return fallback
             
    except Exception as e:
        print(f"Warning: Could not list models: {e}")
    
    return "gemini-1.5-flash" # Ultimate fallback
