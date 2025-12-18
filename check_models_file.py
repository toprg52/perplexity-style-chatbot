import os
import google.generativeai as genai
from dotenv import load_dotenv
import sys

# Redirect stdout to a file to capture all output reliably
sys.stdout = open('available_models.txt', 'w')

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: API Key not found")
    sys.exit(1)

genai.configure(api_key=api_key)

print("--- START MODEL LIST ---")
try:
    for m in genai.list_models():
        print(f"Name: {m.name}")
        print(f"Methods: {m.supported_generation_methods}")
        print("-" * 20)
except Exception as e:
    print(f"ERROR listing models: {e}")

print("--- END MODEL LIST ---")
