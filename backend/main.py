
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from services.pdf_reader import extract_pdf_text
from services.pdf_analyzer import analyze_pdf_content
from services.curriculum_generator import generate_curriculum
from services.excel_generator import generate_excel
import shutil
from services.ai_service import generate_ai_response

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
@app.get("/test-ai")
def test_ai():

    prompt = """
    You are an instructional design assistant.

    Explain the importance of learning objectives
    in an eLearning course in three simple points.
    """

    try:
        result = generate_ai_response(prompt)

        return {
            "status": "success",
            "ai_response": result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

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

            # Stage 3: Generate slide-by-slide curriculum
            curriculum_data = generate_curriculum(
            analysis_report,
            extracted_content
            )

            # Stage 4: Generate Excel workbook
            excel_filename = f"{file_path.stem}_curriculum.xlsx"
            excel_path = UPLOAD_DIR / excel_filename

            generate_excel(
                curriculum_data,
                str(excel_path)
            )

            # Stage 5: Return processing results
            return {
                "message": "PDF processed and curriculum Excel generated successfully",
                "filename": safe_filename,
                "status": "success",
                "extracted_content": extracted_content,
                "analysis_report": analysis_report,
                "curriculum": curriculum_data,
                "excel_filename": excel_filename,
                "download_url": f"/download/{excel_filename}"
            }

        # Other formats will be supported later
        return {
            "message": "Document uploaded successfully. Extraction for this format is coming next.",
            "filename": safe_filename,
            "file_type": file_extension,
            "status": "uploaded"
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(error)}"
        )

    finally:
        await file.close()


# 7. Excel download endpoint
@app.get("/download/{filename}")
def download_excel(filename: str):

    # Prevent directory traversal
    safe_filename = Path(filename).name

    if safe_filename != filename or not safe_filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Invalid Excel filename"
        )

    file_path = UPLOAD_DIR / safe_filename

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Excel file not found"
        )

    return FileResponse(
        path=file_path,
        filename=safe_filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
