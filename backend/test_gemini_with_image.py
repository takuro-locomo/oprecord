import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import sys

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Use the model we configured in ai_service.py
model_name = 'gemini-2.0-flash'
print(f"Testing model: {model_name}")

try:
    model = genai.GenerativeModel(model_name)
    
    # Path to the uploaded image (using the one from metadata)
    image_path = r"C:\Users\takur\.gemini\antigravity\brain\cb52b439-0cc8-4d22-be9a-217b10e3fcee\uploaded_image_1764900687707.png"
    
    if not os.path.exists(image_path):
        print(f"Image not found at {image_path}")
        sys.exit(1)
        
    print(f"Loading image from {image_path}...")
    img = Image.open(image_path)
    
    print("Generating content...")
    prompt = "Describe this image briefly."
    response = model.generate_content([prompt, img])
    
    print("Response received:")
    print(response.text)

except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
