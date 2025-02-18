from fastapi import FastAPI, File, UploadFile, HTTPException,Response
import shutil
import os
import openai
from typing import List,Dict
from docx import Document
import uvicorn
import json
import pdfplumber
import io
import pandas as pd


app = FastAPI()

OPENAI_API_KEY = ""  # Replace with your API key
#openai.api_key = OPENAI_API_KEY

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_file(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")

def extract_criteria_from_text(text):
    prompt = f"""
    You are an expert job analyst.Extract key ranking criteria from the following job description:
    {text}
    ---
    Return the criteria as a JSON list with criteria as a key.
    """
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",  # Use an appropriate model
        messages=[{"role": "system", "content": "You are an expert in job analysis."},
                  {"role": "user", "content": prompt}],response_format={"type":"json_object"}
    )
    print("criteria json is",response.choices[0].message.content.strip())
    return response.choices[0].message.content.strip()



# Function to score resumes using OpenAI
def score_resume(text: str, criteria: List[str]) -> Dict[str, int]:
    prompt = f"""
    Evaluate the following resume text against the given criteria and score each criterion from 0-5.
    
    Resume Text:
    {text}
    
    Criteria:
    {criteria}
    
    Return the scores in JSON format as a dictionary with criteria as keys and scores as values
    """
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are an AI resume evaluator."},
                  {"role": "user", "content": prompt}],response_format={"type":"json_object"}
    )
    
    
    scores_text = response.choices[0].message.content.strip()
    try:
        scores = json.loads(scores_text)  # Ensure correct JSON format
    except json.JSONDecodeError:
        print("Error parsing JSON:", scores_text)  # Debugging
        return {criterion: 0 for criterion in criteria}  # Return zeroes if parsing fails
    score_dict = {key: int(value) for key, value in scores.items()}
    return score_dict # Filter valid keys
      # Ensure OpenAI returns structured data

@app.post("/score-resumes",description = "API to score resume on criteria.")
async def score_resumes(
    criteria: List[str],
    files: List[UploadFile] = File(...)
):
    results = []
    
    for file in files:
        if file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file.file)
        elif file.filename.endswith(".docx"):
            text = extract_text_from_docx(file.file)
        else:
            return {"error": f"Unsupported file format: {file.filename}"}
        
        scores = score_resume(text, criteria)
        print(scores.values())
        scores_list = list(scores.values())
        total_score = sum(scores_list)
        results.append([file.filename] + list(scores.values()) + [total_score])
    
    columns = ["Candidate Name"] + list(scores.keys()) + ["Total Score"]
    df = pd.DataFrame(results, columns=columns)
    
    
   
    output_stream = io.BytesIO()
    df.to_excel(output_stream, index=False)
    output_stream.seek(0)
    
    

    return Response(content=output_stream.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=resume_scores.xlsx"})


@app.post("/extract-criteria",description = "API to extract the criteria from the job description.")
async def extract_criteria(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    temp_file_path = f"temp.{file_ext}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        text = extract_text_from_file(temp_file_path)
        criteria_json = extract_criteria_from_text(text)
    finally:
        os.remove(temp_file_path)
    
    return json.loads(criteria_json)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

