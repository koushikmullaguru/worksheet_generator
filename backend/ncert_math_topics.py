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

TOPIC_SUMMARIES = {
    "Quadratic Equations": """
1. A quadratic equation in the variable x is of the form ax2 + bx + c = 0, where a, b, c are real numbers and a ≠ 0.
2. A real number α is said to be a root of the quadratic equation ax2 + bx + c = 0, if aα2 + bα + c = 0. The zeroes of the quadratic polynomial ax2 + bx + c and the roots of the quadratic equation ax2 + bx + c = 0 are the same.
3. If we can factorise ax2 + bx + c, a ≠ 0, into a product of two linear factors, then the roots of the quadratic equation ax2 + bx + c = 0 can be found by equating each factor to zero.
4. Quadratic formula: The roots of a quadratic equation ax2 + bx + c = 0 are given by [-b ± √(b2 – 4ac)] / 2a, provided b2 – 4ac ≥ 0.
5. A quadratic equation ax2 + bx + c = 0 has:
(i) two distinct real roots, if b2 – 4ac > 0,
(ii) two equal roots (i.e., coincident roots), if b2 – 4ac = 0, and
(iii) no real roots, if b2 – 4ac < 0.
    """,
    
    "Arithmetic Progressions": """
1. An arithmetic progression (AP) is a list of numbers in which each term is obtained by adding a fixed number d to the preceding term, except the first term. The fixed number d is called the common difference. The general form of an AP is a, a + d, a + 2d, a + 3d, . . .
2. A given list of numbers a1, a2, a3, . . . is an AP, if the differences a2 – a1, a3 – a2, a4 – a3, . . ., give the same value, i.e., if ak + 1 – ak is the same for different values of k.
3. In an AP with first term a and common difference d, the nth term (or the general term) is given by an = a + (n – 1) d.
4. The sum of the first n terms of an AP is given by : S = n/2 [2a + (n-1) d]
5. If l is the last term of the finite AP, say the nth term, then the sum of all terms of the AP is given by : S = n/2 (a + l)
    """,

    "Introduction to Trigonometry": """
1. In a right triangle ABC, right-angled at B, sin A = (side opposite to angle A)/hypotenuse, cos A = (side adjacent to angle A)/hypotenuse, tan A = (side opposite to angle A)/(side adjacent to angle A).
2. cosec A = 1/sin A; sec A = 1/cos A; cot A = 1/tan A; tan A = sin A / cos A.
3. If one of the trigonometric ratios of an acute angle is known, the remaining trigonometric ratios of the angle can be easily determined.
4. The values of trigonometric ratios for angles 0°, 30°, 45°, 60° and 90°.
5. The value of sin A or cos A never exceeds 1, whereas the value of sec A (0° ≤ A < 90°) or cosec A (0° < A ≤ 90°) is always greater than or equal to 1.
6. sin^2 A + cos^2 A = 1, sec^2 A – tan^2 A = 1 for 0° ≤ A < 90°, cosec^2 A = 1 + cot^2 A for 0° < A ≤ 90°.
    """
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