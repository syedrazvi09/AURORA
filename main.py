from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import AssessmentSubmission, StudentProfile
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load skill genome & career tracks
with open("data/skill_genome.json") as f:
    SKILL_GENOME = json.load(f)

with open("data/career_tracks.json") as f:
    CAREER_TRACKS = json.load(f)

# Temporary in-memory storage
STUDENTS = {}

# Map assessment answers to skills (simplified: question_id = skill_name)
def map_assessment_to_skills(answers: dict):
    skills = {}
    for question, score in answers.items():
        # Score normalized to 0-100
        skills[question] = score
    return skills

# Recommend career tracks based on skills
def recommend_career(skills: dict):
    recommendations = []
    for track in CAREER_TRACKS:
        total_fit = 0
        count = 0
        for skill, req in track['required_skills'].items():
            student_skill = skills.get(skill, 0)
            fit = min(student_skill / req, 1)
            total_fit += fit
            count += 1
        avg_fit = total_fit / count
        recommendations.append({"role": track['role'], "fit_score": round(avg_fit*100, 2)})
    # Sort by best fit
    recommendations = sorted(recommendations, key=lambda x: x['fit_score'], reverse=True)
    top_roles = [r['role'] for r in recommendations if r['fit_score'] >= 50]  # threshold 50%
    return top_roles

@app.post("/submit-assessment")
def submit_assessment(submission: AssessmentSubmission):
    skills = map_assessment_to_skills(submission.answers)
    recommended_tracks = recommend_career(skills)
    profile = StudentProfile(
        student_id=submission.student_id,
        name=submission.student_name,
        skills=skills,
        recommended_tracks=recommended_tracks
    )
    STUDENTS[submission.student_id] = profile
    return profile

@app.get("/student/{student_id}")
def get_student(student_id: str):
    return STUDENTS.get(student_id, {"error": "Student not found"})
