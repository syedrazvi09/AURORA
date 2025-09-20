from pydantic import BaseModel
from typing import List, Dict

class AssessmentSubmission(BaseModel):
    student_id: str
    student_name: str
    answers: Dict[str, int]  # {question_id: score}

class StudentProfile(BaseModel):
    student_id: str
    name: str
    skills: Dict[str, int] = {}
    recommended_tracks: List[str] = []
