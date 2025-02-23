from docx import Document
from exceptions import FileProcessingError, OpenAIProcessingError
import pdfplumber
import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Replace with your API key

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
        return text.strip()
    except Exception as e:
        raise FileProcessingError(f"Error extracting text from PDF: {str(e)}")
    

def extract_text_from_docx(docx_file) -> str:
    """Extract text from a DOCX file."""
    try:
        doc = Document(docx_file)
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    except Exception as e:
        raise FileProcessingError(f"Error extracting text from DOCX: {str(e)}")
    

def extract_text_from_file(file_path: str) -> str:
    """Extract text from a file based on its format."""
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    raise ValueError("Unsupported file format")


def extract_criteria_from_text(text):
    """Extract key ranking criteria from job description text using OpenAI API."""
    prompt = f"""
    You are an expert job analyst. Extract key ranking criteria from the following job description:
    {text}
    ---
    Return the criteria as a JSON list with **criteria** as a key.
    """
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in job analysis."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        raise OpenAIProcessingError(f"Failed to extract criteria: {str(e)}")


def score_resume(text, criteria):
    """Score resume based on given criteria using OpenAI API."""
    prompt = f"""
    Evaluate the following resume text against the given criteria and score each criterion from 0-5.
    
    Resume Text:
    {text}
    
    Criteria:
    {criteria}
    
    Return the scores in JSON format as a dictionary with criteria as keys and scores as values.
    """
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI resume evaluator."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        raise OpenAIProcessingError(f"Failed to score resume: {str(e)}")