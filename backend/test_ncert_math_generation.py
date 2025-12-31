import asyncio
import json
import sys
import uuid
from main import _generate_questions_from_topics
from database import SessionLocal
import models
import schemas

async def test_ncert_math_generation():
    """Test the NCERT Class 10 Mathematics question generation."""
    db = SessionLocal()
    try:
        # Create a test user if it doesn't exist
        test_user_id = "test-user"
        test_user = db.query(models.User).filter(models.User.id == test_user_id).first()
        if not test_user:
            test_user = models.User(
                id=test_user_id,
                username="testuser",
                email="test@example.com",
                hashed_password="test"
            )
            db.add(test_user)
            db.commit()
            print(f"Created test user: {test_user_id}")
        # Get the Mathematics subject for Grade 10
        math_subject = db.query(models.Subject).filter(
            models.Subject.name == "Mathematics"
        ).first()
        
        if not math_subject:
            print("ERROR: Mathematics subject not found in the database")
            return False
        
        # Get the Quadratic Equations chapter
        quadratic_chapter = db.query(models.Chapter).filter(
            models.Chapter.name == "Quadratic Equations",
            models.Chapter.subject_id == math_subject.id
        ).first()
        
        if not quadratic_chapter:
            print("ERROR: Quadratic Equations chapter not found")
            return False
        
        # Get the Quadratic Equations topic
        quadratic_topic = db.query(models.Topic).filter(
            models.Topic.name == "Quadratic Equations",
            models.Topic.chapter_id == quadratic_chapter.id
        ).first()
        
        if not quadratic_topic:
            print("ERROR: Quadratic Equations topic not found")
            return False
        
        # Create a quiz request
        quiz_request = schemas.QuizRequest(
            topic_id=quadratic_topic.id,
            mcq_count=2,
            short_answer_count=1,
            long_answer_count=1,
            difficulty="medium",
            subject_name="Mathematics",
            include_images=False
        )
        
        # Generate questions
        print(f"Generating questions for topic: {quadratic_topic.name}")
        questions = await _generate_questions_from_topics(
            db=db,
            request=quiz_request,
            current_user="test-user",
            topic_ids=[quadratic_topic.id]
        )
        
        # Print the generated questions
        print(f"\nGenerated {len(questions)} questions:")
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}:")
            print(f"Type: {question.type}")
            print(f"Text: {question.text}")
            print(f"Difficulty: {question.difficulty}")
            print(f"Marks: {question.marks}")
            if question.options:
                print(f"Options: {question.options}")
            print(f"Correct Answer: {question.correct_answer}")
            print(f"Explanation: {question.explanation}")
        
        # Check if questions are properly formatted
        all_valid = True
        for question in questions:
            if not question.text or "formula" in question.text.lower():
                print(f"WARNING: Question text may contain formula name: {question.text}")
                all_valid = False
            
            if question.difficulty not in ["easy", "medium", "hard"]:
                print(f"ERROR: Invalid difficulty level: {question.difficulty}")
                all_valid = False
            
            if question.marks <= 0:
                print(f"ERROR: Invalid marks: {question.marks}")
                all_valid = False
        
        if all_valid:
            print("\nSUCCESS: All questions are properly formatted according to NCERT guidelines")
            return True
        else:
            print("\nFAILURE: Some questions are not properly formatted")
            return False
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_ncert_math_generation())
    sys.exit(0 if success else 1)