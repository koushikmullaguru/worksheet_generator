from sqlalchemy.orm import Session
from database import Base, User, Grade, Subject, Chapter, Topic, Question, Worksheet, QuizAnswer, QuizResult, QuizFeedback
import schemas
import uuid

# User operations
def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    # In production, hash the password before storing
    db_user = User(
        id=user.id,
        username=user.username,
        email=user.email,
        hashed_password=user.password  # In production, use hashed password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Grade operations
def get_grades(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Grade).offset(skip).limit(limit).all()

def get_grade(db: Session, grade_id: str):
    return db.query(Grade).filter(Grade.id == grade_id).first()

def create_grade(db: Session, grade_obj: schemas.GradeCreate):
    db_grade = Grade(
        id=grade_obj.id,
        name=grade_obj.name,
        description=grade_obj.description
    )
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade

def get_subjects_by_grade(db: Session, grade_id: str):
    return db.query(Subject).filter(Subject.grade_id == grade_id).all()

# Subject operations
def get_subjects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Subject).offset(skip).limit(limit).all()

def get_subject(db: Session, subject_id: str):
    return db.query(Subject).filter(Subject.id == subject_id).first()

def create_subject(db: Session, subject: schemas.SubjectCreate):
    db_subject = Subject(
        id=subject.id,
        name=subject.name,
        description=subject.description,
        grade_id=subject.grade_id
    )
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

# Chapter operations
def get_chapters_by_subject(db: Session, subject_id: str):
    return db.query(Chapter).filter(Chapter.subject_id == subject_id).all()

def get_chapter(db: Session, chapter_id: str):
    return db.query(Chapter).filter(Chapter.id == chapter_id).first()

def create_chapter(db: Session, chapter: schemas.ChapterCreate):
    db_chapter = Chapter(
        id=chapter.id,
        name=chapter.name,
        description=chapter.description,
        subject_id=chapter.subject_id
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter

# Topic operations
def get_topics_by_chapter(db: Session, chapter_id: str):
    return db.query(Topic).filter(Topic.chapter_id == chapter_id).all()

def get_topic(db: Session, topic_id: str):
    return db.query(Topic).filter(Topic.id == topic_id).first()

def create_topic(db: Session, topic: schemas.TopicCreate):
    db_topic = Topic(
        id=topic.id,
        name=topic.name,
        description=topic.description,
        chapter_id=topic.chapter_id,
        subtopics=topic.subtopics
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

# Question operations
def get_questions(db: Session, user_id: str, topic_id: str = None, skip: int = 0, limit: int = 100):
    query = db.query(Question).filter(Question.user_id == user_id)
    if topic_id:
        query = query.filter(Question.topic_id == topic_id)
    return query.offset(skip).limit(limit).all()

def get_question(db: Session, question_id: str):
    return db.query(Question).filter(Question.id == question_id).first()

def create_question(db: Session, question: schemas.QuestionCreate, user_id: str):
    db_question = Question(
        id=question.id,
        type=question.type,
        text=question.text,
        options=question.options,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        images=question.images,
        difficulty=question.difficulty,
        marks=question.marks,
        topic_id=question.topic_id,
        user_id=user_id
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def create_bulk_questions(db: Session, questions: list, user_id: str):
    db_questions = []
    for question_data in questions:
        db_question = Question(
            id=question_data.id,
            type=question_data.type,
            text=question_data.text,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            images=question_data.images,
            difficulty=question_data.difficulty,
            marks=question_data.marks,
            topic_id=question_data.topic_id,
            user_id=user_id
        )
        db.add(db_question)
        db_questions.append(db_question)
    
    db.commit()
    # Refresh all questions
    for question in db_questions:
        db.refresh(question)
    
    return db_questions

# Worksheet operations
def get_worksheets(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(Worksheet).filter(Worksheet.user_id == user_id).offset(skip).limit(limit).all()

def get_worksheet(db: Session, worksheet_id: str, user_id: str):
    return db.query(Worksheet).filter(
        Worksheet.id == worksheet_id,
        Worksheet.user_id == user_id
    ).first()

def create_worksheet(db: Session, worksheet: schemas.WorksheetCreate, user_id: str):
    db_worksheet = Worksheet(
        id=worksheet.id,
        name=worksheet.name,
        topic_id=worksheet.topic_id,
        user_id=user_id,
        question_ids=worksheet.question_ids
    )
    db.add(db_worksheet)
    db.commit()
    db.refresh(db_worksheet)
    return db_worksheet

def delete_worksheet(db: Session, worksheet_id: str, user_id: str):
    worksheet = db.query(Worksheet).filter(
        Worksheet.id == worksheet_id,
        Worksheet.user_id == user_id
    ).first()
    
    if worksheet:
        db.delete(worksheet)
        db.commit()
    
    return worksheet

# Quiz Answer operations
def get_quiz_answers(db: Session, user_id: str, worksheet_id: str = None):
    query = db.query(QuizAnswer).filter(QuizAnswer.user_id == user_id)
    if worksheet_id:
        query = query.filter(QuizAnswer.worksheet_id == worksheet_id)
    return query.all()

def get_quiz_answer(db: Session, answer_id: str, user_id: str):
    return db.query(QuizAnswer).filter(
        QuizAnswer.id == answer_id,
        QuizAnswer.user_id == user_id
    ).first()

def create_quiz_answer(db: Session, answer: schemas.QuizAnswerCreate, user_id: str):
    # Get the question to check if the answer is correct
    question = db.query(Question).filter(Question.id == answer.question_id).first()
    if not question:
        raise ValueError(f"Question with ID {answer.question_id} not found")
    
    # Determine if the answer is correct
    is_correct = False
    if question.type == "mcq":
        if isinstance(answer.user_answer, int) and isinstance(question.correct_answer, int):
            is_correct = answer.user_answer == question.correct_answer
        elif isinstance(answer.user_answer, list) and isinstance(question.correct_answer, list):
            is_correct = sorted(answer.user_answer) == sorted(question.correct_answer)
    else:
        # For short and long answer questions, simple string comparison
        if isinstance(answer.user_answer, str) and isinstance(question.correct_answer, str):
            is_correct = answer.user_answer.lower().strip() == question.correct_answer.lower().strip()
    
    db_answer = QuizAnswer(
        id=str(uuid.uuid4()),
        user_id=user_id,
        question_id=answer.question_id,
        worksheet_id=answer.worksheet_id,
        user_answer=answer.user_answer,
        is_correct=is_correct
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer

def create_bulk_quiz_answers(db: Session, answers: list, user_id: str):
    db_answers = []
    for answer_data in answers:
        try:
            db_answer = create_quiz_answer(db, answer_data, user_id)
            db_answers.append(db_answer)
        except ValueError as e:
            print(f"Error creating answer: {str(e)}")
            continue
    
    return db_answers

# Quiz Result operations
def get_quiz_results(db: Session, user_id: str, worksheet_id: str = None):
    query = db.query(QuizResult).filter(QuizResult.user_id == user_id)
    if worksheet_id:
        query = query.filter(QuizResult.worksheet_id == worksheet_id)
    return query.all()

def get_quiz_result(db: Session, result_id: str, user_id: str):
    return db.query(QuizResult).filter(
        QuizResult.id == result_id,
        QuizResult.user_id == user_id
    ).first()

def create_quiz_result(db: Session, result: schemas.QuizResultCreate, user_id: str):
    db_result = QuizResult(
        id=str(uuid.uuid4()),
        user_id=user_id,
        worksheet_id=result.worksheet_id,
        total_questions=result.total_questions,
        correct_answers=result.correct_answers,
        score_percentage=result.score_percentage
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

# Quiz Feedback operations
def get_quiz_feedback(db: Session, user_id: str, worksheet_id: str = None):
    query = db.query(QuizFeedback).filter(QuizFeedback.user_id == user_id)
    if worksheet_id:
        query = query.filter(QuizFeedback.worksheet_id == worksheet_id)
    return query.all()

def get_quiz_feedback_by_type(db: Session, user_id: str, worksheet_id: str, feedback_type: str):
    return db.query(QuizFeedback).filter(
        QuizFeedback.user_id == user_id,
        QuizFeedback.worksheet_id == worksheet_id,
        QuizFeedback.feedback_type == feedback_type
    ).all()

def create_quiz_feedback(db: Session, feedback: schemas.QuizFeedbackCreate, user_id: str):
    db_feedback = QuizFeedback(
        id=str(uuid.uuid4()),
        user_id=user_id,
        worksheet_id=feedback.worksheet_id,
        feedback_type=feedback.feedback_type,
        comment=feedback.comment
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback