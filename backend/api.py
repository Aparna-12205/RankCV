from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import fitz
import shutil
import re
from docx import Document
from backend.semantic_utils import semantic_score

app = FastAPI()

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# SKILLS LIST
# -------------------------
SKILLS = [
    "python",
    "java",
    "c++",
    "javascript",
    "react",
    "node.js",
    "html",
    "css",
    "sql",
    "mongodb",
    "mysql",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "git",
    "linux",
    "machine learning",
    "deep learning",
    "nlp",
    "computer vision",
    "tensorflow",
    "pytorch",
    "data analysis",
    "communication",
    "leadership",
    "teamwork",
    "critical thinking",
    "problem solving"
]

# -------------------------
# TEXT EXTRACTION
# -------------------------
def extract_text_from_pdf(file_path):

    text = ""

    try:

        pdf = fitz.open(file_path)

        for page in pdf:
            text += page.get_text()

        pdf.close()

    except Exception as e:

        print("PDF extraction error:", e)

    return text

def extract_text_from_docx(file_path):

    doc = Document(file_path)

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text
# -------------------------
# SKILL EXTRACTION
# -------------------------
def extract_skills(text):

    text = text.lower()

    found = []

    for skill in SKILLS:

        if skill in text:
            found.append(skill)

    return found
# -------------------------
# CANDIDATE DETAILS
# -------------------------
def extract_email(text):

    match = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        text
    )

    return match.group(0) if match else "Not Found"


def extract_phone(text):

    match = re.search(
        r'(\+?\d[\d\s\-]{8,15}\d)',
        text
    )

    return match.group(0) if match else "Not Found"
    

def extract_name(text):

    lines = text.split("\n")

    for line in lines[:15]:

        line = line.strip()

        if len(line) < 3:
            continue

        if "@" in line:
            continue

        if re.search(r"\d", line):
            continue

        words = line.split()

        if (
            2 <= len(words) <= 4 and
            all(word[0].isupper() for word in words if word)
        ):
            return line

    return "Not Found"
# -------------------------
# AI SCORING
# -------------------------
def calculate_score(
    resume_skills,
    job_skills,
    semantic_similarity
):

    matched = []
    missing = []

    for skill in job_skills:

        if skill in resume_skills:
            matched.append(skill)
        else:
            missing.append(skill)

    skill_score = (
        len(matched) /
        len(job_skills) * 100
        if job_skills else 0
    )

    semantic_percent = (
        semantic_similarity * 100
    )

    final_score = (
        skill_score * 0.7 +
        semantic_percent * 0.3
    )

    return (
        round(final_score, 2),
        matched,
        missing
    )

def get_recommendation(score):

    if score >= 85:

        return "Strongly Recommended"

    elif score >= 70:

        return "Recommended"

    elif score >= 50:

        return "Consider"

    else:

        return "Not Recommended"
# -------------------------
# TEST ENDPOINT
# -------------------------
@app.get("/test")
def test():

    return {
        "message": "Backend is working"
    }


# -------------------------
# PING ENDPOINT
# -------------------------
@app.get("/ping")
def ping():

    return {
        "status": "ok"
    }


# -------------------------
# ANALYZE ENDPOINT
# -------------------------
@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...)
):

    file_path = f"temp_{file.filename}"

    try:

        file.file.seek(0)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(
                file.file,
                f
            )

        if file.filename.lower().endswith(".pdf"):

             text = extract_text_from_pdf(
            file_path
    )

        elif file.filename.lower().endswith(".docx"):

            text = extract_text_from_docx(
            file_path
    )

        else:

            text = ""

        skills = extract_skills(text)

        return {
            "filename": file.filename,
            "skills": skills
        }

    except Exception as e:

        print("Analyze Error:", e)

        return {
            "filename": file.filename,
            "skills": [],
            "error": str(e)
        }

    finally:

        if os.path.exists(file_path):
            os.remove(file_path)


# -------------------------
# RANK ENDPOINT
# -------------------------
@app.post("/rank")
async def rank_candidates(
    job_description: str = Form(...),
    files: List[UploadFile] = File(...)
):

    print("===== /rank called =====")

    try:

        job_skills = extract_skills(
            job_description
        )

        print(
            "Job Skills:",
            job_skills
        )

        results = []

        for file in files:

            file_path = (
                f"temp_{file.filename}"
            )

            try:

                file.file.seek(0)

                with open(
                    file_path,
                    "wb"
                ) as f:

                    shutil.copyfileobj(
                        file.file,
                        f
                    )

                if file.filename.lower().endswith(".pdf"):

                    text = extract_text_from_pdf(
                    file_path
                 )

                elif file.filename.lower().endswith(".docx"):

                    text = extract_text_from_docx(
                    file_path
                )

                else:

                    text = ""
                name = extract_name(text)

                email = extract_email(text)

                phone = extract_phone(text)
                resume_skills = (
                    extract_skills(text)
                )

                print(
                    "Resume Skills:",
                    resume_skills
                )

                semantic_similarity = (
                    semantic_score(
                        text,
                        job_description
                    )
                )

                print(
                    "Semantic Score:",
                    semantic_similarity
                )

                score, matched, missing = (
                    calculate_score(
                        resume_skills,
                        job_skills,
                        semantic_similarity
                    )
                )

                results.append({

                    "filename":
                        str(file.filename),
                    
                    "name":
                        name,
                    "email":
                        email,
                    "phone":
                        phone,
                    "score":
                        float(score),
                    "recommendation":
                        get_recommendation(score),

                    "semantic_score":
                        round(
                            semantic_similarity * 100,
                            2
                        ),

                    "matched":
                        matched,

                    "missing":
                        missing
                })

            except Exception as e:

                print(
                    f"ERROR processing {file.filename}: {e}"
                )

                results.append({

                    "filename":
                        str(file.filename),
                    "name":
                        "Not Found",
                    "email":
                        "Not Found",
                    "phone":
                        "Not Found",
                    "score":
                        0.0,

                    "semantic_score":
                        0.0,

                    "matched":
                        [],

                    "missing":
                        job_skills
                })

            finally:

                if os.path.exists(
                    file_path
                ):
                    os.remove(file_path)

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        response_data = {

            "job_skills":
                job_skills,

            "rankings":
                results
        }

        print(
            "===== RESPONSE ====="
        )

        print(response_data)

        return response_data

    except Exception as e:

        print(
            "===== FATAL ERROR ====="
        )

        print(e)

        return {

            "job_skills":
                [],

            "rankings":
                [],

            "error":
                str(e)
        }

