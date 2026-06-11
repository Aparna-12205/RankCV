import fitz
import os
from semantic_utils import semantic_score


SKILLS = [
    "python",
    "java",
    "sql",
    "machine learning",
    "docker",
    "communication",
    "leadership",
    "teamwork",
    "critical thinking",
    "problem solving"
]


def extract_text(pdf_path):

    pdf = fitz.open(pdf_path)

    text = ""

    for page in pdf:
        text += page.get_text()

    return text


def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        if skill in text:
            found_skills.append(skill)

    return found_skills


# -----------------------------
# SEMANTIC SCORING (AI VERSION)
# -----------------------------

def calculate_score(resume_skills, job_skills):

    matched = []
    missing = []

    THRESHOLD = 0.6  # similarity cutoff

    for job_skill in job_skills:

        best_score = 0
        best_match = None

        for resume_skill in resume_skills:

            score = semantic_score(resume_skill, job_skill)

            if score > best_score:
                best_score = score
                best_match = resume_skill

        if best_score >= THRESHOLD:
            matched.append(job_skill)
        else:
            missing.append(job_skill)

    final_score = (len(matched) / len(job_skills)) * 100

    return final_score, matched, missing


# -----------------------------
# JOB DESCRIPTION
# -----------------------------

with open(
    "job_description.txt",
    "r",
    encoding="utf-8"
) as file:

    job_description = file.read()


job_skills = extract_skills(job_description)

print("Job Skills:")
print(job_skills)


# -----------------------------
# RANK RESUMES
# -----------------------------

results = []

resume_folder = "resumes"

for file in os.listdir(resume_folder):

    if file.endswith(".pdf"):

        pdf_path = os.path.join(resume_folder, file)

        resume_text = extract_text(pdf_path)

        resume_skills = extract_skills(resume_text)

        score, matched, missing = calculate_score(
            resume_skills,
            job_skills
        )

        results.append((file, score, matched, missing))


# -----------------------------
# SORT RESULTS
# -----------------------------

results.sort(
    key=lambda x: x[1],
    reverse=True
)


# -----------------------------
# OUTPUT
# -----------------------------

print("\nCandidate Ranking\n")

rank = 1

for file, score, matched, missing in results:

    print(f"{rank}. {file} - {score:.2f}%")

    print("Matched Skills:", matched)
    print("Missing Skills:", missing)
    print()

    rank += 1