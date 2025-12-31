# NCERT Class 10 Mathematics Topics Structure

NCERT_CLASS_10_MATH_TOPICS = {
    "Real Numbers": "Fundamental Theorem of Arithmetic, Proof of irrationality of root 2, 3, 5",
    "Polynomials": "Zeros of a polynomial, Relationship between zeros and coefficients of quadratic polynomials",
    "Pair of Linear Equations in Two Variables": "Graphical method, Consistency, Substitution, Elimination",
    "Quadratic Equations": "Standard form, Factorization, Quadratic formula, Nature of roots, Discriminant",
    "Arithmetic Progressions": "nth term of AP, Sum of first n terms",
    "Triangles": "Similarity, BPT Theorem, AA, SAS, SSS criteria",
    "Coordinate Geometry": "Distance formula, Section formula",
    "Introduction to Trigonometry": "Trigonometric ratios 0-90 degrees, sin^2 + cos^2 = 1",
    "Some Applications of Trigonometry": "Heights and Distances, Angle of elevation/depression",
    "Circles": "Tangent properties, Tangents from external points",
    "Areas Related to Circles": "Area of sectors and segments",
    "Surface Areas and Volumes": (
        "1. Determine the surface area of an object formed by combining any two of the basic solids: "
        "cuboid, cone, cylinder, sphere and hemisphere. "
        "2. Find the volume of objects formed by combining any two of a cuboid, cone, cylinder, sphere and hemisphere."
    ),
    "Statistics": "Mean, Median, Mode of grouped data",
    "Probability": "Theoretical probability, Simple events"
}

# Difficulty levels and their corresponding question types and marks
DIFFICULTY_LEVELS = {
    "easy": {
        "description": "Basic understanding and direct application of formulas",
        "mcq_marks": 1,
        "short_marks": 2,
        "long_marks": 3,
        "focus": "Direct application of formulas, basic concepts"
    },
    "medium": {
        "description": "Multi-step problems requiring application of multiple concepts",
        "mcq_marks": 2,
        "short_marks": 3,
        "long_marks": 5,
        "focus": "Problem-solving, application of multiple concepts"
    },
    "hard": {
        "description": "Complex problems requiring analytical thinking and deeper understanding",
        "mcq_marks": 3,
        "short_marks": 4,
        "long_marks": 5,
        "focus": "Analytical thinking, complex problem-solving"
    }
}

# Question type distribution based on difficulty
QUESTION_DISTRIBUTION = {
    "easy": {
        "mcq_percentage": 60,  # 60% MCQ questions
        "short_percentage": 30,  # 30% Short answer questions
        "long_percentage": 10  # 10% Long answer questions
    },
    "medium": {
        "mcq_percentage": 40,  # 40% MCQ questions
        "short_percentage": 40,  # 40% Short answer questions
        "long_percentage": 20  # 20% Long answer questions
    },
    "hard": {
        "mcq_percentage": 30,  # 30% MCQ questions
        "short_percentage": 30,  # 30% Short answer questions
        "long_percentage": 40  # 40% Long answer questions
    }
}

# Topic-wise weightage for exam preparation
TOPIC_WISE_WEIGHTAGE = {
    "Real Numbers": 6,
    "Polynomials": 5,
    "Pair of Linear Equations in Two Variables": 8,
    "Quadratic Equations": 8,
    "Arithmetic Progressions": 5,
    "Triangles": 9,
    "Coordinate Geometry": 6,
    "Introduction to Trigonometry": 8,
    "Some Applications of Trigonometry": 8,
    "Circles": 7,
    "Areas Related to Circles": 7,
    "Surface Areas and Volumes": 10,
    "Statistics": 7,
    "Probability": 6
}