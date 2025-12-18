import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("--- ALL AVAILABLE MODELS ---")
for m in genai.list_models():
    print(f"Model Name: {m.name}")
    print(f"Supported Methods: {m.supported_generation_methods}")
print("----------------------------")
