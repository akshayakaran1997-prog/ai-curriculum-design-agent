
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil

# 1. Create the FastAPI application
app = FastAPI(
    title="AI Curriculum Design Agent",
    description="Backend for document analysis and curriculum generation",
    version="1.0.0"
)

# 2. Allow our GitHub Pages frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Create a folder to store uploaded documents
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# 4. Home API endpoint
@app.get("/")
def home():
    return {
        "message": "AI Curriculum Design Agent Backend is running!",
        "status": "success"
    }


# 5. Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "AI Curriculum Design Agent"
    }


# 6. Document upload endpoint
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    # Allow only supported document formats
    allowed_extensions = [".pdf", ".pptx", ".docx", ".txt"]

    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Upload PDF, PPTX, DOCX or TXT."
        )

    # Create a safe filename
    safe_filename = Path(file.filename).name

    file_path = UPLOAD_DIR / safe_filename

    try:
        # Save the uploaded document
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": "Document uploaded successfully!",
            "filename": safe_filename,
            "file_type": file_extension,
            "status": "success"
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to save the uploaded document."
        )

    finally:
        await file.close()
