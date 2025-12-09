from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Union
import os
import json
import httpx
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel  # noqa: F401  (kept in case schemas use it)
import jwt
from dotenv import load_dotenv
import re  # For robust parsing logic

# ---------------------------------------------------------------------------
# Environment & DB setup
# ---------------------------------------------------------------------------

load_dotenv()

from database import SessionLocal, engine, Base  # noqa: E402
import models  # noqa: E402
import schemas  # noqa: E402

# Create database tables
Base.metadata.create_all(bind=engine)


def init_grades() -> None:
    """Initialize Grade table with Grade 1–12 if empty."""
    db = SessionLocal()
    try:
        if db.query(models.Grade).count() == 0:
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

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Security / JWT
# ---------------------------------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def get_db():
    """FastAPI dependency for DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


security = HTTPBearer()


def verify_token():
    """
    Development helper: bypass authentication and return a default user id.

    Lets the frontend interact with the API without providing tokens during
    development. If no users exist in the DB, creates a single default user
    and returns its id.
    """
    db = SessionLocal()
    try:
        user = db.query(models.User).first()
        if user:
            return user.id

        default_id = "dev-user"
        dev_user = models.User(
            id=default_id,
            username="dev",
            email="dev@example.com",
            hashed_password="dev",  # NOTE: not hashed; dev only
        )
        db.add(dev_user)
        db.commit()
        return default_id
    finally:
        db.close()


# ---------------------------------------------------------------------------
# OpenRouter / LLM Service
# ---------------------------------------------------------------------------

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMService:
    """Utility class for calling subject-specific LLMs and image models."""

    SUBJECT_LLM_MODELS = {
        "Biology": "mistralai/mistral-7b-instruct:free",
        "Mathematics": "meta-llama/llama-3.3-70b-instruct:free",
        "Chemistry": "openai/gpt-oss-20b:free",
        "Physics": "google/gemma-3-27b-it:free",
    }
    DEFAULT_MODEL = "google/gemini-2.0-flash-exp:free"

    @staticmethod
    def get_model_for_subject(subject_name: str) -> str:
        """Return an appropriate LLM model name for a given subject."""
        normalized_subject = subject_name.lower().strip()

        if "biology" in normalized_subject:
            return LLMService.SUBJECT_LLM_MODELS.get("Biology", LLMService.DEFAULT_MODEL)
        if "math" in normalized_subject or "mathematics" in normalized_subject:
            return LLMService.SUBJECT_LLM_MODELS.get("Mathematics", LLMService.DEFAULT_MODEL)
        if "chemistry" in normalized_subject:
            return LLMService.SUBJECT_LLM_MODELS.get("Chemistry", LLMService.DEFAULT_MODEL)
        if "physics" in normalized_subject:
            return LLMService.SUBJECT_LLM_MODELS.get("Physics", LLMService.DEFAULT_MODEL)

        return LLMService.DEFAULT_MODEL

    # ------------------------------------------------------------------ #
    # Image generation
    # ------------------------------------------------------------------ #
    @staticmethod
    async def generate_image(prompt: str, subject_name: str = "") -> str:
        """
        Call OpenRouter with a multimodal model to generate an image.

        Returns a Base64 data URI (data:image/png;base64,...).
        """
        IMAGE_MODEL = "google/gemini-2.5-flash-image-preview"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": IMAGE_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Generate a clear, educational image or diagram for {subject_name} "
                        f"based on this description for a quiz question: {prompt}"
                    ),
                }
            ],
            "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": "1:1"},
        }

        print(f"DEBUG: Calling OpenRouter for image generation with model: {IMAGE_MODEL}")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    OPENROUTER_API_URL, json=payload, headers=headers
                )

            if response.status_code != 200:
                print(
                    "ERROR: Image generation failed. "
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=(
                        "OpenRouter Image API failed. "
                        f"Status: {response.status_code}. Details: {response.text[:100]}"
                    ),
                )

            result = response.json()
            images = result["choices"][0]["message"].get("images")

            if not images or not images[0].get("image_url"):
                print("ERROR: Image model returned content but no valid image data.")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Image generation succeeded but returned no Base64 image data.",
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
                detail=f"An unexpected error occurred during image generation: {str(e)}",
            )

    # ------------------------------------------------------------------ #
    # Question generation
    # ------------------------------------------------------------------ #
    @staticmethod
    async def generate_questions(prompt: str, subject_name: str = "") -> List[dict]:
        """Call OpenRouter to generate a JSON list of question dicts."""
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        model = LLMService.get_model_for_subject(subject_name)
        print(f"DEBUG: Using model '{model}' for subject '{subject_name}'")

        system_prompt = (
            "You are an expert educational content creator specializing in generating "
            "rigorous, expression-based questions with detailed mathematical, chemical, "
            "or physical formulations."
        )

        subj_lower = subject_name.lower()
        if "biology" in subj_lower:
            system_prompt += (
                " You specialize in creating biology questions that MUST include biological "
                "processes, molecular structures, quantitative relationships, and detailed "
                "diagrams. NEVER create word-only questions without biological expressions, "
                "formulas, or structural representations."
            )
        elif "math" in subj_lower or "mathematics" in subj_lower:
            system_prompt += (
                " You specialize in creating mathematics questions that MUST include complex "
                "mathematical expressions, multi-step equations, calculus operations, and "
                "rigorous problem-solving. NEVER create word-only questions without actual "
                "mathematical expressions and equations."
            )
        elif "chemistry" in subj_lower:
            system_prompt += (
                " You specialize in creating chemistry questions that MUST include complex "
                "chemical equations, reaction mechanisms, stoichiometric calculations, and "
                "thermodynamic analysis. NEVER create word-only questions without chemical "
                "expressions and equations."
            )
        elif "physics" in subj_lower:
            system_prompt += (
                " You specialize in creating physics questions that MUST include physical "
                "formulas, vector equations, multi-step problem-solving, and real-world "
                "applications. NEVER create word-only questions without physical expressions "
                "and formulas."
            )

        system_prompt += (
            " Generate high-quality, expression-based questions that require analytical "
            "thinking and problem-solving skills. Always respond with valid JSON only."
        )

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(OPENROUTER_API_URL, json=payload, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating questions: {response.text}",
            )

        result = response.json()
        content = result["choices"][0]["message"]["content"]
        print(f"DEBUG: Raw LLM Response: {content}")

        # ----------------- Robust JSON Parsing Block ----------------- #
        try:
            # 1. Strip whitespace and code fences like ```json ... ```
            raw_content = content.strip()
            raw_content = re.sub(
                r'^```(?:json)?\s*', '', raw_content, flags=re.IGNORECASE
            )
            raw_content = re.sub(r'\s*```$', '', raw_content)

            # Remove common special tokens like <s>, </s>, <INST>, </INST>
            raw_content = re.sub(
                r'(</?s>|</?INST>|<INST>)', '', raw_content, flags=re.IGNORECASE
            )

            # 2. CRITICAL: Fix invalid backslash escapes for LaTeX.
            # We ONLY touch *single* backslashes that:
            #   - are NOT preceded by another backslash, and
            #   - do NOT start a valid JSON escape sequence (", \, /, b, f, n, r, t, u).
            #
            # This turns sequences like \,  \epsilon  \frac  etc. into \\,, \\epsilon, \\frac
            # while leaving already valid escapes such as \\sin, \n, \t untouched.
            raw_content = re.sub(
                r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', raw_content
            )

            cleaned_content = raw_content

            # 3. Isolate JSON array/object if there is extra noise around it
            if cleaned_content.count('[') > 0 and cleaned_content.count(']') > 0:
                start = cleaned_content.find('[')
                end = cleaned_content.rfind(']')
                cleaned_content = cleaned_content[start : end + 1]
            elif (
                not cleaned_content.startswith('[')
                and cleaned_content.startswith('{')
            ):
                cleaned_content = f"[{cleaned_content}]"

            if not cleaned_content.strip():
                raise json.JSONDecodeError(
                    "Content is empty after cleaning.", cleaned_content, 0
                )

            # 4. Parse JSON
            questions = json.loads(cleaned_content)

            print(
                "DEBUG: Successfully parsed JSON. "
                f"Questions count: {len(questions) if isinstance(questions, list) else 1}"
            )

            if isinstance(questions, dict):
                questions = [questions]

            return questions

        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parse error even after cleaning: {str(e)}")
            print(
                "DEBUG: Final cleaned content (first 500 chars): "
                f"{cleaned_content[:500]}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Failed to parse LLM response. Final attempt failed. "
                    f"Raw response (truncated): {content[:200]}"
                ),
            )
        except Exception as e:
            print(f"DEBUG: Unexpected error during JSON parsing: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error during JSON parsing: {str(e)}",
            )


# ---------------------------------------------------------------------------
# Core logic: generate questions for topic list
# ---------------------------------------------------------------------------

async def _generate_questions_from_topics(
    db: Session,
    request: Union[
        schemas.WorksheetRequest,
        schemas.QuizRequest,
        schemas.ExamRequest,
    ],
    current_user: str,
    topic_ids: List[str],
) -> List[models.Question]:

    if not topic_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic list cannot be empty.",
        )

    topics_data = []
    subject_name: Optional[str] = None

    # 1. Aggregate topic + chapter + subject data
    for topic_id in topic_ids:
        topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic {topic_id} not found",
            )

        chapter = (
            db.query(models.Chapter)
            .filter(models.Chapter.id == topic.chapter_id)
            .first()
        )
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chapter {topic.chapter_id} not found",
            )

        subject = (
            db.query(models.Subject)
            .filter(models.Subject.id == chapter.subject_id)
            .first()
        )
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject {chapter.subject_id} not found",
            )

        if subject_name is None:
            subject_name = request.subject_name or subject.name

        topics_data.append(
            {
                "name": topic.name,
                "chapter_name": chapter.name,
                "subtopics": ", ".join(topic.subtopics),
            }
        )

    # 2. Build prompt
    topic_names = ", ".join(d["name"] for d in topics_data)
    subtopics = "; ".join(f"{d['name']} details: {d['subtopics']}" for d in topics_data)

    normalized_subject = subject_name.lower().strip()

    prompt_base = f"""
    INSTRUCTION: USE LATEX FOR ALL MATHEMATICAL, CHEMICAL, AND SCIENTIFIC NOTATION.
    Use '$' for inline and '$$' for display equations.

    CRITICAL LATEX ESCAPING RULE: When including LaTeX inside JSON string values,
    you MUST escape single backslashes as double backslashes (e.g., use '\\\\' for
    '\\' in commands like '\\\\frac' or '\\\\text').

    CRITICAL REQUIREMENT: ALL questions MUST include actual mathematical expressions,
    chemical equations, physical formulas, or biological processes with quantitative
    relationships in the question text. NEVER generate word-only questions without
    proper expressions, equations, or formulas. Each question MUST require analytical
    thinking and problem-solving.

    Generate educational questions for an assessment with the following details:

    Subject: {subject_name}
    Topics Covered: {topic_names}
    Detailed Concepts: {subtopics}

    Generate the following types of questions:
    - Multiple Choice Questions (MCQ): {request.mcq_count}
    - Short Answer Questions: {request.short_answer_count}
    - Long Answer Questions: {request.long_answer_count}

    Difficulty level: {request.difficulty}

    For each question, provide the following JSON structure (IMPORTANT):
    {{
        "type": "mcq" | "short" | "long" | "image",
        "text": "The question text here (MUST include multiple LaTeX expressions/equations/formulas that require analytical thinking).",
        "options": ["option1", "option2", "option3", "option4"],
        "correct_answer": "The final answer with LaTeX expressions and complete derivations.",
        "explanation": "A comprehensive, step-by-step derivation or explanation.",
        "images": ["Image Description 1"],
        "difficulty": "easy" | "medium" | "hard",
        "marks": 1
    }}

    EXAMPLE MATH QUESTION:
    {{
        "type": "mcq",
        "text": "Find the derivative of $f(x) = 3x^2\\sin(2x) + e^{{4x}}$ using the product rule and chain rule.",
        "options": [
            "$f'(x) = 6x\\sin(2x) + 6x^2\\cos(2x) + 4e^{{4x}}$",
            "$f'(x) = 6x\\sin(2x) + 3x^2\\cos(2x) + e^{{4x}}$",
            "$f'(x) = 3x^2\\sin(2x) + 2\\cos(2x) + 4e^{{4x}}$",
            "$f'(x) = 6x\\sin(2x) - 6x^2\\cos(2x) + 4e^{{4x}}$"
        ],
        "correct_answer": 0,
        "explanation": "Step 1: Apply product rule to $3x^2\\sin(2x)$: $\\\\frac{{d}}{{dx}}[uv] = u'v + uv'$ where $u = 3x^2$ and $v = \\\\sin(2x)$...",
        "difficulty": "medium",
        "marks": 2
    }}

    EXAMPLE CHEMISTRY QUESTION:
    {{
        "type": "short",
        "text": "Calculate the equilibrium constant $K_c$ for the reaction $N_2(g) + 3H_2(g) \\\\rightleftharpoons 2NH_3(g)$ if at equilibrium $[N_2] = 0.2M$, $[H_2] = 0.5M$, and $[NH_3] = 0.8M$.",
        "options": [],
        "correct_answer": "$K_c = 25.6$",
        "explanation": "Step 1: Write the equilibrium expression: $K_c = \\\\frac{{[NH_3]^2}}{{[N_2][H_2]^3}}$...",
        "difficulty": "medium",
        "marks": 3
    }}
    """

    subject_instructions = ""
    if "biology" in normalized_subject:
        subject_instructions = r"""
        For Biology questions:
        - Generate questions with detailed biological processes and quantitative analysis.
        - Include at least one biological formula/structure and one quantitative relationship.
        """
    elif "math" in normalized_subject or "mathematics" in normalized_subject:
        subject_instructions = r"""
        For Mathematics questions:
        - Generate complex, multi-step problems with at least two distinct expressions.
        """
    elif "chemistry" in normalized_subject:
        subject_instructions = r"""
        For Chemistry questions:
        - Include at least one balanced chemical equation and one quantitative formula.
        """
    elif "physics" in normalized_subject:
        subject_instructions = r"""
        For Physics questions:
        - Include at least one governing law or vector equation plus quantitative formulas.
        """

    image_instructions = f"""
    Include images: {request.include_images}

    {{"CRITICAL INSTRUCTION": If include_images is true, you MUST generate image-based
    questions with type "image" and provide a detailed text description for each image
    in the "images" field. If include_images is false, only generate mcq/short/long.}}
    """

    format_instructions = """
    {"MANDATORY FORMAT": You are STRICTLY forbidden from including any text, explanation,
    markdown (like ```json), or wrapping characters before or after the JSON array.
    Respond with ONLY a single, valid JSON array of question objects. Start with '['
    and end with ']'.}
    """

    prompt = prompt_base + subject_instructions + image_instructions + format_instructions

    # 3. Call LLM
    generated_questions = await LLMService.generate_questions(prompt, subject_name)

    # 4. If requested, generate images
    if request.include_images:
        for q_data in generated_questions:
            if q_data.get("type") == "image" and q_data.get("images"):
                new_image_data = []
                for image_description in q_data["images"]:
                    try:
                        base64_data_uri = await LLMService.generate_image(
                            image_description, subject_name
                        )
                        new_image_data.append(base64_data_uri)
                    except Exception as e:
                        print(
                            "ERROR: Image generation failed for prompt "
                            f"'{image_description[:50]}...': {e}"
                        )
                        new_image_data = []
                        break
                q_data["images"] = new_image_data

    # 5. Persist questions
    saved_questions: List[models.Question] = []
    for idx, q_data in enumerate(generated_questions):
        try:
            text = (
                q_data.get("text")
                or q_data.get("question")
                or q_data.get("question_text")
            )
            if not text:
                print(f"DEBUG: Question {idx} missing text field. Data: {q_data}")
                continue

            assigned_topic_id = topic_ids[0]

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
                topic_id=assigned_topic_id,
                user_id=current_user,
            )
            db.add(question)
            db.commit()
            db.refresh(question)
            saved_questions.append(question)
            print(f"DEBUG: Successfully created question {idx}")
        except Exception as e:
            print(f"DEBUG: Error processing question {idx}: {q_data}, Error: {str(e)}")
            continue

    if not saved_questions:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate any valid questions. Please check the LLM response format.",
        )

    return saved_questions


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"message": "Classroom Canvas API"}


# ---------------------- Auth ---------------------- #

@app.post("/api/auth/register", response_model=schemas.Token)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = (
            db.query(models.User).filter(models.User.username == user.username).first()
        )
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        hashed_password = user.password  # NOTE: plain text; prod: hash it!
        db_user = models.User(
            id=str(uuid.uuid4()),
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

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
            detail=f"Error creating user: {str(e)}",
        )


@app.post("/api/auth/login", response_model=schemas.Token)
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = (
            db.query(models.User).filter(models.User.username == user.username).first()
        )
        if not db_user or db_user.hashed_password != user.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

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
            detail=f"Error during login: {str(e)}",
        )


@app.get("/api/auth/me", response_model=schemas.User)
async def get_current_user(
    current_user: str = Depends(verify_token), db: Session = Depends(get_db)
):
    try:
        user = db.query(models.User).filter(models.User.id == current_user).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user: {str(e)}",
        )


# ---------------------- Curriculum meta ---------------------- #

@app.get("/api/grades", response_model=List[schemas.Grade])
async def get_grades(db: Session = Depends(get_db)):
    print("DEBUG: GET /api/grades called")
    return db.query(models.Grade).all()


@app.get("/api/grades/{grade_id}/subjects", response_model=List[schemas.Subject])
async def get_subjects_by_grade(grade_id: str, db: Session = Depends(get_db)):
    print(f"DEBUG: GET /api/grades/{grade_id}/subjects called")
    return db.query(models.Subject).filter(models.Subject.grade_id == grade_id).all()


@app.get("/api/subjects", response_model=List[schemas.Subject])
async def get_subjects(db: Session = Depends(get_db)):
    print("DEBUG: GET /api/subjects called")
    return db.query(models.Subject).all()


@app.get("/api/subjects/{subject_id}/chapters", response_model=List[schemas.Chapter])
async def get_chapters(subject_id: str, db: Session = Depends(get_db)):
    print(f"DEBUG: GET /api/subjects/{subject_id}/chapters called")
    return (
        db.query(models.Chapter)
        .filter(models.Chapter.subject_id == subject_id)
        .all()
    )


@app.get("/api/chapters/{chapter_id}/topics", response_model=List[schemas.Topic])
async def get_topics(chapter_id: str, db: Session = Depends(get_db)):
    print(f"DEBUG: GET /api/chapters/{chapter_id}/topics called")
    return db.query(models.Topic).filter(models.Topic.chapter_id == chapter_id).all()


# ---------------------- Generation endpoints ---------------------- #

@app.post("/api/generate-worksheet", response_model=List[schemas.Question])
async def generate_worksheet(
    worksheet_request: schemas.WorksheetRequest,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        topic_id = worksheet_request.topic_id
        return await _generate_questions_from_topics(
            db, worksheet_request, current_user, [topic_id]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating worksheet: {str(e)}",
        )


@app.post("/api/generate-quiz", response_model=List[schemas.Question])
async def generate_quiz(
    quiz_request: schemas.QuizRequest,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        topic_id = quiz_request.topic_id
        return await _generate_questions_from_topics(
            db, quiz_request, current_user, [topic_id]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quiz: {str(e)}",
        )


@app.post("/api/generate-exam", response_model=List[schemas.Question])
async def generate_exam(
    exam_request: schemas.ExamRequest,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        topic_ids = exam_request.topic_ids
        if not topic_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam must specify at least one topic ID.",
            )

        return await _generate_questions_from_topics(
            db, exam_request, current_user, topic_ids
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating exam: {str(e)}",
        )


# ---------------------- Questions CRUD ---------------------- #

@app.get("/api/questions", response_model=List[schemas.Question])
async def get_questions(
    topic_id: Optional[str] = None,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(models.Question).filter(
            models.Question.user_id == current_user
        )
        if topic_id:
            query = query.filter(models.Question.topic_id == topic_id)
        return query.all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching questions: {str(e)}",
        )


@app.get("/api/questions/{question_id}", response_model=schemas.Question)
async def get_question(
    question_id: str,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        question = (
            db.query(models.Question)
            .filter(
                models.Question.id == question_id,
                models.Question.user_id == current_user,
            )
            .first()
        )
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
            )
        return question
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching question: {str(e)}",
        )


# ---------------------- Worksheets CRUD ---------------------- #

@app.post("/api/worksheets", response_model=schemas.Worksheet)
async def save_worksheet(
    worksheet: schemas.WorksheetCreate,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        topic = db.query(models.Topic).filter(models.Topic.id == worksheet.topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found"
            )

        for question_id in worksheet.question_ids:
            question = (
                db.query(models.Question)
                .filter(
                    models.Question.id == question_id,
                    models.Question.user_id == current_user,
                )
                .first()
            )
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Question with ID {question_id} not found "
                        "or does not belong to the user"
                    ),
                )

        db_worksheet = models.Worksheet(
            id=str(uuid.uuid4()),
            name=worksheet.name,
            topic_id=worksheet.topic_id,
            user_id=current_user,
            question_ids=worksheet.question_ids,
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
            detail=f"Error saving worksheet: {str(e)}",
        )


@app.get("/api/worksheets", response_model=List[schemas.Worksheet])
async def get_worksheets(
    current_user: str = Depends(verify_token), db: Session = Depends(get_db)
):
    try:
        return (
            db.query(models.Worksheet)
            .filter(models.Worksheet.user_id == current_user)
            .all()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching worksheets: {str(e)}",
        )


@app.get("/api/worksheets/{worksheet_id}", response_model=schemas.Worksheet)
async def get_worksheet(
    worksheet_id: str,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        worksheet = (
            db.query(models.Worksheet)
            .filter(
                models.Worksheet.id == worksheet_id,
                models.Worksheet.user_id == current_user,
            )
            .first()
        )
        if not worksheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Worksheet not found"
            )
        return worksheet
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching worksheet: {str(e)}",
        )


@app.delete("/api/worksheets/{worksheet_id}")
async def delete_worksheet(
    worksheet_id: str,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        worksheet = (
            db.query(models.Worksheet)
            .filter(
                models.Worksheet.id == worksheet_id,
                models.Worksheet.user_id == current_user,
            )
            .first()
        )
        if not worksheet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Worksheet not found"
            )

        db.delete(worksheet)
        db.commit()
        return {"message": "Worksheet deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting worksheet: {str(e)}",
        )


# ---------------------------------------------------------------------------
# Entry point (uvicorn)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=debug)
