
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from services.pdf_reader import extract_pdf_text
from services.pdf_analyzer import analyze_pdf_content
import shutil


# 1. Create the FastAPI application
app = FastAPI(
    title="AI Curriculum Design Agent",
    description="Backend for document analysis and curriculum generation",
    version="1.0.0"
)


# 2. Allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. Create upload folder
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


# 6. Document upload and processing endpoint
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    # Allow supported document formats
    allowed_extensions = [".pdf", ".pptx", ".docx", ".txt"]

    file_extension = Path(file.filename or "").suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Upload PDF, PPTX, DOCX or TXT."
        )

    safe_filename = Path(file.filename).name
    file_path = UPLOAD_DIR / safe_filename

    try:

        # Save uploaded document
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process PDF documents
        if file_extension == ".pdf":

            # Stage 1: Extract PDF text
            extracted_content = extract_pdf_text(str(file_path))

            # Stage 2: Analyze extracted text
            analysis_report = analyze_pdf_content(extracted_content)

            # Stage 3: Return processing results
            return {
                "message": "PDF uploaded, extracted, and analyzed successfully",
                "filename": safe_filename,
                "status": "success",
                "extracted_content": extracted_content,
                "analysis_report": analysis_report
            }

        # Other formats will be supported later
        return {
            "message": "Document uploaded successfully. Extraction for this format is coming next.",
            "filename": safe_filename,
            "file_type": file_extension,
            "status": "uploaded"
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(error)}"
        )

    finally:
        await file.close()
