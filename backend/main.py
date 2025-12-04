from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import json
import httpx
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel
import jwt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from database import SessionLocal, engine, Base
import models
import schemas

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize grades if they don't exist
def init_grades():
    db = SessionLocal()
    try:
        # Check if grades already exist
        if db.query(models.Grade).count() == 0:
            # Create grades from 1 to 12
            for i in range(1, 13):
                grade = models.Grade(
                    id=f"grade-{i}",
                    name=f"Grade {i}"
                )
                db.add(grade)
            db.commit()
            print("Grades initialized successfully!")
    finally:
        db.close()

# Initialize grades on startup
init_grades()

app = FastAPI(title="Classroom Canvas API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    # Allow any localhost/127.0.0.1 origin on any port during development
    allow_origins=[],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

security = HTTPBearer()

def verify_token():
    """Development helper: bypass authentication and return a default user id.

    This lets the frontend interact with the API without providing tokens during
    development. If no users exist in the DB, creates a single default user and
    returns its id.
    """
    db = SessionLocal()
    try:
        # Prefer an existing user if present
        user = db.query(models.User).first()
        if user:
            return user.id

        # Create a default user for development
        default_id = "dev-user"
        dev_user = models.User(
            id=default_id,
            username="dev",
            email="dev@example.com",
            hashed_password="dev"
        )
        db.add(dev_user)
        db.commit()
        return default_id
    finally:
        db.close()

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# LLM Service
class LLMService:
    @staticmethod
    async def generate_questions(prompt: str) -> List[dict]:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert educational content creator. Generate high-quality questions based on the given topic and requirements. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error generating questions: {response.text}"
                )
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            print(f"DEBUG: Raw LLM Response: {content}")
            
            # Parse the LLM response to extract questions
            # This is a simplified version - in production, you'd want more robust parsing
            try:
                # First, try to parse the entire content as JSON
                questions = json.loads(content)
                print(f"DEBUG: Successfully parsed JSON. Questions count: {len(questions) if isinstance(questions, list) else 1}")
                if isinstance(questions, dict):
                    questions = [questions]
                
                # Check if any image-based questions were generated
                image_questions = [q for q in questions if q.get("type") == "image"]
                print(f"DEBUG: Found {len(image_questions)} image-based questions")
                
                return questions
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON parse error: {str(e)}")
                # If the response is not valid JSON, try to extract JSON from the text
                import re
                
                # Try to find JSON array
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    try:
                        questions = json.loads(json_match.group(0))
                        print(f"DEBUG: Successfully extracted JSON array. Questions count: {len(questions)}")
                        return questions
                    except json.JSONDecodeError as e2:
                        print(f"DEBUG: Failed to parse extracted JSON: {str(e2)}")
                
                # Try to find JSON object
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        question = json.loads(json_match.group(0))
                        print(f"DEBUG: Successfully extracted JSON object")
                        return [question]
                    except json.JSONDecodeError as e3:
                        print(f"DEBUG: Failed to parse extracted JSON object: {str(e3)}")
                
                print(f"DEBUG: No valid JSON found in response: {content[:500]}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to parse LLM response. Raw response: {content[:200]}"
                )
            except Exception as e:
                print(f"DEBUG: Unexpected error during JSON parsing: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Unexpected error during JSON parsing: {str(e)}"
                )

# API Endpoints

@app.get("/")
async def root():
    return {"message": "Classroom Canvas API"}

@app.post("/api/auth/register", response_model=schemas.Token)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Create new user
        import uuid
        hashed_password = user.password  # In production, hash the password
        db_user = models.User(
            id=str(uuid.uuid4()),
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@app.post("/api/auth/login", response_model=schemas.Token)
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        # Authenticate user
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if not db_user or db_user.hashed_password != user.password:  # In production, verify hashed password
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )

@app.get("/api/auth/me", response_model=schemas.User)
async def get_current_user(
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        # `verify_token` returns the user's id now, so query by id
        user = db.query(models.User).filter(models.User.id == current_user).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user: {str(e)}"
        )

@app.get("/api/grades", response_model=List[schemas.Grade])
async def get_grades(db: Session = Depends(get_db)):
    print("DEBUG: GET /api/grades called")
    grades = db.query(models.Grade).all()
    return grades

@app.get("/api/grades/{grade_id}/subjects", response_model=List[schemas.Subject])
async def get_subjects_by_grade(grade_id: str, db: Session = Depends(get_db)):
    print(f"DEBUG: GET /api/grades/{grade_id}/subjects called")
    subjects = db.query(models.Subject).filter(models.Subject.grade_id == grade_id).all()
    return subjects

@app.get("/api/subjects", response_model=List[schemas.Subject])
async def get_subjects(db: Session = Depends(get_db)):
    print("DEBUG: GET /api/subjects called")
    subjects = db.query(models.Subject).all()
    return subjects

@app.get("/api/subjects/{subject_id}/chapters", response_model=List[schemas.Chapter])
async def get_chapters(subject_id: str, db: Session = Depends(get_db)):
    print(f"DEBUG: GET /api/subjects/{subject_id}/chapters called")
    chapters = db.query(models.Chapter).filter(models.Chapter.subject_id == subject_id).all()
    return chapters

@app.get("/api/chapters/{chapter_id}/topics", response_model=List[schemas.Topic])
async def get_topics(chapter_id: str, db: Session = Depends(get_db)):
    print(f"DEBUG: GET /api/chapters/{chapter_id}/topics called")
    topics = db.query(models.Topic).filter(models.Topic.chapter_id == chapter_id).all()
    return topics

@app.get("/api/subjects/{subject_id}/chapters", response_model=List[schemas.Chapter])
async def get_chapters(subject_id: str, db: Session = Depends(get_db)):
    chapters = db.query(models.Chapter).filter(models.Chapter.subject_id == subject_id).all()
    return chapters

@app.get("/api/chapters/{chapter_id}/topics", response_model=List[schemas.Topic])
async def get_topics(chapter_id: str, db: Session = Depends(get_db)):
    topics = db.query(models.Topic).filter(models.Topic.chapter_id == chapter_id).all()
    return topics

@app.post("/api/generate-worksheet", response_model=List[schemas.Question])
async def generate_worksheet(
    worksheet_request: schemas.WorksheetRequest,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        # Get the topic details
        topic = db.query(models.Topic).filter(models.Topic.id == worksheet_request.topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        
        # Get the chapter and subject details
        chapter = db.query(models.Chapter).filter(models.Chapter.id == topic.chapter_id).first()
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
            
        subject = db.query(models.Subject).filter(models.Subject.id == chapter.subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Construct prompt for LLM
        prompt = f"""
        Generate educational questions for a worksheet with the following details:
        
        Subject: {subject.name}
        Chapter: {chapter.name}
        Topic: {topic.name}
        Subtopics: {', '.join(topic.subtopics)}
        
        Generate the following types of questions:
        - Multiple Choice Questions (MCQ): {worksheet_request.mcq_count}
        - Short Answer Questions: {worksheet_request.short_answer_count}
        - Long Answer Questions: {worksheet_request.long_answer_count}
        
        Difficulty level: {worksheet_request.difficulty}
        
        For each question, provide the following JSON structure (IMPORTANT):
        {{
            "type": "mcq" | "short" | "long" | "image",
            "text": "The question text here",
            "options": ["option1", "option2", "option3", "option4"] (for MCQ and image-based questions),
            "correct_answer": "answer text or option index",
            "explanation": "explanation of the answer",
            "images": ["https://example.com/image1.jpg"] (include placeholder image URLs if include_images is true),
            "difficulty": "easy" | "medium" | "hard",
            "marks": 1 (or higher)
        }}
        
        Include images: {worksheet_request.include_images}
        
        {"CRITICAL INSTRUCTION": If include_images is true, you MUST create at least 1-2 image-based questions that require analyzing a diagram, chart, or image. These questions should have "type": "image" and include placeholder image URLs in the "images" field.}
        
        If include_images is false, generate only regular text-based questions (mcq, short, long).
        
        {"MANDATORY FORMAT": Respond with ONLY a valid JSON array of question objects, nothing else.}
        Example format:
        [
            {{"type": "mcq", "text": "Question 1?", "options": ["A", "B", "C", "D"], "correct_answer": 0, "explanation": "Because...", "difficulty": "easy", "marks": 1}},
            {{"type": "image", "text": "Analyze the diagram and answer:", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_answer": 0, "explanation": "Because...", "images": ["https://example.com/diagram.jpg"], "difficulty": "medium", "marks": 3}},
            {{"type": "short", "text": "Question 3?", "options": [], "correct_answer": "answer", "explanation": "Because...", "difficulty": "medium", "marks": 2}}
        ]
        """
        
        # Generate questions using LLM
        try:
            generated_questions = await LLMService.generate_questions(prompt)
            print(f"DEBUG: Generated questions data: {generated_questions}")
        except Exception as e:
            print(f"DEBUG: LLM generation failed: {str(e)}")
            print(f"DEBUG: Using fallback mock data for testing")
            # Fallback mock data for testing
            # Include an image-based question if include_images is true
            if worksheet_request.include_images:
                generated_questions = [
                    {
                        "type": "mcq",
                        "text": "What is the capital of France?",
                        "options": ["London", "Berlin", "Paris", "Madrid"],
                        "correct_answer": 2,
                        "explanation": "Paris is the capital of France.",
                        "difficulty": "easy",
                        "marks": 1
                    },
                    {
                        "type": "image",
                        "text": "Analyze the diagram of a plant cell and identify the organelle responsible for photosynthesis.",
                        "options": ["Mitochondria", "Nucleus", "Chloroplast", "Vacuole"],
                        "correct_answer": 2,
                        "explanation": "Chloroplasts are the organelles responsible for photosynthesis in plant cells.",
                        "images": ["https://example.com/plant-cell.jpg"],
                        "difficulty": "medium",
                        "marks": 3
                    },
                    {
                        "type": "short",
                        "text": "Define photosynthesis.",
                        "options": [],
                        "correct_answer": "Process by which plants convert light into chemical energy",
                        "explanation": "Photosynthesis is the process where plants use sunlight to produce glucose.",
                        "difficulty": "medium",
                        "marks": 2
                    }
                ]
            else:
                generated_questions = [
                    {
                        "type": "mcq",
                        "text": "What is the capital of France?",
                        "options": ["London", "Berlin", "Paris", "Madrid"],
                        "correct_answer": 2,
                        "explanation": "Paris is the capital of France.",
                        "difficulty": "easy",
                        "marks": 1
                    },
                    {
                        "type": "short",
                        "text": "Define photosynthesis.",
                        "options": [],
                        "correct_answer": "Process by which plants convert light into chemical energy",
                        "explanation": "Photosynthesis is the process where plants use sunlight to produce glucose.",
                        "difficulty": "medium",
                        "marks": 2
                    }
                ]
        
        # Save generated questions to database
        saved_questions = []
        for idx, q_data in enumerate(generated_questions):
            try:
                # Handle different field name variations
                text = q_data.get("text") or q_data.get("question") or q_data.get("question_text")
                if not text:
                    print(f"DEBUG: Question {idx} missing text field. Data: {q_data}")
                    raise ValueError("Missing question text field")
                
                question = models.Question(
                    id=str(uuid.uuid4()),
                    type=q_data.get("type", "mcq"),
                    text=text,
                    options=q_data.get("options", q_data.get("choices", [])),
                    correct_answer=q_data.get("correct_answer", q_data.get("answer")),
                    explanation=q_data.get("explanation", ""),
                    images=q_data.get("images", []),
                    difficulty=q_data.get("difficulty", "medium"),
                    marks=q_data.get("marks", 1),
                    topic_id=worksheet_request.topic_id,
                    user_id=current_user
                )
                db.add(question)
                db.commit()
                db.refresh(question)
                saved_questions.append(question)
                print(f"DEBUG: Successfully created question {idx}")
            except Exception as e:
                print(f"DEBUG: Error processing question {idx}: {q_data}, Error: {str(e)}")
                continue
        
        print(f"DEBUG: Total saved questions: {len(saved_questions)}")
        
        if not saved_questions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate any valid questions. Please check the LLM response format."
            )
        
        return saved_questions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating worksheet: {str(e)}"
        )

@app.get("/api/questions", response_model=List[schemas.Question])
async def get_questions(
    topic_id: Optional[str] = None,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(models.Question).filter(models.Question.user_id == current_user)
        if topic_id:
            query = query.filter(models.Question.topic_id == topic_id)
        questions = query.all()
        return questions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching questions: {str(e)}"
        )

@app.get("/api/questions/{question_id}", response_model=schemas.Question)
async def get_question(
    question_id: str,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        question = db.query(models.Question).filter(
            models.Question.id == question_id,
            models.Question.user_id == current_user
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        return question
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching question: {str(e)}"
        )

@app.post("/api/worksheets", response_model=schemas.Worksheet)
async def save_worksheet(
    worksheet: schemas.WorksheetCreate,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        # Validate that the topic exists
        topic = db.query(models.Topic).filter(models.Topic.id == worksheet.topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
        
        # Validate that all questions exist and belong to the user
        for question_id in worksheet.question_ids:
            question = db.query(models.Question).filter(
                models.Question.id == question_id,
                models.Question.user_id == current_user
            ).first()
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Question with ID {question_id} not found or does not belong to the user"
                )
        
        # Create new worksheet
        db_worksheet = models.Worksheet(
            id=str(uuid.uuid4()),
            name=worksheet.name,
            topic_id=worksheet.topic_id,
            user_id=current_user,
            question_ids=worksheet.question_ids
        )
        db.add(db_worksheet)
        db.commit()
        db.refresh(db_worksheet)
        
        return db_worksheet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving worksheet: {str(e)}"
        )

@app.get("/api/worksheets", response_model=List[schemas.Worksheet])
async def get_worksheets(
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        worksheets = db.query(models.Worksheet).filter(models.Worksheet.user_id == current_user).all()
        return worksheets
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching worksheets: {str(e)}"
        )

@app.get("/api/worksheets/{worksheet_id}", response_model=schemas.Worksheet)
async def get_worksheet(
    worksheet_id: str,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        worksheet = db.query(models.Worksheet).filter(
            models.Worksheet.id == worksheet_id,
            models.Worksheet.user_id == current_user
        ).first()
        
        if not worksheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worksheet not found"
            )
        
        return worksheet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching worksheet: {str(e)}"
        )

@app.delete("/api/worksheets/{worksheet_id}")
async def delete_worksheet(
    worksheet_id: str,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        worksheet = db.query(models.Worksheet).filter(
            models.Worksheet.id == worksheet_id,
            models.Worksheet.user_id == current_user
        ).first()
        
        if not worksheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worksheet not found"
            )
        
        db.delete(worksheet)
        db.commit()
        
        return {"message": "Worksheet deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting worksheet: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=debug)