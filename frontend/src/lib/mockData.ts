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
    id: 'biology',
    name: 'Biology',
    chapters: [
      {
        id: 'control-coordination',
        name: 'Control and Coordination',
        topics: [
          {
            id: 'nervous-system',
            name: 'Animals - Nervous System',
            subtopics: ['Neurons', 'Reflex Actions', 'Brain Structure']
          },
          {
            id: 'hormones',
            name: 'Chemical Coordination',
            subtopics: ['Endocrine Glands', 'Hormones', 'Feedback Mechanism']
          }
        ]
      },
      {
        id: 'reproduction',
        name: 'How Do Organisms Reproduce',
        topics: [
          {
            id: 'asexual',
            name: 'Asexual Reproduction',
            subtopics: ['Binary Fission', 'Budding', 'Fragmentation']
          }
        ]
      }
    ]
  },
  {
    id: 'physics',
    name: 'Physics',
    chapters: [
      {
        id: 'electricity',
        name: 'Electricity',
        topics: [
          {
            id: 'circuits',
            name: 'Electric Circuits',
            subtopics: ['Series', 'Parallel', 'Ohms Law']
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
