# Resume Scoring API

## Overview

Extract criteria API allows users to extract criteria from job descriptions and score resume API scores resumes based on these criteria. It uses OpenAI's GPT-4o model to analyze resumes and assign scores based on a predefined set of ranking criteria.

## Features

- Extracts key ranking criteria from job descriptions in PDF or DOCX format.
- Scores resumes based on extracted or provided criteria.
- Generates an Excel file with candidate scores.
- Uses FastAPI for efficient request handling.

## Requirements

- Python 3.10
- FastAPI
- Uvicorn
- OpenAI API Key
- Pandas
- pdfplumber
- python-docx

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/Prashant1729/assign.git
   cd <repository_folder>
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Environment Setup

Replace `OPENAI_API_KEY` with your OpenAI API key inside `extract

```python
OPENAI_API_KEY = "your_openai_api_key"
```

## Running the API

Run the FastAPI application using Uvicorn:

```python extract.py
```

## API Endpoints

### 1. Extract Criteria from Job Description

**Endpoint:** `/extract-criteria`

**Method:** `POST`

**Description:** Extracts key ranking criteria from a job description document.

**Request:**

- Upload a `.pdf` or `.docx` file containing the job description.

**Response:**

```json
{
  "criteria": ["Skill 1", "Skill 2", "Skill 3"]
}
```

---

### 2. Score Resumes Based on Criteria

**Endpoint:** `/score-resumes`

**Method:** `POST`

**Description:** Evaluates resumes against a given set of criteria and returns scores.

**Request:**

- JSON payload containing:
  - `criteria`: List of criteria.
  - `files`: List of resume files (`.pdf` or `.docx`).

**Response:**

- Returns an Excel file (`resume_scores.xlsx`) containing candidate scores.

## Example Usage (cURL)

### Extract Criteria

```sh
curl -X 'POST' \
  'http://127.0.0.1:8000/extract-criteria' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@job_description.pdf'
```

### Score Resumes

```sh
curl -X 'POST' \
  'http://127.0.0.1:8000/score-resumes' \
  -H 'accept: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' \
  -H 'Content-Type: multipart/form-data' \
  -F 'criteria=["Python", "Machine Learning"]' \
  -F 'files=@resume1.pdf' \
  -F 'files=@resume2.docx'
```

## Swagger UI

The API documentation is available at:

```
http://127.0.0.1:8000/docs
```

## Links to video demo
# Resume scoring api

```
https://www.loom.com/share/2578c119968e4314872d4a2d1ba26d44?sid=5ab16af8-83f2-43e2-83f2-64524c15a1be
```
# Exract Criteria api
```
https://www.loom.com/share/b98924bea0e4436b89995ce5604d7bcb?sid=0d570f2b-8c13-4581-9407-3630634d5c92
```

