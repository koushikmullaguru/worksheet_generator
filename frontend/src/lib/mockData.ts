export interface Question {
  id: string;
  type: 'mcq' | 'short' | 'long' | 'image';
  text: string;
  options?: string[];
  correct_answer?: number | number[] | string;
  correctAnswer?: number | number[];
  explanation: string;
  images?: string[];
  difficulty: 'easy' | 'medium' | 'hard';
  marks: number;
  topic_id?: string;
  user_id?: string;
}

export interface Topic {
  id: string;
  name: string;
  subtopics: string[];
  chapter_id?: string;
  description?: string;
}

export interface Chapter {
  id: string;
  name: string;
  topics?: Topic[];
  subject_id?: string;
  description?: string;
}

export interface Subject {
  id: string;
  name: string;
  chapters?: Chapter[];
  grade_id?: string;
  description?: string;
}

export interface Grade {
  id: string;
  name: string;
  description?: string;
}

export const boards = ['CBSE', 'ICSE', 'State Board'];
export const grades = ['7', '8', '9', '10', '11', '12'];

export const subjects: Subject[] = [
  {
    id: 'math-grade-10',
    name: 'Mathematics',
    chapters: [
      {
        id: 'math-grade-10-chapter-real-numbers',
        name: 'Real Numbers',
        topics: [
          {
            id: 'math-grade-10-chapter-real-numbers-topic-real-numbers',
            name: 'Real Numbers',
            subtopics: ['Fundamental Theorem of Arithmetic', 'Irrational Numbers', 'Decimal Expansion']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-polynomials',
        name: 'Polynomials',
        topics: [
          {
            id: 'math-grade-10-chapter-polynomials-topic-polynomials',
            name: 'Polynomials',
            subtopics: ['Geometrical Meaning of Zeroes', 'Relationship between Zeroes and Coefficients', 'Division Algorithm for Polynomials']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-pair-of-linear-equations',
        name: 'Pair of Linear Equations in Two Variables',
        topics: [
          {
            id: 'math-grade-10-chapter-pair-of-linear-equations-topic-pair-of-linear-equations',
            name: 'Pair of Linear Equations in Two Variables',
            subtopics: ['Graphical Method', 'Algebraic Methods', 'Consistency of Linear Equations']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-quadratic-equations',
        name: 'Quadratic Equations',
        topics: [
          {
            id: 'math-grade-10-chapter-quadratic-equations-topic-quadratic-equations',
            name: 'Quadratic Equations',
            subtopics: ['Standard Form', 'Solution by Factorization', 'Nature of Roots']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-arithmetic-progressions',
        name: 'Arithmetic Progressions',
        topics: [
          {
            id: 'math-grade-10-chapter-arithmetic-progressions-topic-arithmetic-progressions',
            name: 'Arithmetic Progressions',
            subtopics: ['nth Term of an AP', 'Sum of First n Terms of an AP']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-triangles',
        name: 'Triangles',
        topics: [
          {
            id: 'math-grade-10-chapter-triangles-topic-triangles',
            name: 'Triangles',
            subtopics: ['Similarity of Triangles', 'Basic Proportionality Theorem', 'Criteria for Similarity of Triangles']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-coordinate-geometry',
        name: 'Coordinate Geometry',
        topics: [
          {
            id: 'math-grade-10-chapter-coordinate-geometry-topic-coordinate-geometry',
            name: 'Coordinate Geometry',
            subtopics: ['Distance Formula', 'Section Formula']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-introduction-to-trigonometry',
        name: 'Introduction to Trigonometry',
        topics: [
          {
            id: 'math-grade-10-chapter-introduction-to-trigonometry-topic-introduction-to-trigonometry',
            name: 'Introduction to Trigonometry',
            subtopics: ['Trigonometric Ratios', 'Trigonometric Identities']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-applications-of-trigonometry',
        name: 'Some Applications of Trigonometry',
        topics: [
          {
            id: 'math-grade-10-chapter-applications-of-trigonometry-topic-applications-of-trigonometry',
            name: 'Some Applications of Trigonometry',
            subtopics: ['Heights and Distances', 'Angle of Elevation and Depression']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-circles',
        name: 'Circles',
        topics: [
          {
            id: 'math-grade-10-chapter-circles-topic-circles',
            name: 'Circles',
            subtopics: ['Tangent to a Circle', 'Number of Tangents from a Point to a Circle']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-areas-related-to-circles',
        name: 'Areas Related to Circles',
        topics: [
          {
            id: 'math-grade-10-chapter-areas-related-to-circles-topic-areas-related-to-circles',
            name: 'Areas Related to Circles',
            subtopics: ['Perimeter and Area of a Circle', 'Areas of Sector and Segment of a Circle']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-surface-areas-and-volumes',
        name: 'Surface Areas and Volumes',
        topics: [
          {
            id: 'math-grade-10-chapter-surface-areas-and-volumes-topic-surface-areas-and-volumes',
            name: 'Surface Areas and Volumes',
            subtopics: ['Surface Area of Combined Solids', 'Volume of Combined Solids']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-statistics',
        name: 'Statistics',
        topics: [
          {
            id: 'math-grade-10-chapter-statistics-topic-statistics',
            name: 'Statistics',
            subtopics: ['Mean of Grouped Data', 'Mode of Grouped Data', 'Median of Grouped Data']
          }
        ]
      },
      {
        id: 'math-grade-10-chapter-probability',
        name: 'Probability',
        topics: [
          {
            id: 'math-grade-10-chapter-probability-topic-probability',
            name: 'Probability',
            subtopics: ['Theoretical Probability', 'Simple Events']
          }
        ]
      }
    ]
  }
];

export const questionTypes = ['MCQ', 'Short Answer', 'Long Answer', 'Image-based'];

const sampleQuestions: Question[] = [
  {
    id: 'q-1',
    type: 'image',
    text: 'Observe the diagram of a neuron and identify the parts labeled A, B, and C.',
    options: ['A: Dendrites, B: Cell body, C: Axon', 'A: Axon, B: Dendrites, C: Cell body', 'A: Cell body, B: Axon, C: Dendrites', 'A: Dendrites, B: Axon, C: Cell body'],
    correctAnswer: 0,
    explanation: 'Dendrites receive signals from other neurons, the cell body contains the nucleus and processes information, and the axon transmits electrical impulses away from the cell body.',
    images: ['https://images.unsplash.com/photo-1559757175-0eb30cd8c063?w=400'],
    difficulty: 'medium',
    marks: 3
  },
  {
    id: 'q-2',
    type: 'mcq',
    text: 'Which part of the brain controls involuntary actions such as heartbeat and breathing?',
    options: ['Cerebrum', 'Cerebellum', 'Medulla oblongata', 'Hypothalamus'],
    correctAnswer: 2,
    explanation: 'The medulla oblongata is located in the brainstem and controls vital involuntary functions like heartbeat, breathing, and blood pressure regulation.',
    difficulty: 'easy',
    marks: 1
  },
  {
    id: 'q-3',
    type: 'short',
    text: 'Explain the difference between a reflex action and a voluntary action with one example each.',
    explanation: 'Reflex actions are automatic, involuntary responses that occur without conscious thought (e.g., pulling hand away from a hot surface). Voluntary actions are conscious, deliberate movements controlled by the brain (e.g., writing or walking).',
    difficulty: 'medium',
    marks: 3
  },
  {
    id: 'q-4',
    type: 'mcq',
    text: 'What is the gap between two neurons called?',
    options: ['Dendrite', 'Axon', 'Synapse', 'Neurotransmitter'],
    correctAnswer: 2,
    explanation: 'A synapse is the junction between two neurons where neurotransmitters are released to transmit signals from one neuron to another.',
    difficulty: 'easy',
    marks: 1
  },
  {
    id: 'q-5',
    type: 'image',
    text: 'Study the diagram showing a reflex arc. What is the correct pathway of the nerve impulse?',
    options: ['Receptor → Sensory neuron → Brain → Motor neuron → Effector', 'Receptor → Sensory neuron → Spinal cord → Motor neuron → Effector', 'Receptor → Motor neuron → Spinal cord → Sensory neuron → Effector', 'Receptor → Spinal cord → Brain → Effector'],
    correctAnswer: 1,
    explanation: 'In a reflex arc, the impulse travels from receptor to sensory neuron, then to the spinal cord (not brain), and through motor neuron to effector. This bypasses the brain for faster response.',
    images: ['https://images.unsplash.com/photo-1576086213369-97a306d36557?w=400'],
    difficulty: 'hard',
    marks: 3
  }
];

export function generateQuestions(count: number, types: string[]): Question[] {
  const filtered = sampleQuestions.filter(q =>
    types.length === 0 || types.includes(q.type === 'image' ? 'Image-based' : q.type === 'mcq' ? 'MCQ' : q.type === 'short' ? 'Short Answer' : 'Long Answer')
  );
  
  const questions: Question[] = [];
  for (let i = 0; i < count; i++) {
    const base = filtered[i % filtered.length];
    questions.push({
      ...base,
      id: `q-${Date.now()}-${i}`
    });
  }
  
  return questions;
}
