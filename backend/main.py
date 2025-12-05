# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy.orm import Session
# from typing import List, Optional
# import os
# import json
# import httpx
# import uuid
# from datetime import datetime, timedelta
# from pydantic import BaseModel
# import jwt
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# from database import SessionLocal, engine, Base
# import models
# import schemas

# # Create database tables
# Base.metadata.create_all(bind=engine)

# # Initialize grades if they don't exist
# def init_grades():
#     db = SessionLocal()
#     try:
#         # Check if grades already exist
#         if db.query(models.Grade).count() == 0:
#             # Create grades from 1 to 12
#             for i in range(1, 13):
#                 grade = models.Grade(
#                     id=f"grade-{i}",
#                     name=f"Grade {i}"
#                 )
#                 db.add(grade)
#             db.commit()
#             print("Grades initialized successfully!")
#     finally:
#         db.close()

# # Initialize grades on startup
# init_grades()

# app = FastAPI(title="Classroom Canvas API", version="1.0.0")

# # CORS configuration
# app.add_middleware(
#     CORSMiddleware,
#     # Allow any localhost/127.0.0.1 origin on any port during development
#     allow_origins=[],
#     allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Security
# SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
# ALGORITHM = os.getenv("ALGORITHM", "HS256")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


# # Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # JWT functions
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# security = HTTPBearer()

# def verify_token():
#     """Development helper: bypass authentication and return a default user id.

#     This lets the frontend interact with the API without providing tokens during
#     development. If no users exist in the DB, creates a single default user and
#     returns its id.
#     """
#     db = SessionLocal()
#     try:
#         # Prefer an existing user if present
#         user = db.query(models.User).first()
#         if user:
#             return user.id

#         # Create a default user for development
#         default_id = "dev-user"
#         dev_user = models.User(
#             id=default_id,
#             username="dev",
#             email="dev@example.com",
#             hashed_password="dev"
#         )
#         db.add(dev_user)
#         db.commit()
#         return default_id
#     finally:
#         db.close()

# # OpenRouter API configuration
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key")
# OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# # Image generation is now handled by Gemini (multimodal model)

# # LLM Service
# class LLMService:
#     @staticmethod
#     async def generate_image(prompt: str) -> str:
#         """Generate an image using Gemini's multimodal capabilities."""
#         headers = {
#             "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#             "Content-Type": "application/json"
#         }
        
#         payload = {
#             "model": "google/gemini-2.0-flash-exp:free",
#             "messages": [
#                 {
#                     "role": "system",
#                     "content": "You are an expert educational image generator. Create clear, educational diagrams and images based on the given prompt. Return the images which are generated."
#                 },
#                 {
#                     "role": "user",
#                     "content": f"Generate an educational image for this prompt: {prompt}. Please provide generated images that can be used in a worksheet."
#                 }
#             ]
#         }
        
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)
#                 if response.status_code != 200:
#                     print(f"Error generating image with Gemini: {response.text}")
#                     # Return a placeholder URL if image generation fails
#                     return "https://picsum.photos/seed/placeholder/1024/1024.jpg"
                
#                 result = response.json()
#                 content = result["choices"][0]["message"]["content"]
                
#                 # Try to extract URL from the response
#                 import re
#                 url_match = re.search(r'https?://[^\s<>"{}|\\^`\[\]]+', content)
#                 if url_match:
#                     image_url = url_match.group(0)
#                     print(f"Generated image URL with Gemini: {image_url}")
#                     return image_url
#                 else:
#                     print(f"No URL found in Gemini response: {content}")
#                     return "https://picsum.photos/seed/gemini-fallback/1024/1024.jpg"
#         except Exception as e:
#             print(f"Exception during image generation with Gemini: {str(e)}")
#             # Return a placeholder URL if there's an exception
#             return "https://picsum.photos/seed/gemini-error/1024/1024.jpg"
    
#     @staticmethod
#     async def generate_questions(prompt: str, generate_real_images: bool = False) -> List[dict]:
#         headers = {
#             "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#             "Content-Type": "application/json"
#         }
        
#         payload = {
#             "model": "google/gemini-2.0-flash-exp:free",
#             "messages": [
#                 {
#                     "role": "system",
#                     "content": "You are an expert educational content creator. Generate high-quality questions based on the given topic and requirements. Always respond with valid JSON only."
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ]
#         }
        
#         async with httpx.AsyncClient() as client:
#             response = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)
#             if response.status_code != 200:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Error generating questions: {response.text}"
#                 )
            
#             result = response.json()
#             content = result["choices"][0]["message"]["content"]
            
#             print(f"DEBUG: Raw LLM Response: {content}")
#             print(f"DEBUG: Include images flag: {worksheet_request.include_images}")
#             print(f"DEBUG: Generate real images flag: {generate_real_images}")
            
#             # Parse the LLM response to extract questions
#             # This is a simplified version - in production, you'd want more robust parsing
#             try:
#                 # First, try to parse the entire content as JSON
#                 questions = json.loads(content)
#                 print(f"DEBUG: Successfully parsed JSON. Questions count: {len(questions) if isinstance(questions, list) else 1}")
#                 if isinstance(questions, dict):
#                     questions = [questions]
                
#                 # Check if any image-based questions were generated
#                 image_questions = [q for q in questions if q.get("type") == "image"]
#                 print(f"DEBUG: Found {len(image_questions)} image-based questions")
                
#                 # If generate_real_images is True and there are image-based questions, generate actual images
#                 if generate_real_images and image_questions:
#                     for question in image_questions:
#                         if "images" in question and question["images"]:
#                             # Generate actual images for each image description
#                             for i, image_description in enumerate(question["images"]):
#                                 # Use the image description directly as the prompt
#                                 image_prompt = f"Create a clear, educational image: {image_description}"
#                                 print(f"Generating image with Gemini using prompt: {image_prompt}")
                                
#                                 # Generate the actual image using Gemini
#                                 actual_image_url = await LLMService.generate_image(image_prompt)
#                                 question["images"][i] = actual_image_url
                
#                 return questions
#             except json.JSONDecodeError as e:
#                 print(f"DEBUG: JSON parse error: {str(e)}")
#                 # If the response is not valid JSON, try to extract JSON from the text
#                 import re
                
#                 # Try to find JSON array
#                 json_match = re.search(r'\[.*\]', content, re.DOTALL)
#                 if json_match:
#                     try:
#                         questions = json.loads(json_match.group(0))
#                         print(f"DEBUG: Successfully extracted JSON array. Questions count: {len(questions)}")
#                         return questions
#                     except json.JSONDecodeError as e2:
#                         print(f"DEBUG: Failed to parse extracted JSON: {str(e2)}")
                
#                 # Try to find JSON object
#                 json_match = re.search(r'\{.*\}', content, re.DOTALL)
#                 if json_match:
#                     try:
#                         question = json.loads(json_match.group(0))
#                         print(f"DEBUG: Successfully extracted JSON object")
#                         return [question]
#                     except json.JSONDecodeError as e3:
#                         print(f"DEBUG: Failed to parse extracted JSON object: {str(e3)}")
                
#                 print(f"DEBUG: No valid JSON found in response: {content[:500]}")
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Failed to parse LLM response. Raw response: {content[:200]}"
#                 )
#             except Exception as e:
#                 print(f"DEBUG: Unexpected error during JSON parsing: {str(e)}")
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Unexpected error during JSON parsing: {str(e)}"
#                 )

# # API Endpoints

# @app.get("/")
# async def root():
#     return {"message": "Classroom Canvas API"}

# @app.post("/api/auth/register", response_model=schemas.Token)
# async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     try:
#         # Check if user already exists
#         db_user = db.query(models.User).filter(models.User.username == user.username).first()
#         if db_user:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Username already registered"
#             )
        
#         # Create new user
#         import uuid
#         hashed_password = user.password  # In production, hash the password
#         db_user = models.User(
#             id=str(uuid.uuid4()),
#             username=user.username,
#             email=user.email,
#             hashed_password=hashed_password
#         )
#         db.add(db_user)
#         db.commit()
#         db.refresh(db_user)
        
#         # Create access token
#         access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         access_token = create_access_token(
#             data={"sub": user.username}, expires_delta=access_token_expires
#         )
        
#         return {"access_token": access_token, "token_type": "bearer"}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error creating user: {str(e)}"
#         )

# @app.post("/api/auth/login", response_model=schemas.Token)
# async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
#     try:
#         # Authenticate user
#         db_user = db.query(models.User).filter(models.User.username == user.username).first()
#         if not db_user or db_user.hashed_password != user.password:  # In production, verify hashed password
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Incorrect username or password",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
        
#         # Create access token
#         access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         access_token = create_access_token(
#             data={"sub": user.username}, expires_delta=access_token_expires
#         )
        
#         return {"access_token": access_token, "token_type": "bearer"}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error during login: {str(e)}"
#         )

# @app.get("/api/auth/me", response_model=schemas.User)
# async def get_current_user(
#     current_user: str = Depends(verify_token),
#     db: Session = Depends(get_db)
# ):
#     try:
#         # `verify_token` returns the user's id now, so query by id
#         user = db.query(models.User).filter(models.User.id == current_user).first()
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found"
#             )
#         return user
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error getting user: {str(e)}"
#         )

# @app.get("/api/grades", response_model=List[schemas.Grade])
# async def get_grades(db: Session = Depends(get_db)):
#     print("DEBUG: GET /api/grades called")
#     grades = db.query(models.Grade).all()
#     return grades

# @app.get("/api/grades/{grade_id}/subjects", response_model=List[schemas.Subject])
# async def get_subjects_by_grade(grade_id: str, db: Session = Depends(get_db)):
#     print(f"DEBUG: GET /api/grades/{grade_id}/subjects called")
#     subjects = db.query(models.Subject).filter(models.Subject.grade_id == grade_id).all()
#     return subjects

# @app.get("/api/subjects", response_model=List[schemas.Subject])
# async def get_subjects(db: Session = Depends(get_db)):
#     print("DEBUG: GET /api/subjects called")
#     subjects = db.query(models.Subject).all()
#     return subjects

# @app.get("/api/subjects/{subject_id}/chapters", response_model=List[schemas.Chapter])
# async def get_chapters(subject_id: str, db: Session = Depends(get_db)):
#     print(f"DEBUG: GET /api/subjects/{subject_id}/chapters called")
#     chapters = db.query(models.Chapter).filter(models.Chapter.subject_id == subject_id).all()
#     return chapters

# @app.get("/api/chapters/{chapter_id}/topics", response_model=List[schemas.Topic])
# async def get_topics(chapter_id: str, db: Session = Depends(get_db)):
#     print(f"DEBUG: GET /api/chapters/{chapter_id}/topics called")
#     topics = db.query(models.Topic).filter(models.Topic.chapter_id == chapter_id).all()
#     return topics

# @app.get("/api/subjects/{subject_id}/chapters", response_model=List[schemas.Chapter])
# async def get_chapters(subject_id: str, db: Session = Depends(get_db)):
#     chapters = db.query(models.Chapter).filter(models.Chapter.subject_id == subject_id).all()
#     return chapters

# @app.get("/api/chapters/{chapter_id}/topics", response_model=List[schemas.Topic])
# async def get_topics(chapter_id: str, db: Session = Depends(get_db)):
#     topics = db.query(models.Topic).filter(models.Topic.chapter_id == chapter_id).all()
#     return topics

# @app.post("/api/generate-worksheet", response_model=List[schemas.Question])
# async def generate_worksheet(
#     worksheet_request: schemas.WorksheetRequest,
#     current_user: str = Depends(verify_token),
#     db: Session = Depends(get_db)
# ):
#     try:
#         # Get the topic details
#         topic = db.query(models.Topic).filter(models.Topic.id == worksheet_request.topic_id).first()
#         if not topic:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Topic not found"
#             )
        
#         # Get the chapter and subject details
#         chapter = db.query(models.Chapter).filter(models.Chapter.id == topic.chapter_id).first()
#         if not chapter:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Chapter not found"
#             )
            
#         subject = db.query(models.Subject).filter(models.Subject.id == chapter.subject_id).first()
#         if not subject:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Subject not found"
#             )
        
#         # Construct prompt for LLM
#         prompt = f"""
#         Generate educational questions for a worksheet with the following details:
        
#         Subject: {subject.name}
#         Chapter: {chapter.name}
#         Topic: {topic.name}
#         Subtopics: {', '.join(topic.subtopics)}
        
#         Generate the following types of questions:
#         - Multiple Choice Questions (MCQ): {worksheet_request.mcq_count}
#         - Short Answer Questions: {worksheet_request.short_answer_count}
#         - Long Answer Questions: {worksheet_request.long_answer_count}
        
#         Difficulty level: {worksheet_request.difficulty}
        
#         For each question, provide the following JSON structure (IMPORTANT):
#         {{
#             "type": "mcq" | "short" | "long" | "image",
#             "text": "The question text here",
#             "options": ["option1", "option2", "option3", "option4"] (for MCQ and image-based questions),
#             "correct_answer": "answer text or option index",
#             "explanation": "explanation of the answer",
#             "images": ["https://example.com/image1.jpg"] (for image-based questions, include a brief description of the image to generate),
#             "difficulty": "easy" | "medium" | "hard",
#             "marks": 1 (or higher)
#         }}
        
#         Include images: {worksheet_request.include_images}
        
#         {"CRITICAL INSTRUCTION": If include_images is true, you MUST create at least 1-2 image-based questions that require analyzing a diagram, chart, or image. These questions should have "type": "image" and include a detailed description of the educational image to be generated in the "images" field. For example: "A detailed diagram of a plant cell showing all major organelles with labels."}
        
#         If include_images is false, generate only regular text-based questions (mcq, short, long).
        
#         {"MANDATORY FORMAT": Respond with ONLY a valid JSON array of question objects, nothing else.}
#         Example format:
#         [
#             {{"type": "mcq", "text": "Question 1?", "options": ["A", "B", "C", "D"], "correct_answer": 0, "explanation": "Because...", "difficulty": "easy", "marks": 1}},
#             {{"type": "image", "text": "Analyze the diagram and answer:", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_answer": 0, "explanation": "Because...", "images": ["https://example.com/diagram.jpg"], "difficulty": "medium", "marks": 3}},
#             {{"type": "short", "text": "Question 3?", "options": [], "correct_answer": "answer", "explanation": "Because...", "difficulty": "medium", "marks": 2}}
#         ]
#         """
        
#         # Generate questions using LLM
#         try:
#             generated_questions = await LLMService.generate_questions(prompt, worksheet_request.generate_real_images)
#             print(f"DEBUG: Generated questions data: {generated_questions}")
#         except Exception as e:
#             print(f"DEBUG: LLM generation failed: {str(e)}")
#             print(f"DEBUG: Using fallback mock data for testing")
#             print(f"DEBUG: Include images flag in fallback: {worksheet_request.include_images}")
#             # Fallback mock data for testing
#             # Include an image-based question if include_images is true
#             if worksheet_request.include_images:
#                 generated_questions = [
#                     {
#                         "type": "mcq",
#                         "text": "What is the capital of France?",
#                         "options": ["London", "Berlin", "Paris", "Madrid"],
#                         "correct_answer": 2,
#                         "explanation": "Paris is the capital of France.",
#                         "difficulty": "easy",
#                         "marks": 1
#                     },
#                     {
#                         "type": "image",
#                         "text": "Analyze the diagram of a plant cell and identify the organelle responsible for photosynthesis.",
#                         "options": ["Mitochondria", "Nucleus", "Chloroplast", "Vacuole"],
#                         "correct_answer": 2,
#                         "explanation": "Chloroplasts are the organelles responsible for photosynthesis in plant cells.",
#                         "images": ["A detailed diagram of a plant cell showing all major organelles with clear labels, highlighting the chloroplasts in green."],
#                         "difficulty": "medium",
#                         "marks": 3
#                     },
#                     {
#                         "type": "short",
#                         "text": "Define photosynthesis.",
#                         "options": [],
#                         "correct_answer": "Process by which plants convert light into chemical energy",
#                         "explanation": "Photosynthesis is the process where plants use sunlight to produce glucose.",
#                         "difficulty": "medium",
#                         "marks": 2
#                     }
#                 ]
#             else:
#                 generated_questions = [
#                     {
#                         "type": "mcq",
#                         "text": "What is the capital of France?",
#                         "options": ["London", "Berlin", "Paris", "Madrid"],
#                         "correct_answer": 2,
#                         "explanation": "Paris is the capital of France.",
#                         "difficulty": "easy",
#                         "marks": 1
#                     },
#                     {
#                         "type": "short",
#                         "text": "Define photosynthesis.",
#                         "options": [],
#                         "correct_answer": "Process by which plants convert light into chemical energy",
#                         "explanation": "Photosynthesis is the process where plants use sunlight to produce glucose.",
#                         "difficulty": "medium",
#                         "marks": 2
#                     }
#                 ]
        
#         # Save generated questions to database
#         saved_questions = []
#         for idx, q_data in enumerate(generated_questions):
#             print(f"DEBUG: Processing question {idx}: {q_data}")
#             try:
#                 # Handle different field name variations
#                 text = q_data.get("text") or q_data.get("question") or q_data.get("question_text")
#                 if not text:
#                     print(f"DEBUG: Question {idx} missing text field. Data: {q_data}")
#                     raise ValueError("Missing question text field")
                
#                 question = models.Question(
#                     id=str(uuid.uuid4()),
#                     type=q_data.get("type", "mcq"),
#                     text=text,
#                     options=q_data.get("options", q_data.get("choices", [])),
#                     correct_answer=q_data.get("correct_answer", q_data.get("answer")),
#                     explanation=q_data.get("explanation", ""),
#                     images=q_data.get("images", []),
#                     difficulty=q_data.get("difficulty", "medium"),
#                     marks=q_data.get("marks", 1),
#                     topic_id=worksheet_request.topic_id,
#                     user_id=current_user
#                 )
#                 db.add(question)
#                 db.commit()
#                 db.refresh(question)
#                 saved_questions.append(question)
#                 print(f"DEBUG: Successfully created question {idx}")
#             except Exception as e:
#                 print(f"DEBUG: Error processing question {idx}: {q_data}, Error: {str(e)}")
#                 continue
        
#         print(f"DEBUG: Total saved questions: {len(saved_questions)}")
        
#         if not saved_questions:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to generate any valid questions. Please check the LLM response format."
#             )
        
#         return saved_questions
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error generating worksheet: {str(e)}"
#         )

# @app.get("/api/questions", response_model=List[schemas.Question])
# async def get_questions(
#     topic_id: Optional[str] = None,
#     current_user: str = Depends(verify_token),
#     db: Session = Depends(get_db)
# ):
#     try:
#         query = db.query(models.Question).filter(models.Question.user_id == current_user)
#         if topic_id:
#             query = query.filter(models.Question.topic_id == topic_id)
#         questions = query.all()
#         return questions
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching questions: {str(e)}"
#         )

# @app.get("/api/questions/{question_id}", response_model=schemas.Question)
# async def get_question(
#     question_id: str,
#     current_user: str = Depends(verify_token),
#     db: Session = Depends(get_db)
# ):
#     try:
#         question = db.query(models.Question).filter(
#             models.Question.id == question_id,
#             models.Question.user_id == current_user
#         ).first()
        
#         if not question:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Question not found"
#             )
        
#         return question
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching question: {str(e)}"
#         )

# @app.post("/api/worksheets", response_model=schemas.Worksheet)
# async def save_worksheet(
#     worksheet: schemas.WorksheetCreate,
#     current_user: str = Depends(verify_token),
#     db: Session = Depends(get_db)
# ):
#     try:
#         # Validate that the topic exists
#         topic = db.query(models.Topic).filter(models.Topic.id == worksheet.topic_id).first()
#         if not topic:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Topic not found"
#             )
        
#         # Validate that all questions exist and belong to the user
#         for question_id in worksheet.question_ids:
#             question = db.query(models.Question).filter(
#                 models.Question.id == question_id,
#                 models.Question.user_id == current_user
#             ).first()
#             if not question:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail=f"Question with ID {question_id} not found or does not belong to the user"
#                 )
        
#         # Create new worksheet
#         db_worksheet = models.Worksheet(
#             id=str(uuid.uuid4()),
#             name=worksheet.name,
#             topic_id=worksheet.topic_id,
#             user_id=current_user,
#             question_ids=worksheet.question_ids
#         )
#         db.add(db_worksheet)
#         db.commit()
#         db.refresh(db_worksheet)
        
#         return db_worksheet
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error saving worksheet: {str(e)}"
#         )

# @app.get("/api/worksheets", response_model=List[schemas.Worksheet])
# async def get_worksheets(
#     current_user: str = Depends(verify_token),
#     db: Session = Depends(get_db)
# ):
#     try:
#         worksheets = db.query(models.Worksheet).filter(models.Worksheet.user_id == current_user).all()
#         return worksheets
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching worksheets: {str(e)}"
#         )

# @app.get("/api/worksheets/{worksheet_id}", response_model=schemas.Worksheet)
# async def get_worksheet(
#     worksheet_id: str,
#     current_user: str = Depends(verify_token),
#     db: Session = Depends(get_db)
# ):
#     try:
#         worksheet = db.query(models.Worksheet).filter(
#             models.Worksheet.id == worksheet_id,
#             models.Worksheet.user_id == current_user
#         ).first()
        
#         if not worksheet:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Worksheet not found"
#             )
        
#         return worksheet
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching worksheet: {str(e)}"
#         )

# @app.delete("/api/worksheets/{worksheet_id}")
# async def delete_worksheet(
#     worksheet_id: str,
#     current_user: str = Depends(verify_token),
#     db: Session = Depends(get_db)
# ):
#     try:
#         worksheet = db.query(models.Worksheet).filter(
#             models.Worksheet.id == worksheet_id,
#             models.Worksheet.user_id == current_user
#         ).first()
        
#         if not worksheet:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Worksheet not found"
#             )
        
#         db.delete(worksheet)
#         db.commit()
        
#         return {"message": "Worksheet deleted successfully"}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error deleting worksheet: {str(e)}"
#         )

# if __name__ == "__main__":
#     import uvicorn
#     host = os.getenv("HOST", "0.0.0.0")
#     port = int(os.getenv("PORT", "8000"))
#     debug = os.getenv("DEBUG", "True").lower() == "true"
#     uvicorn.run("main:app", host=host, port=port, reload=debug)

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
    # Dictionary mapping subjects to their specific LLM models
    SUBJECT_LLM_MODELS = {
        "Biology": "mistralai/mistral-7b-instruct:free",
        "Mathematics": "meta/llama-3.3-70b-instruct:free",
        "Chemistry": "nous/hermes-3-405b-instruct:free",
        "Physics": "google/gemma-3-27b:free"
    }
    
    # Default model for subjects not in the dictionary
    DEFAULT_MODEL = "google/gemini-2.0-flash-exp:free"
    
    @staticmethod
    def get_model_for_subject(subject_name: str) -> str:
        """Get the appropriate LLM model for a given subject."""
        # Normalize subject name to handle variations
        normalized_subject = subject_name.lower().strip()
        
        # Check for subject keywords in the subject name
        if "biology" in normalized_subject:
            return LLMService.SUBJECT_LLM_MODELS["Biology"]
        elif "math" in normalized_subject or "mathematics" in normalized_subject:
            return LLMService.SUBJECT_LLM_MODELS["Mathematics"]
        elif "chemistry" in normalized_subject:
            return LLMService.SUBJECT_LLM_MODELS["Chemistry"]
        elif "physics" in normalized_subject:
            return LLMService.SUBJECT_LLM_MODELS["Physics"]
        else:
            # Return default model for other subjects
            return LLMService.DEFAULT_MODEL
    
    @staticmethod
    async def generate_image(prompt: str, subject_name: str = "") -> str:
        """
        Calls OpenRouter with a multimodal model to generate an image from a text prompt.
        The image is returned as a Base64 data URI (data:image/png;base64,...).
        """
        # Using a known OpenRouter model capable of image generation
        IMAGE_MODEL = "google/gemini-2.5-flash-image-preview"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": IMAGE_MODEL,
            "messages": [
                {
                    "role": "user",
                    # Important prompt for educational image generation
                    "content": f"Generate a clear, educational image or diagram for {subject_name} based on this description for a quiz question: {prompt}"
                }
            ],
            # CRITICAL: Enable the image modality for generation
            "modalities": ["image", "text"],
            # Optional: Specify aspect ratio for consistent output
            "image_config": {
                "aspect_ratio": "1:1"
            }
        }
        
        print(f"DEBUG: Calling OpenRouter for image generation with model: {IMAGE_MODEL}")
        
        try:
            # Set a longer timeout for image generation
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)
                
                if response.status_code != 200:
                    print(f"ERROR: Image generation failed. Status: {response.status_code}, Response: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"OpenRouter Image API failed. Status: {response.status_code}. Details: {response.text[:100]}"
                    )
                
                result = response.json()
                
                # CRITICAL: Extract the Base64 data URI from the response structure
                images = result["choices"][0]["message"].get("images")
                
                if not images or not images[0].get("image_url"):
                    print(f"ERROR: Image model returned content but no valid image data.")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Image generation succeeded but returned no Base64 image data."
                    )
                
                base64_data_uri = images[0]["image_url"]["url"]
                
                print("DEBUG: Successfully generated and retrieved Base64 image data.")
                return base64_data_uri
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"EXCEPTION: Image generation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during image generation: {str(e)}"
            )
    
    @staticmethod
    async def generate_questions(prompt: str, subject_name: str = "") -> List[dict]:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Get the appropriate model for the subject
        model = LLMService.get_model_for_subject(subject_name)
        print(f"DEBUG: Using model '{model}' for subject '{subject_name}'")
        
        # Create subject-specific system prompt
        system_prompt = "You are an expert educational content creator."
        
        # Add subject-specific instructions
        if "biology" in subject_name.lower():
            system_prompt += " You specialize in creating accurate biology questions with precise scientific terminology."
        elif "math" in subject_name.lower() or "mathematics" in subject_name.lower():
            system_prompt += " You specialize in creating mathematics questions with clear problem-solving steps and accurate formulas."
        elif "chemistry" in subject_name.lower():
            system_prompt += " You specialize in creating chemistry questions with accurate chemical equations and terminology."
        elif "physics" in subject_name.lower():
            system_prompt += " You specialize in creating physics questions with accurate physical laws and formulas."
        
        system_prompt += " Generate high-quality questions based on the given topic and requirements. Always respond with valid JSON only."
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
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
            try:
                # First, try to parse the entire content as JSON
                questions = json.loads(content)
                print(f"DEBUG: Successfully parsed JSON. Questions count: {len(questions) if isinstance(questions, list) else 1}")
                if isinstance(questions, dict):
                    questions = [questions]
                
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
        
        # Get the subject name for prompt customization
        subject_name = worksheet_request.subject_name or subject.name
        normalized_subject = subject_name.lower().strip()
        
        # Base prompt structure
        prompt_base = f"""
        Generate educational questions for a worksheet with the following details:
        
        Subject: {subject_name}
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
            "images": ["Image Description 1"] (for image-based questions, include a detailed text description of the educational image that needs to be generated),
            "difficulty": "easy" | "medium" | "hard",
            "marks": 1 (or higher)
        }}
        """
        
        # Subject-specific instructions
        subject_instructions = ""
        
        if "biology" in normalized_subject:
            subject_instructions = r"""
            For Biology questions:
            - Focus on biological processes, structures, and terminology
            - Include questions about cell biology, genetics, evolution, ecology, etc.
            - For image-based questions, include diagrams of biological structures (cells, organs, systems)
            - Ensure scientific accuracy in all biological concepts
            - Format all biological terms correctly with proper scientific notation
            - IMPORTANT: Format all biological terms and formulas using LaTeX notation:
              * Use $ for inline equations (e.g., $H_2O$)
              * Use $$ for display equations (e.g., $$C_6H_{12}O_6 + 6O_2 \rightarrow 6CO_2 + 6H_2O$$)
              * Use proper subscripts and superscripts for chemical formulas
            """
        elif "math" in normalized_subject or "mathematics" in normalized_subject:
            subject_instructions = r"""
            For Mathematics questions:
            - Focus on mathematical concepts, formulas, and problem-solving
            - Include questions with equations, graphs, and numerical problems
            - For image-based questions, include graphs, geometric diagrams, or mathematical visualizations
            - Ensure all mathematical formulas and equations are accurate
            - IMPORTANT: Format all mathematical equations using LaTeX notation:
              * Use $ for inline equations (e.g., $x^2 + y^2 = r^2$)
              * Use $$ for display equations (e.g., $$\int_{a}^{b} f(x)dx$$)
              * Use proper Greek letters (e.g., $\alpha$, $\beta$, $\theta$)
              * Use proper mathematical symbols (e.g., $\sum$, $\prod$, $\int$)
            - For solutions, show step-by-step problem-solving process
            - Include units for all numerical answers where appropriate
            """
        elif "chemistry" in normalized_subject:
            subject_instructions = r"""
            For Chemistry questions:
            - Focus on chemical reactions, properties, and terminology
            - Include questions with chemical equations, molecular structures, and periodic table concepts
            - For image-based questions, include molecular diagrams, reaction mechanisms, or chemical structures
            - Ensure all chemical equations and formulas are balanced and accurate
            - IMPORTANT: Format chemical equations using LaTeX notation:
              * Use $ for inline equations (e.g., $H_2O$)
              * Use $$ for display equations (e.g., $$2H_2 + O_2 \rightarrow 2H_2O$$)
              * Use subscripts for numbers (e.g., $H_2O$, $CO_2$)
              * Use superscripts for charges (e.g., $Ca^{2+}$, $Fe^{3+}$)
              * Use proper arrow notation for reactions ($\rightarrow$ for forward, $\leftrightarrow$ for equilibrium)
              * Include state symbols where appropriate ((s), (l), (g), (aq))
            """
        elif "physics" in normalized_subject:
            subject_instructions = r"""
            For Physics questions:
            - Focus on physical laws, formulas, and concepts
            - Include questions with physics equations, diagrams, and problem-solving
            - For image-based questions, include force diagrams, circuit diagrams, or physics visualizations
            - Ensure all physics formulas and concepts are accurate
            - IMPORTANT: Format all physics equations using LaTeX notation:
              * Use $ for inline equations (e.g., $F = ma$)
              * Use $$ for display equations (e.g., $$E = mc^2$$)
              * Use Greek letters for variables ($\alpha$, $\beta$, $\gamma$, $\theta$, etc.)
              * Use proper mathematical symbols ($\int$, $\partial$, $\nabla$, etc.)
              * Include units for all physical quantities where appropriate
              * For vector quantities, use proper vector notation ($\vec{v}$, $|\vec{v}|$, etc.)
            """
        
        # Image instructions
        image_instructions = f"""
        Include images: {worksheet_request.include_images}
        
        {{"CRITICAL INSTRUCTION": If include_images is true, you MUST create at least 1-2 image-based questions that require analyzing a diagram, chart, or image. These questions should have "type": "image" and include a DETAILED TEXT DESCRIPTION of the educational image to be generated in the "images" field.}}
        
        If include_images is false, generate only regular text-based questions (mcq, short, long).
        """
        
        # Format instructions
        format_instructions = """
        {"MANDATORY FORMAT": Respond with ONLY a valid JSON array of question objects, nothing else.}
        Example format:
        [
            {"type": "mcq", "text": "Question 1?", "options": ["A", "B", "C", "D"], "correct_answer": 0, "explanation": "Because...", "difficulty": "easy", "marks": 1}},
            {"type": "image", "text": "Analyze the diagram and answer:", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_answer": 0, "explanation": "Because...", "images": ["A diagram of a plant cell"], "difficulty": "medium", "marks": 3}},
            {"type": "short", "text": "Question 3?", "options": [], "correct_answer": "answer", "explanation": "Because...", "difficulty": "medium", "marks": 2}}
        ]
        """
        
        # Combine all parts of the prompt
        prompt = prompt_base + subject_instructions + image_instructions + format_instructions
        
        # 1. Generate questions structure using the LLM
        try:
            # Use subject_name from the request if provided, otherwise fall back to the database subject
            subject_name = worksheet_request.subject_name or subject.name
            generated_questions = await LLMService.generate_questions(prompt, subject_name)
            print(f"DEBUG: Generated question structures: {generated_questions}")
        except Exception as e:
            # Re-raise LLM error if JSON generation fails
            raise e
        
        # 2. Iterate and generate actual images (Base64) if requested
        if worksheet_request.include_images:
            for q_data in generated_questions:
                if q_data.get("type") == "image" and q_data.get("images"):
                    new_image_data = []
                    # LLM generated a list of text descriptions in q_data["images"].
                    for image_description in q_data["images"]:
                        try:
                            # Call the dedicated image generation function with subject context
                            base64_data_uri = await LLMService.generate_image(image_description, subject_name)
                            new_image_data.append(base64_data_uri)
                        except Exception as e:
                            print(f"ERROR: Image generation failed for prompt '{image_description[:50]}...': {e}")
                            # If image generation fails, clear images for this question
                            new_image_data = []
                            break
                    
                    # Overwrite the text descriptions with the Base64 URI(s)
                    q_data["images"] = new_image_data
        
        # 3. Save generated questions to database
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
                    # images now contains Base64 Data URI strings
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