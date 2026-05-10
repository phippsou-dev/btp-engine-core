"""FastAPI application for BTP Engine HTTP Service."""

import shutil
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import JSONResponse

from .schemas import HealthResponse, RunResponse
from .security import verify_token
from .runner import extract_uploaded_file, run_engine

app = FastAPI(
    title="BTP Engine Core HTTP Service",
    description="HTTP service for BTP Engine integration with MyHome/Lovable",
    version="1.0.0"
)


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint - no authentication required."""
    return HealthResponse()


@app.post("/run", response_model=RunResponse)
async def run(
    file: UploadFile = File(...),
    mode: str = Form(...),
    _authenticated: bool = Depends(verify_token)
):
    """
    Run BTP Engine on uploaded file.
    
    Args:
        file: PDF or ZIP file
        mode: Must be 'dry_run'
        
    Returns:
        Engine execution results
    """
    # Validate mode
    if mode != "dry_run":
        raise HTTPException(
            status_code=400,
            detail=f"Only 'dry_run' mode is allowed, got: {mode}"
        )
    
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    if not (file.filename.lower().endswith('.pdf') or file.filename.lower().endswith('.zip')):
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF or ZIP files are allowed, got: {file.filename}"
        )
    
    tmp_input = None
    tmp_output = None
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract to temporary directory
        tmp_input = extract_uploaded_file(file_content, file.filename)
        
        # Run engine
        result, tmp_output = run_engine(tmp_input, mode)
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
    finally:
        # Cleanup temporary directories
        if tmp_input and tmp_input.exists():
            shutil.rmtree(tmp_input, ignore_errors=True)
        if tmp_output and tmp_output.exists():
            shutil.rmtree(tmp_output, ignore_errors=True)
