from pydantic import BaseModel, EmailStr
from typing import List, Optional, Union
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str

# Grade schemas
class GradeBase(BaseModel):
    name: str
    description: Optional[str] = None

class GradeCreate(GradeBase):
    id: str

class Grade(GradeBase):
    id: str
    
    class Config:
        from_attributes = True

# Subject schemas
class SubjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class SubjectCreate(SubjectBase):
    id: str
    grade_id: str

class Subject(SubjectBase):
    id: str
    grade_id: str
    
    class Config:
        from_attributes = True

# Chapter schemas
class ChapterBase(BaseModel):
    name: str
    description: Optional[str] = None

class ChapterCreate(ChapterBase):
    id: str
    subject_id: str

class Chapter(ChapterBase):
    id: str
    subject_id: str
    
    class Config:
        from_attributes = True

# Topic schemas
class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None
    subtopics: List[str] = []

class TopicCreate(TopicBase):
    id: str
    chapter_id: str

class Topic(TopicBase):
    id: str
    chapter_id: str
    
    class Config:
        from_attributes = True

# Question schemas
class QuestionBase(BaseModel):
    type: str  # mcq, short, long, image
    text: str
    options: List[str] = []
    # Allow correct_answer to be an index (int), list of indices, or a string answer
    correct_answer: Optional[Union[List[int], int, str]] = None
    explanation: str
    images: List[str] = []
    difficulty: str  # easy, medium, hard
    marks: int = 1

class QuestionCreate(QuestionBase):
    id: str
    topic_id: str

class Question(QuestionBase):
    id: str
    topic_id: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Worksheet schemas
class WorksheetBase(BaseModel):
    name: str
    topic_id: str
    question_ids: List[str] = []

class WorksheetCreate(WorksheetBase):
    id: str

class Worksheet(WorksheetBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- Assessment Generation Request Models (NEW/MODIFIED) ---

class BaseGenerationRequest(BaseModel):
    """Base class defining common parameters for all content generation."""
    mcq_count: int = 2
    short_answer_count: int = 2
    long_answer_count: int = 1
    difficulty: str = "medium"
    subject_name: Optional[str] = ""
    include_images: bool = False
    generate_real_images: bool = False
    
# 1. Worksheet Request (Standard practice tool, single topic)
class WorksheetRequest(BaseGenerationRequest):
    topic_id: str

# 2. Quiz Request (Short, Focused, MCQ Heavy)
class QuizRequest(BaseGenerationRequest):
    topic_id: str
    # Overriding defaults for Quiz characteristics:
    mcq_count: int = 5
    short_answer_count: int = 1
    long_answer_count: int = 0  # Typically no long answers
    difficulty: str = "easy"

# 3. Exam Request (Long, Comprehensive, Multi-Topic)
class ExamRequest(BaseGenerationRequest):
    topic_ids: List[str] # KEY DIFFERENCE: List of topic IDs for broad scope
    # Overriding defaults for Exam characteristics:
    mcq_count: int = 10
    short_answer_count: int = 5
    long_answer_count: int = 3
    difficulty: str = "hard" # Higher default difficulty
    name: str = "Generated Exam"

# Quiz Answer schemas
class QuizAnswerBase(BaseModel):
    user_answer: Union[List[int], int, str]
    is_correct: bool = False

class QuizAnswerCreate(QuizAnswerBase):
    question_id: str
    worksheet_id: Optional[str] = None

class QuizAnswer(QuizAnswerBase):
    id: str
    user_id: str
    question_id: str
    worksheet_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Quiz Result schemas
class QuizResultBase(BaseModel):
    total_questions: int
    correct_answers: int
    score_percentage: int

class QuizResultCreate(QuizResultBase):
    worksheet_id: str

class QuizResult(QuizResultBase):
    id: str
    user_id: str
    worksheet_id: str
    completed_at: datetime
    
    class Config:
        from_attributes = True

# Quiz Feedback schemas
class QuizFeedbackBase(BaseModel):
    feedback_type: str  # "thumbs_up" or "thumbs_down"
    comment: Optional[str] = None

class QuizFeedbackCreate(QuizFeedbackBase):
    worksheet_id: str

class QuizFeedback(QuizFeedbackBase):
    id: str
    user_id: str
    worksheet_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Quiz Submission schema
class QuizSubmission(BaseModel):
    worksheet_id: Optional[str] = None
    answers: List[QuizAnswerCreate]