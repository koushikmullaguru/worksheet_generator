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
from ncert_math_topics import NCERT_CLASS_10_MATH_TOPICS, DIFFICULTY_LEVELS, QUESTION_DISTRIBUTION, TOPIC_WISE_WEIGHTAGE

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

    Lets's frontend interact with the API without providing tokens during
    development. If no users exist in the DB, creates a single default user
    and returns its id.
    """
    # For development, always return a hardcoded user ID
    return "dev-user"


# ---------------------------------------------------------------------------
# OpenRouter / LLM Service
# ---------------------------------------------------------------------------

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMService:
    """Utility class for calling subject-specific LLMs and image models."""

    SUBJECT_LLM_MODELS = {
        "Biology": "mistralai/mistral-7b-instruct:free",
        "Mathematics": "tngtech/deepseek-r1t2-chimera:free",
        "Chemistry": "openai/gpt-oss-20b:free",
        "Physics": "openai/gpt-oss-20b:free",
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
                error_text = response.text
                print(
                    "ERROR: Image generation failed. "
                    f"Status: {response.status_code}, Response: {error_text}"
                )
                
                # Check if it's an authentication error
                if "401" in error_text or "unauthorized" in error_text.lower() or "user not found" in error_text.lower():
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="The AI service is currently unavailable due to authentication issues. Please try again later.",
                    )
                
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=(
                        "OpenRouter Image API failed. "
                        f"Status: {response.status_code}. Details: {error_text[:100]}"
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
            "or physical formulations. CRITICAL RULE: NEVER include formulas, formula names, "
            "or pre-calculated intermediate results in the question text. The question text "
            "should ONLY present the problem statement without any hints about which formula "
            "to use or how to solve it. "
            "CRITICAL: You MUST provide accurate, comprehensive, and step-by-step explanations "
            "for all questions. The explanations must include all formulas used, detailed reasoning, "
            "and be pedagogically sound to help students understand the complete solution process. "
            "ABSOLUTELY CRITICAL: Each explanation MUST have MULTIPLE steps (at least 3-4 steps for MCQ, "
            "4-5 steps for short answer, and 5-6 steps for long answer questions). Each step MUST be on a "
            "separate line with clear numbering like 'Step 1:', 'Step 2:', etc. Do NOT combine multiple steps "
            "in the same paragraph. Each step must be separated by an actual newline character, not just visually separated."
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
            "thinking and problem-solving skills. Always respond with valid JSON only. "
            "CRITICAL: For every question, you MUST provide a comprehensive, accurate, "
            "and pedagogically sound explanation that includes all steps, formulas used, "
            "and clear reasoning. The explanation must be detailed enough for a student "
            "to completely understand the solution process."
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
            error_text = response.text
            print(f"ERROR: OpenRouter API returned status {response.status_code}: {error_text}")
            
            # Check if it's an authentication error
            if "401" in error_text or "unauthorized" in error_text.lower() or "user not found" in error_text.lower():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="The AI service is currently unavailable due to authentication issues. Please try again later.",
                )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating questions: {error_text}",
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
            raw_content = re.sub(
                r'(</?s>|</?INST>|<INST>)', '', raw_content, flags=re.IGNORECASE
            )
            
            # First, let's try to parse the JSON as-is to see if it's valid
            try:
                questions = json.loads(raw_content)
                if isinstance(questions, dict):
                    questions = [questions]
                return questions
            except json.JSONDecodeError:
                # If parsing fails, continue with cleaning
                pass
            
            # 2. Debug: Print the exact character at the error position
            # This will help us identify what's causing the issue
            try:
                # Try to parse and catch the exact error
                json.loads(raw_content)
            except json.JSONDecodeError as e:
                error_pos = e.pos
                print(f"DEBUG: Error at position {error_pos}")
                if error_pos < len(raw_content):
                    char_at_error = raw_content[error_pos]
                    char_code = ord(char_at_error)
                    print(f"DEBUG: Character at error position: '{char_at_error}' (code: {char_code})")
                    # Print some context around the error
                    start_context = max(0, error_pos - 20)
                    end_context = min(len(raw_content), error_pos + 20)
                    context = raw_content[start_context:end_context]
                    print(f"DEBUG: Context around error: ...{context}...")
            
            # 3. Use a more direct approach to clean the JSON
            # First, let's extract just the JSON part
            json_start = raw_content.find('[')
            if json_start == -1:
                json_start = raw_content.find('{')
            
            if json_start == -1:
                raise json.JSONDecodeError("No JSON found in response", raw_content, 0)
            
            # Find the matching closing bracket
            if raw_content[json_start] == '[':
                json_end = raw_content.rfind(']')
                if json_end == -1:
                    raise json.JSONDecodeError("Unclosed JSON array", raw_content, json_start)
            else:  # it's '{'
                json_end = raw_content.rfind('}')
                if json_end == -1:
                    raise json.JSONDecodeError("Unclosed JSON object", raw_content, json_start)
            
            json_content = raw_content[json_start:json_end+1]
            
            # 4. Clean the JSON content character by character if needed
            def clean_json_string(json_str):
                # We'll process the string character by character to identify and fix issues
                result = []
                in_string = False
                escape_next = False
                
                for i, char in enumerate(json_str):
                    if escape_next:
                        # We're in an escape sequence, just add the character
                        result.append(char)
                        escape_next = False
                    elif char == '\\':
                        # Start of an escape sequence
                        result.append(char)
                        escape_next = True
                    elif char == '"':
                        # Quote character
                        result.append(char)
                        in_string = not in_string
                    elif in_string:
                        # We're inside a string, check for control characters
                        if ord(char) < 32:  # Control character
                            # Replace with escape sequence
                            if char == '\n':
                                result.append('\\n')
                            elif char == '\r':
                                result.append('\\r')
                            elif char == '\t':
                                result.append('\\t')
                            elif char == '\b':
                                result.append('\\b')
                            elif char == '\f':
                                result.append('\\f')
                            else:
                                # Other control character, use Unicode escape
                                result.append(f'\\u{ord(char):04x}')
                        else:
                            # Normal character, just add it
                            result.append(char)
                    else:
                        # We're outside a string, just add the character
                        result.append(char)
                
                return ''.join(result)
            
            cleaned_json = clean_json_string(json_content)
            
            # 5. Try parsing the cleaned JSON
            try:
                questions = json.loads(cleaned_json)
                print(
                    "DEBUG: Successfully parsed JSON after character-by-character cleaning. "
                    f"Questions count: {len(questions) if isinstance(questions, list) else 1}"
                )
                if isinstance(questions, dict):
                    questions = [questions]
                return questions
            except json.JSONDecodeError as e:
                print(f"DEBUG: Character-by-character JSON parsing failed: {str(e)}")
                
                # 6. Last resort: try using the built-in json decoder with a custom approach
                try:
                    # Use Python's ast module to parse the JSON-like structure
                    import ast
                    
                    # Replace Python None/True/False with JSON null/true/false
                    final_attempt = cleaned_json.replace('None', 'null')
                    final_attempt = final_attempt.replace('True', 'true')
                    final_attempt = final_attempt.replace('False', 'false')
                    
                    # Try to parse as Python literal first, then convert to JSON
                    try:
                        parsed = ast.literal_eval(final_attempt)
                        # Convert back to JSON string and then parse
                        json_str = json.dumps(parsed)
                        questions = json.loads(json_str)
                        
                        print(
                            "DEBUG: Successfully parsed JSON using AST fallback. "
                            f"Questions count: {len(questions) if isinstance(questions, list) else 1}"
                        )
                        if isinstance(questions, dict):
                            questions = [questions]
                        return questions
                    except:
                        # If all else fails, try one more approach
                        pass
                except Exception as e4:
                    print(f"DEBUG: Final AST parsing attempt failed: {str(e4)}")
                
                # 7. Final attempt: try to fix common JSON issues
                try:
                    # Fix unescaped quotes in strings
                    last_resort_cleaned = re.sub(r'(?<!\\)"(?=[^"}]*$)', r'\\"', cleaned_json)
                    # Fix trailing commas
                    last_resort_cleaned = re.sub(r',(\s*[}\]])', r'\1', last_resort_cleaned)
                    
                    questions = json.loads(last_resort_cleaned)
                    
                    print(
                        "DEBUG: Successfully parsed JSON after last resort fixes. "
                        f"Questions count: {len(questions) if isinstance(questions, list) else 1}"
                    )
                    if isinstance(questions, dict):
                        questions = [questions]
                    return questions
                except json.JSONDecodeError as e3:
                    print(f"DEBUG: All JSON parsing attempts failed: {str(e3)}")
                    raise e3

        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parse error even after cleaning: {str(e)}")
            print(
                "DEBUG: Final cleaned content (first 500 chars): "
                f"{cleaned_json[:500] if 'cleaned_json' in locals() else content[:500]}"
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

    # Get NCERT topic details if it's a Class 10 Mathematics topic
    ncert_topic_details = ""
    if subject_name == "Mathematics" and topic_names in NCERT_CLASS_10_MATH_TOPICS:
        ncert_topic_details = NCERT_CLASS_10_MATH_TOPICS[topic_names]
    
    # Get difficulty level details
    difficulty_details = DIFFICULTY_LEVELS.get(request.difficulty, DIFFICULTY_LEVELS["medium"])
    
    prompt_base = f"""
    INSTRUCTION: USE LATEX FOR ALL MATHEMATICAL NOTATION.
    Use '$' for inline and '$$' for display equations.

    CRITICAL LATEX ESCAPING RULE: When including LaTeX inside JSON string values,
    you MUST escape single backslashes as double backslashes (e.g., use '\\\\' for
    '\\' in commands like '\\\\frac' or '\\\\text').

    ### NCERT CLASS 10 MATHEMATICS SYLLABUS ADHERENCE ###
    YOU ARE GENERATING QUESTIONS STRICTLY BASED ON NCERT CLASS 10 MATHEMATICS SYLLABUS.
    
    TOPIC: {topic_names}
    NCERT SYLLABUS DETAILS: {ncert_topic_details}
    SUBTOPICS: {subtopics}
    
    CRITICAL REQUIREMENT: ALL questions MUST be strictly based on NCERT Class 10 Mathematics
    curriculum and MUST include actual mathematical expressions, equations, or formulas
    as specified in the NCERT textbook. Each question MUST require analytical thinking
    and problem-solving as per NCERT guidelines.

    ### CRITICAL RESTRICTION ###
    1. NEVER include the formula name (e.g., "quadratic formula", "sum formula", etc.) in the question text.
    2. NEVER include pre-calculated intermediate results in the question text.
    3. NEVER tell which formula to use in the question.
    4. NEVER provide any hints about the solution approach in the question text.
    5. ALL questions must be strictly based on NCERT Class 10 Mathematics curriculum.

    ### CRITICAL DIVERSITY REQUIREMENT ###
    YOU MUST GENERATE QUESTIONS THAT COVER DIFFERENT ASPECTS OF THE SPECIFIC NCERT TOPIC,
    NOT JUST ONE TYPE OF PROBLEM. ALL QUESTIONS MUST BE DIRECTLY RELATED TO THE TOPIC.
    
    FOR "{topic_names}" TOPIC, YOU MUST CREATE QUESTIONS THAT COVER DIFFERENT ASPECTS, CONCEPTS,
    AND APPLICATIONS WITHIN THIS TOPIC AS PER NCERT. EACH QUESTION SHOULD TEST A DIFFERENT SKILL OR
    UNDERSTANDING RELATED TO THIS TOPIC.
    
    EXAMPLE DIVERSITY FOR "{topic_names}" TOPIC:
    - Questions about fundamental concepts and definitions from NCERT
    - Questions about problem-solving and applications as per NCERT examples
    - Questions that require analytical thinking as per NCERT exercises
    - Questions that test different subtopics within the main topic as per NCERT
    - Questions with varying difficulty levels within the specified difficulty
    - Questions that approach the topic from different angles as per NCERT
    
    ABSOLUTELY DO NOT GENERATE QUESTIONS ABOUT TOPICS OUTSIDE OF "{topic_names}".
    STRICTLY STAY WITHIN THE BOUNDARIES OF THE SPECIFIED TOPIC AND ITS SUBTOPICS: {subtopics}.

    Generate educational questions for an assessment with the following details:

    Subject: {subject_name}
    Topics Covered: {topic_names}
    Detailed Concepts: {subtopics}
    Difficulty Level: {request.difficulty} ({difficulty_details['description']})
    Focus: {difficulty_details['focus']}

    CRITICAL: You MUST generate EXACTLY the following number of questions:
    - Multiple Choice Questions (MCQ): {request.mcq_count} (EXACT COUNT, {difficulty_details['mcq_marks']} marks each)
    - Short Answer Questions: {request.short_answer_count} (EXACT COUNT, {difficulty_details['short_marks']} marks each)
    - Long Answer Questions: {request.long_answer_count} (EXACT COUNT, {difficulty_details['long_marks']} marks each)
    
    TOTAL QUESTIONS TO GENERATE: {request.mcq_count + request.short_answer_count + request.long_answer_count}
    
    DO NOT generate more or fewer questions than specified above.

    For each question, provide the following JSON structure (IMPORTANT):
    {{
        "type": "mcq" | "short" | "long" | "image",
        "text": "The question text here (MUST include multiple LaTeX expressions/equations that require analytical thinking as per NCERT).",
        "options": ["option1", "option2", "option3", "option4"],
        "correct_answer": "The final answer with LaTeX expressions and complete derivations.",
        "explanation": "A comprehensive, step-by-step derivation or explanation as per NCERT methodology. MUST include all steps, formulas used, and clear reasoning that leads to the correct answer. The explanation should be detailed enough for a student to understand the complete solution process. ABSOLUTELY CRITICAL: Each explanation MUST have MULTIPLE steps (at least 3-4 steps for MCQ, 4-5 steps for short answer, and 5-6 steps for long answer questions). Each step MUST be on a separate line with clear numbering like 'Step 1:', 'Step 2:', etc. Do NOT combine multiple steps in the same paragraph. Each step must be separated by an actual newline character.",
        "images": ["Image Description 1"],
        "difficulty": "{request.difficulty}",
        "marks": {difficulty_details['mcq_marks'] if "mcq" in "{request.difficulty}" else difficulty_details['short_marks'] if "short" in "{request.difficulty}" else difficulty_details['long_marks']}
    }}

    EXAMPLE MATH QUESTIONS (SHOWING DIVERSITY):
    
    EXAMPLE 1 - DERIVATIVES:
    {{
        "type": "mcq",
        "text": "Given the function $f(x) = 3x^2\\sin(2x) + e^{{4x}}$, which expression represents its derivative?",
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
    
    EXAMPLE 2 - INTEGRATION:
    {{
        "type": "short",
        "text": "Evaluate the definite integral $\\\\int_0^{{\\\\pi}} x\\cos(x)dx$.",
        "options": [],
        "correct_answer": "$-2$",
        "explanation": "Step 1: Use integration by parts: $\\\\int u dv = uv - \\\\int v du$ where $u = x$ and $dv = \\\\cos(x)dx$...",
        "difficulty": "medium",
        "marks": 3
    }}

    EXAMPLE CHEMISTRY QUESTIONS (SHOWING DIVERSITY):
    
    EXAMPLE 1 - EQUILIBRIUM:
    {{
        "type": "short",
        "text": "For the reaction $N_2(g) + 3H_2(g) \\\\rightleftharpoons 2NH_3(g)$, calculate the equilibrium constant when at equilibrium $[N_2] = 0.2M$, $[H_2] = 0.5M$, and $[NH_3] = 0.8M$.",
        "options": [],
        "correct_answer": "$K_c = 25.6$",
        "explanation": "Step 1: Write the equilibrium expression: $K_c = \\\\frac{{[NH_3]^2}}{{[N_2][H_2]^3}}$...",
        "difficulty": "medium",
        "marks": 3
    }}
    
    EXAMPLE 2 - STOICHIOMETRY:
    {{
        "type": "mcq",
        "text": "When $12.5g$ of $CuSO_4$ reacts with excess $NaOH$, what mass of $Cu(OH)_2$ is produced?",
        "options": [
            "$8.5g$",
            "$12.1g$",
            "$15.3g$",
            "$18.7g$"
        ],
        "correct_answer": 1,
        "explanation": "Step 1: Write the balanced equation: $CuSO_4 + 2NaOH \\\\rightarrow Cu(OH)_2 + Na_2SO_4$...",
        "difficulty": "medium",
        "marks": 2
    }}
    """

    subject_instructions = ""
    if "biology" in normalized_subject:
        subject_instructions = r"""
        For Biology questions:
        - Generate questions with detailed biological processes and quantitative analysis.
        - Include at least one biological formula/structure and one quantitative relationship.
        - REMEMBER: NEVER mention formula names or provide solution hints in the question text.
        - ENSURE DIVERSITY WITHIN THE SPECIFIC TOPIC: Create questions that explore different aspects, processes, and applications within "{topic_names}".
          Each question should test a different skill or understanding related to this biological topic.
          Do not include questions about unrelated biological concepts outside the specified topic.
        """
    elif "math" in normalized_subject or "mathematics" in normalized_subject:
        subject_instructions = f"""
        For NCERT Class 10 Mathematics questions:
        - Generate problems strictly based on NCERT Class 10 Mathematics curriculum for the topic "{topic_names}".
        - Include mathematical expressions and problems as found in NCERT textbooks and exercises.
        - Questions should reflect the exact difficulty level: {request.difficulty} ({difficulty_details['description']}).
        - Each question should be worth {difficulty_details['mcq_marks']} marks for MCQ, {difficulty_details['short_marks']} marks for Short Answer, and {difficulty_details['long_marks']} marks for Long Answer.
        - REMEMBER: NEVER mention formula names (like "quadratic formula", "sum formula", etc.) or provide solution hints in the question text.
        - ENSURE DIVERSITY WITHIN THE SPECIFIC TOPIC: All questions must be directly related to the NCERT topic "{topic_names}".
          Create questions that explore different aspects, applications, and problem-solving approaches within this topic as per NCERT.
          Each question should test a different skill or understanding related to "{topic_names}" as per NCERT guidelines.
          Do not include questions about unrelated mathematical concepts outside the specified NCERT topic.
        - Questions should be similar to those found in NCERT Class 10 Mathematics textbook exercises and examples.
        - CRITICAL: For every question, you MUST provide a comprehensive, accurate, and pedagogically sound explanation.
          The explanation MUST include:
          * All formulas used in the solution
          * Step-by-step reasoning that is clear and logical, with each step on a SEPARATE line
          * Complete mathematical derivations where applicable
          * Final answer with proper mathematical notation
          The explanation should be detailed enough for a student to completely understand the solution process.
          ABSOLUTELY CRITICAL: Each explanation MUST have MULTIPLE steps (at least 3-4 steps for MCQ,
          4-5 steps for short answer, and 5-6 steps for long answer questions). Each step MUST be on a SEPARATE line
          with clear numbering like 'Step 1:', 'Step 2:', etc. Do NOT combine multiple steps in the same paragraph.
          Each step must be separated by an actual newline character.
        """
    elif "chemistry" in normalized_subject:
        subject_instructions = r"""
        For Chemistry questions:
        - Include at least one balanced chemical equation and one quantitative formula.
        - REMEMBER: NEVER mention formula names or provide solution hints in the question text.
        - ENSURE DIVERSITY WITHIN THE SPECIFIC TOPIC: Create questions that explore different aspects, reactions, and applications within "{topic_names}".
          Each question should test a different skill or understanding related to this chemistry topic.
          Do not include questions about unrelated chemical concepts outside the specified topic.
        """
    elif "physics" in normalized_subject:
        subject_instructions = r"""
        For Physics questions:
        - Include at least one governing law or vector equation plus quantitative formulas.
        - REMEMBER: NEVER mention formula names or provide solution hints in the question text.
        - ENSURE DIVERSITY WITHIN THE SPECIFIC TOPIC: Create questions that explore different aspects, principles, and applications within "{topic_names}".
          Each question should test a different skill or understanding related to this physics topic.
          Do not include questions about unrelated physics concepts outside the specified topic.
        """

    include_images = "true" if request.include_images else "false"
    image_instructions = f"""
    Include images: {include_images}

    If include_images is true, you MUST generate image-based questions with type "image" 
    and provide a detailed text description for each image in the "images" field. 
    If include_images is false, only generate mcq/short/long.
    """

    format_instructions = f"""
    MANDATORY FORMAT: You are STRICTLY forbidden from including any text, explanation,
    markdown (like ```json), or wrapping characters before or after the JSON array.
    Respond with ONLY a single, valid JSON array of question objects. Start with '['
    and end with ']'.
    
    FINAL REMINDER: For ALL questions, the 'text' field must ONLY contain the problem
    statement WITHOUT any formula names, solution hints, or instructions about which
    formula to use. The student must determine the appropriate method themselves.
    
    CRITICAL NCERT TOPIC AND DIVERSITY CHECK: Before responding, review your generated questions to ensure:
    1. ALL questions are strictly based on the NCERT Class 10 Mathematics topic "{topic_names}".
    2. Questions cover DIFFERENT aspects of the NCERT topic, not just one type of problem.
    3. Each question tests a different skill or understanding within the NCERT topic.
    4. Questions are diverse in their approach, complexity, and application as per NCERT.
    5. NO questions about concepts outside the specified NCERT topic and subtopics.
    6. All questions reflect the {request.difficulty} difficulty level ({difficulty_details['description']}).
    7. Questions are similar to those found in NCERT Class 10 Mathematics textbook.
    8. CRITICAL: Each question has a comprehensive, accurate, and pedagogically sound explanation
       that includes all formulas used, step-by-step reasoning with each step on a SEPARATE line,
       and complete mathematical derivations. The explanation must be detailed enough for a student
       to completely understand the solution process. Each explanation MUST have MULTIPLE steps
       (at least 3-4 steps for MCQ, 4-5 steps for short answer, and 5-6 steps for long answer questions).
       Each step MUST be on a SEPARATE line with clear numbering like 'Step 1:', 'Step 2:', etc.
       Do NOT combine multiple steps in the same paragraph. Each step must be separated by an actual
       newline character, not just visually separated.
    
    If any question fails these checks, revise it to ensure NCERT topic relevance and diversity within the topic.
    """

    prompt = prompt_base + subject_instructions + image_instructions + format_instructions

    # 3. Call LLM
    generated_questions = await LLMService.generate_questions(prompt, subject_name)
    
    # 3.1 Validate question count and adjust if needed
    expected_total = request.mcq_count + request.short_answer_count + request.long_answer_count
    actual_total = len(generated_questions)
    
    print(f"LLM generated {actual_total} questions, expected {expected_total}")
    
    # If we have too many questions, trim them down to the expected count
    if actual_total > expected_total:
        print(f"Trimming {actual_total - expected_total} excess questions...")
        generated_questions = generated_questions[:expected_total]
        print(f"Now have {len(generated_questions)} questions after trimming")
    
    # If we have too few questions, try to generate more
    elif actual_total < expected_total:
        print(f"Attempting to generate {expected_total - actual_total} additional questions...")
        additional_prompt = prompt + f"\n\nCRITICAL: You previously generated {actual_total} questions but we need EXACTLY {expected_total} questions in total. Please generate {expected_total - actual_total} more questions with the same specifications. Make sure they are different from the previous ones but follow the same format and difficulty level."
        
        try:
            additional_questions = await LLMService.generate_questions(additional_prompt, subject_name)
            # Only take as many as we need
            needed = expected_total - actual_total
            additional_questions = additional_questions[:needed]
            generated_questions.extend(additional_questions)
            print(f"Now have {len(generated_questions)} questions after additional generation")
        except Exception as e:
            print(f"ERROR: Failed to generate additional questions: {e}")
    
    # Final validation for total count
    if len(generated_questions) != expected_total:
        print(f"ERROR: Could not generate the exact number of questions. Have {len(generated_questions)}, need {expected_total}")
        # As a last resort, trim or duplicate to meet the exact count
        if len(generated_questions) > expected_total:
            generated_questions = generated_questions[:expected_total]
        else:
            # Duplicate questions to meet the count
            while len(generated_questions) < expected_total:
                # Duplicate the first question and modify its text slightly
                duplicate = generated_questions[0].copy()
                duplicate["text"] = duplicate["text"] + " (Variation)"
                generated_questions.append(duplicate)
        print(f"Final question count after adjustment: {len(generated_questions)}")
    
    # 3.2 Validate question types and adjust if needed
    mcq_questions = [q for q in generated_questions if q.get("type") == "mcq"]
    short_questions = [q for q in generated_questions if q.get("type") == "short"]
    long_questions = [q for q in generated_questions if q.get("type") == "long"]
    
    print(f"Question type distribution: MCQ: {len(mcq_questions)}, Short: {len(short_questions)}, Long: {len(long_questions)}")
    print(f"Expected distribution: MCQ: {request.mcq_count}, Short: {request.short_answer_count}, Long: {request.long_answer_count}")
    
    # Adjust MCQ count if needed
    while len(mcq_questions) < request.mcq_count:
        # Find a non-MCQ question to convert or duplicate an existing MCQ
        if len(short_questions) > 0:
            # Convert a short question to MCQ
            question_to_convert = short_questions.pop()
            question_to_convert["type"] = "mcq"
            # Add options if not present, but don't overwrite existing options
            if not question_to_convert.get("options") or len(question_to_convert.get("options", [])) < 4:
                # Only add placeholder options if none exist
                if not question_to_convert.get("options"):
                    question_to_convert["options"] = ["Option A", "Option B", "Option C", "Option D"]
                else:
                    # If some options exist, pad with placeholders to reach 4
                    existing_options = question_to_convert.get("options", [])
                    while len(existing_options) < 4:
                        existing_options.append(f"Option {chr(65 + len(existing_options))}")
                    question_to_convert["options"] = existing_options
            mcq_questions.append(question_to_convert)
        elif len(long_questions) > 0:
            # Convert a long question to MCQ
            question_to_convert = long_questions.pop()
            question_to_convert["type"] = "mcq"
            # Add options if not present
            if not question_to_convert.get("options") or len(question_to_convert.get("options", [])) < 4:
                question_to_convert["options"] = ["Option A", "Option B", "Option C", "Option D"]
            mcq_questions.append(question_to_convert)
        else:
            # Duplicate an existing MCQ
            duplicate = mcq_questions[0].copy()
            duplicate["text"] = duplicate["text"] + " (MCQ Variation)"
            mcq_questions.append(duplicate)
    
    # If we have too many MCQs, remove the excess
    while len(mcq_questions) > request.mcq_count:
        mcq_questions.pop()
    
    # Adjust short answer count if needed
    while len(short_questions) < request.short_answer_count:
        # Find a non-short question to convert or duplicate an existing short question
        if len(mcq_questions) > request.mcq_count:
            # Convert an MCQ to short answer
            question_to_convert = mcq_questions.pop()
            question_to_convert["type"] = "short"
            question_to_convert["options"] = []
            short_questions.append(question_to_convert)
        elif len(long_questions) > 0:
            # Convert a long question to short answer
            question_to_convert = long_questions.pop()
            question_to_convert["type"] = "short"
            question_to_convert["options"] = []
            short_questions.append(question_to_convert)
        else:
            # Duplicate an existing short question
            duplicate = short_questions[0].copy()
            duplicate["text"] = duplicate["text"] + " (Short Answer Variation)"
            short_questions.append(duplicate)
    
    # If we have too many short answers, remove the excess
    while len(short_questions) > request.short_answer_count:
        short_questions.pop()
    
    # Adjust long answer count if needed
    while len(long_questions) < request.long_answer_count:
        # Find a non-long question to convert or duplicate an existing long question
        if len(mcq_questions) > request.mcq_count:
            # Convert an MCQ to long answer
            question_to_convert = mcq_questions.pop()
            question_to_convert["type"] = "long"
            question_to_convert["options"] = []
            long_questions.append(question_to_convert)
        elif len(short_questions) > request.short_answer_count:
            # Convert a short question to long answer
            question_to_convert = short_questions.pop()
            question_to_convert["type"] = "long"
            question_to_convert["options"] = []
            long_questions.append(question_to_convert)
        else:
            # Duplicate an existing long question
            duplicate = long_questions[0].copy()
            duplicate["text"] = duplicate["text"] + " (Long Answer Variation)"
            long_questions.append(duplicate)
    
    # If we have too many long answers, remove the excess
    while len(long_questions) > request.long_answer_count:
        long_questions.pop()
    
    # Reconstruct the questions list with the adjusted counts
    generated_questions = mcq_questions + short_questions + long_questions
    print(f"Final question type distribution: MCQ: {len(mcq_questions)}, Short: {len(short_questions)}, Long: {len(long_questions)}")
    print(f"Total questions: {len(generated_questions)}, Expected: {expected_total}")

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

            # Determine marks based on question type and difficulty
            question_type = q_data.get("type", "mcq")
            difficulty = q_data.get("difficulty", "medium")
            marks = q_data.get("marks", 1)
            
            # If marks are not properly set, assign based on NCERT guidelines
            if marks == 1 and question_type and difficulty:
                if difficulty in DIFFICULTY_LEVELS:
                    if question_type == "mcq":
                        marks = DIFFICULTY_LEVELS[difficulty]["mcq_marks"]
                    elif question_type == "short":
                        marks = DIFFICULTY_LEVELS[difficulty]["short_marks"]
                    elif question_type == "long":
                        marks = DIFFICULTY_LEVELS[difficulty]["long_marks"]
            
            question = models.Question(
                id=str(uuid.uuid4()),
                type=question_type,
                text=text,
                options=q_data.get("options", q_data.get("choices", [])),
                correct_answer=q_data.get("correct_answer", q_data.get("answer")),
                explanation=q_data.get("explanation", ""),
                images=q_data.get("images", []),
                difficulty=difficulty,
                marks=marks,
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

        hashed_password = user.password
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
    db: Session = Depends(get_db)
):
    try:
        # For testing, always return the first user or create a default one
        user = db.query(models.User).first()
        if not user:
            default_id = "dev-user"
            user = models.User(
                id=default_id,
                username="dev",
                email="dev@example.com",
                hashed_password="dev",  # NOTE: not hashed; dev only
            )
            db.add(user)
            db.commit()
            db.refresh(user)
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
    db: Session = Depends(get_db),
):
    try:
        topic_id = worksheet_request.topic_id
        return await _generate_questions_from_topics(
            db, worksheet_request, "dev-user", [topic_id]
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
    db: Session = Depends(get_db),
):
    try:
        topic_id = quiz_request.topic_id
        return await _generate_questions_from_topics(
            db, quiz_request, "dev-user", [topic_id]
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
            db, exam_request, "dev-user", topic_ids
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
    db: Session = Depends(get_db),
):
    try:
        query = db.query(models.Question)
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
    db: Session = Depends(get_db),
):
    try:
        question = (
            db.query(models.Question)
            .filter(models.Question.id == question_id)
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
                .filter(models.Question.id == question_id)
                .first()
            )
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Question with ID {question_id} not found",
                )

        db_worksheet = models.Worksheet(
            id=str(uuid.uuid4()),
            name=worksheet.name,
            topic_id=worksheet.topic_id,
            user_id="dev-user",
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
    db: Session = Depends(get_db)
):
    try:
        return db.query(models.Worksheet).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching worksheets: {str(e)}",
        )


@app.get("/api/worksheets/{worksheet_id}", response_model=schemas.Worksheet)
async def get_worksheet(
    worksheet_id: str,
    db: Session = Depends(get_db),
):
    try:
        worksheet = (
            db.query(models.Worksheet)
            .filter(models.Worksheet.id == worksheet_id)
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
    db: Session = Depends(get_db),
):
    try:
        worksheet = (
            db.query(models.Worksheet)
            .filter(models.Worksheet.id == worksheet_id)
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


# ---------------------- Quiz Answer & Result CRUD ----------------------

@app.post("/api/quiz-answers", response_model=List[schemas.QuizAnswer])
async def submit_quiz_answers(
    submission: schemas.QuizSubmission,
    db: Session = Depends(get_db),
):
    """Submit answers for a quiz and calculate results."""
    try:
        # Save all answers
        saved_answers = models.create_bulk_quiz_answers(db, submission.answers, "dev-user")
        
        # Calculate quiz results
        total_questions = len(saved_answers)
        correct_answers = sum(1 for answer in saved_answers if answer.is_correct)
        score_percentage = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        
        # Create quiz result record
        if submission.worksheet_id:
            result_data = schemas.QuizResultCreate(
                worksheet_id=submission.worksheet_id,
                total_questions=total_questions,
                correct_answers=correct_answers,
                score_percentage=score_percentage
            )
            models.create_quiz_result(db, result_data, "dev-user")
        
        return saved_answers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting quiz answers: {str(e)}",
        )

@app.get("/api/quiz-answers", response_model=List[schemas.QuizAnswer])
async def get_quiz_answers(
    worksheet_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all quiz answers for a user, optionally filtered by worksheet."""
    try:
        return models.get_quiz_answers(db, "dev-user", worksheet_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching quiz answers: {str(e)}",
        )

@app.get("/api/quiz-results", response_model=List[schemas.QuizResult])
async def get_quiz_results(
    worksheet_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all quiz results for a user, optionally filtered by worksheet."""
    try:
        return models.get_quiz_results(db, "dev-user", worksheet_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching quiz results: {str(e)}",
        )

@app.get("/api/quiz-results/{result_id}", response_model=schemas.QuizResult)
async def get_quiz_result(
    result_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific quiz result by ID."""
    try:
        result = models.get_quiz_result(db, result_id, "dev-user")
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz result not found",
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching quiz result: {str(e)}",
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