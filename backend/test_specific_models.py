import google.generativeai as genai
import os

GEMINI_API_KEY = "AIzaSyCikLiet8ZiU0i0klew5qQ6xQSKqdQCP2M"
genai.configure(api_key=GEMINI_API_KEY)

models_to_test = [
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "models/gemini-1.5-flash",
]

print(f"Testing models with key: {GEMINI_API_KEY[:10]}...")

for model_name in models_to_test:
    print(f"\n--- Testing {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"SUCCESS: {model_name} works!")
    except Exception as e:
        print(f"FAILED: {model_name} error: {e}")
