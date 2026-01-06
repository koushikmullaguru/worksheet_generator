const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Types
export interface Grade {
  id: string;
  name: string;
  description?: string;
}

export interface Subject {
  id: string;
  name: string;
  description?: string;
  grade_id: string;
}

export interface Chapter {
  id: string;
  name: string;
  description?: string;
  subject_id: string;
}

export interface Topic {
  id: string;
  name: string;
  description?: string;
  chapter_id: string;
  subtopics: string[];
}

export interface Question {
  id: string;
  type: "mcq" | "short" | "long" | "image";
  text: string;
  options: string[];
  correct_answer: number | string | number[];
  explanation: string;
  images: string[];
  difficulty: "easy" | "medium" | "hard";
  marks: number;
  topic_id: string;
  user_id: string;
  created_at: string;
}

export interface Worksheet {
  id: string;
  name: string;
  topic_id: string;
  user_id: string;
  question_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface QuizAnswer {
  id: string;
  user_id: string;
  question_id: string;
  worksheet_id: string;
  user_answer: number | string | number[];
  is_correct: boolean;
  created_at: string;
}

export interface QuizAnswerCreate {
  question_id: string;
  worksheet_id?: string;
  user_answer: number | string | number[];
}

export interface QuizResult {
  id: string;
  user_id: string;
  worksheet_id: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
  completed_at: string;
}

export interface QuizResultCreate {
  worksheet_id: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
}

export interface QuizFeedback {
  id: string;
  user_id: string;
  worksheet_id: string;
  feedback_type: "thumbs_up" | "thumbs_down";
  comment?: string;
  created_at: string;
}

export interface QuizFeedbackCreate {
  worksheet_id: string;
  feedback_type: "thumbs_up" | "thumbs_down";
  comment?: string;
}

export interface QuizSubmission {
  worksheet_id?: string;
  answers: QuizAnswerCreate[];
}

// Helper function for API requests
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error: ${response.status} - ${error}`);
  }

  return response.json();
}

// API Functions
export async function getGrades(): Promise<Grade[]> {
  return apiRequest<Grade[]>("/api/grades");
}

export async function getSubjectsByGrade(gradeId: string): Promise<Subject[]> {
  return apiRequest<Subject[]>(`/api/grades/${gradeId}/subjects`);
}

export async function getSubjects(): Promise<Subject[]> {
  return apiRequest<Subject[]>("/api/subjects");
}

export async function getChapters(subjectId: string): Promise<Chapter[]> {
  return apiRequest<Chapter[]>(`/api/subjects/${subjectId}/chapters`);
}

export async function getTopics(chapterId: string): Promise<Topic[]> {
  return apiRequest<Topic[]>(`/api/chapters/${chapterId}/topics`);
}

export async function generateWorksheet(
  request: QuizGenerationRequest,
  token: string
): Promise<Question[]> {
  return apiRequest<Question[]>("/api/generate-worksheet", {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export interface QuizGenerationRequest {
  topic_id: string;
  mcq_count: number;
  short_answer_count: number;
  long_answer_count: number;
  difficulty?: "easy" | "medium" | "hard";
  include_images: boolean;
  subject_name: string;
  generate_real_images?: boolean;
  use_blooms_taxonomy?: boolean;
  blooms_taxonomy_level?: 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create';
}

export interface ExamGenerationRequest {
  topic_ids: string[];
  mcq_count: number;
  short_answer_count: number;
  long_answer_count: number;
  difficulty?: "easy" | "medium" | "hard";
  include_images: boolean;
  subject_name: string;
  generate_real_images?: boolean;
  use_blooms_taxonomy?: boolean;
  blooms_taxonomy_level?: 'remember' | 'understand' | 'apply' | 'analyze' | 'evaluate' | 'create';
}

export async function generateQuiz(
  request: QuizGenerationRequest,
  token: string
): Promise<Question[]> {
  return apiRequest<Question[]>("/api/generate-quiz", {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function generateExam(
  request: ExamGenerationRequest,
  token: string
): Promise<Question[]> {
  return apiRequest<Question[]>("/api/generate-exam", {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function saveWorksheet(
  name: string,
  topicId: string,
  questionIds: string[],
  token: string
): Promise<Worksheet> {
  return apiRequest<Worksheet>("/api/worksheets", {
    method: 'POST',
    body: JSON.stringify({
      id: `ws-${Date.now()}`,
      name,
      topic_id: topicId,
      question_ids: questionIds,
    }),
  });
}

export async function getWorksheet(worksheetId: string, token: string): Promise<Worksheet> {
  return apiRequest<Worksheet>(`/api/worksheets/${worksheetId}`);
}

export async function submitQuizAnswers(
  submission: QuizSubmission,
  token: string
): Promise<QuizAnswer[]> {
  return apiRequest<QuizAnswer[]>("/api/quiz-answers", {
    method: 'POST',
    body: JSON.stringify(submission),
  });
}

export async function getQuizAnswers(
  worksheetId: string,
  token: string
): Promise<QuizAnswer[]> {
  return apiRequest<QuizAnswer[]>(`/api/quiz-answers?worksheet_id=${worksheetId}`);
}

export async function getQuizResults(
  worksheetId: string,
  token: string
): Promise<QuizResult[]> {
  return apiRequest<QuizResult[]>(`/api/quiz-results?worksheet_id=${worksheetId}`);
}

export async function getQuizResult(
  resultId: string,
  token: string
): Promise<QuizResult> {
  return apiRequest<QuizResult>(`/api/quiz-results/${resultId}`);
}

export async function submitQuizFeedback(
  feedback: QuizFeedbackCreate,
  token: string
): Promise<QuizFeedback> {
  return apiRequest<QuizFeedback>("/api/quiz-feedback", {
    method: 'POST',
    body: JSON.stringify(feedback),
  });
}

export async function getQuizFeedback(
  worksheetId: string,
  token: string
): Promise<QuizFeedback[]> {
  return apiRequest<QuizFeedback[]>(`/api/quiz-feedback?worksheet_id=${worksheetId}`);
}