import google.generativeai as genai
import os
import json
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
# Users need to set GEMINI_API_KEY in .env
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def scan_op_log(image_path):
    if not api_key:
        # Mock response for testing if no key provided
        return {
            "id": "9999999",
            "date": "2025/01/01",
            "sex": 1,
            "age": 70,
            "side": 1,
            "diagnosis": 1,
            "cement": 1,
            "stem": "Test Stem",
            "mdm": 0,
            "cup": "50",
            "screw": "2",
            "head": "0",
            "time": 120,
            "bleeding": 100
        }

    model = genai.GenerativeModel('gemini-2.0-flash')
    
    img = Image.open(image_path)
    
    prompt = """
    Analyze this OP Log image and extract the following data into a JSON object.
    
    Fields to extract:
    - id: Patient ID (e.g., 9606882)
    - date: Date of surgery (Format: YYYY/MM/DD)
    - sex: 1 for Male, 2 for Female
    - age: Patient age
    - side: 1 for Right, 2 for Left (Look for "右", "左", "R", "L", "ひだり"->2, "みぎ"->1)
    - diagnosis: 1 for OA (Osteoarthritis), check for "OA", "変形性股関節症". If unsure or other, leave null or best guess.
    - cement: Default to 1 (Cementless). ONLY if "Cemented" or "Cement" is explicitly written, set to 0.
    - stem: Stem product name (e.g., universia, wagner)
    - mdm: 1 if "DM" or "Dual Mobility" is mentioned, else 0.
    - cup: Cup size (number)
    - screw: Total count of screws. Example: "20*1 25*2" means 1+2=3 screws. Return 3. Max value is single digit.
    - head: Head size. Range typically 28-50. If "DM44/28", use the larger number (44).
    - time: Surgery duration in minutes (convert "1時間26分" to 86).
    - bleeding: Bleeding amount in mL (number only).

    Return ONLY the JSON object. No markdown formatting.
    """
    
    try:
        response = model.generate_content([prompt, img])
        text = response.text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text)
    except Exception as e:
        print(f"AI Error: {e}")
        raise Exception("Failed to extract data with AI")
