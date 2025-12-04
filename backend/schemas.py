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

# Worksheet request schema
class WorksheetRequest(BaseModel):
    topic_id: str
    mcq_count: int = 0
    short_answer_count: int = 0
    long_answer_count: int = 0
    difficulty: str = "medium"
    include_images: bool = False