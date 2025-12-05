import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model_name = 'models/gemini-3-pro-preview'
print(f"Checking {model_name}...")
try:
    model = genai.get_model(model_name)
    print(f"Supported methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error: {e}")
