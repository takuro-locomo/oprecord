from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import shutil
import os
import json
from ai_service import scan_op_log
from sheets_service import save_to_sheet

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev
    allow_credentials=False, # Disable credentials to allow wildcard origin
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def read_root():
    return {"message": "OP Log Scanner API is running"}

@app.post("/scan")
async def scan_image(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Call AI Service
        extracted_data = scan_op_log(file_path)
        
        # Clean up file? Maybe keep for debugging for now
        # os.remove(file_path)
        
        return extracted_data
    except Exception as e:
        print(f"Error scanning image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save")
async def save_data(data: Dict[str, Any] = Body(...)):
    try:
        # Log incoming data for debugging
        with open("backend_debug.log", "a") as f:
            f.write(f"Received data: {data}\n")
            
        save_to_sheet(data)
        return {"status": "success", "message": "Data saved to Google Sheets"}
    except Exception as e:
        error_msg = f"Error saving data: {e}"
        print(error_msg)
        with open("backend_error.log", "a") as f:
            f.write(f"{error_msg}\n")
            import traceback
            traceback.print_exc(file=f)
        raise HTTPException(status_code=500, detail=str(e))
