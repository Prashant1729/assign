from fastapi import File, UploadFile, HTTPException, Response, Form,APIRouter
import shutil
import os
import openai
from typing import List
import uvicorn
import json
import io
import pandas as pd
from exceptions import OpenAIProcessingError,FileProcessingError
from services.utils import (extract_text_from_pdf,
                   extract_text_from_docx,
                   score_resume,
                   extract_criteria_from_text)

router = APIRouter()


@router.post("/score-resumes", description="API to score resumes based on given criteria.")
async def score_resumes(
    criteria: List[str] = Form(...),
    files: List[UploadFile] = File(...)
):
    """Score resumes against given criteria and return an Excel file."""
    results = []
    
    for file in files:
        try:
            if file.filename.endswith(".pdf"):
                text = extract_text_from_pdf(file.file)
            elif file.filename.endswith(".docx"):
                text = extract_text_from_docx(file.file)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {file.filename}")
            
            scores = score_resume(text, criteria)
            total_score = sum(scores.values())
            results.append([file.filename] + list(scores.values()) + [total_score])
        except FileProcessingError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except OpenAIProcessingError as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    columns = ["Candidate Name"] + list(scores.keys()) + ["Total Score"]
    df = pd.DataFrame(results, columns=columns)
    
    output_stream = io.BytesIO()
    df.to_excel(output_stream, index=False)
    output_stream.seek(0)
    
    return Response(
        content=output_stream.getvalue(), 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        headers={"Content-Disposition": "attachment; filename=resume_scores.xlsx"}
    )

@router.post("/extract-criteria", description="API to extract criteria from a job description.")
async def extract_criteria(file: UploadFile = File(...)):
    """Extract key ranking criteria from a job description file."""
    try:
        if file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file.file)
        elif file.filename.endswith(".docx"):
            text = extract_text_from_docx(file.file)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file.filename}")
        
        criteria = extract_criteria_from_text(text)
        return criteria
    except FileProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except OpenAIProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
