import fitz
from skills import SKILLS
from scorer import calculate_score


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


# Extract text from resume
resume_text = extract_text(
    "resumes/sample_resume.pdf"
)

# Extract skills from resume
skills = extract_skills(resume_text)

print("Skills Found:")
print(skills)


# Read job description file
with open(
    "job_description.txt",
    "r",
    encoding="utf-8"
) as file:

    job_description = file.read()


# Extract skills from job description
job_skills = extract_skills(
    job_description
)

print("\nJob Skills:")
print(job_skills)


# Calculate score
score, matched, missing = calculate_score(
    skills,
    job_skills
)

print("\nMatch Score:")
print(score)

print("\nMatched Skills:")
print(matched)

print("\nMissing Skills:")
print(missing)