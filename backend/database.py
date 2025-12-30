import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer, Text, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = relationship("Question", back_populates="user")
    worksheets = relationship("Worksheet", back_populates="user")

class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    subjects = relationship("Subject", back_populates="grade")

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    grade_id = Column(String, ForeignKey("grades.id"))
    
    # Relationships
    grade = relationship("Grade", back_populates="subjects")
    chapters = relationship("Chapter", back_populates="subject")

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    subject_id = Column(String, ForeignKey("subjects.id"))
    
    # Relationships
    subject = relationship("Subject", back_populates="chapters")
    topics = relationship("Topic", back_populates="chapter")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    chapter_id = Column(String, ForeignKey("chapters.id"))
    subtopics = Column(JSON, default=[])
    
    # Relationships
    chapter = relationship("Chapter", back_populates="topics")
    questions = relationship("Question", back_populates="topic")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(String, primary_key=True, index=True)
    type = Column(String, index=True)  # mcq, short, long, image
    text = Column(Text)
    options = Column(JSON, default=[])
    correct_answer = Column(JSON, default=[])
    explanation = Column(Text)
    images = Column(JSON, default=[])
    difficulty = Column(String, index=True)  # easy, medium, hard
    marks = Column(Integer, default=1)
    topic_id = Column(String, ForeignKey("topics.id"))
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    topic = relationship("Topic", back_populates="questions")
    user = relationship("User", back_populates="questions")

class Worksheet(Base):
    __tablename__ = "worksheets"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    topic_id = Column(String, ForeignKey("topics.id"))
    user_id = Column(String, ForeignKey("users.id"))
    question_ids = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="worksheets")

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    question_id = Column(String, ForeignKey("questions.id"))
    worksheet_id = Column(String, ForeignKey("worksheets.id"), nullable=True)
    # Store user's answer as JSON to handle different question types
    user_answer = Column(JSON, default=[])
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    question = relationship("Question")
    worksheet = relationship("Worksheet")

class QuizResult(Base):
    __tablename__ = "quiz_results"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    worksheet_id = Column(String, ForeignKey("worksheets.id"))
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    score_percentage = Column(Integer, default=0)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    worksheet = relationship("Worksheet")

class QuizFeedback(Base):
    __tablename__ = "quiz_feedback"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    worksheet_id = Column(String, ForeignKey("worksheets.id"))
    feedback_type = Column(String, index=True)  # "thumbs_up" or "thumbs_down"
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    worksheet = relationship("Worksheet")