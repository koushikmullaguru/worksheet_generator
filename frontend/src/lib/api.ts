const API_BASE_URL = 'http://localhost:8000/api';

// Types
export interface Grade {
  id: string;
  name: string;
  description?: string;
}

export interface Subject {
  id: string;
  name: string;
  grade_id: string;
  description?: string;
}

export interface Chapter {
  id: string;
  name: string;
  subject_id: string;
  description?: string;
}

export interface Topic {
  id: string;
  name: string;
  chapter_id: string;
  subtopics: string[];
  description?: string;
}

// Question schemas
export interface Question {
  id: string;
  type: 'mcq' | 'short' | 'long' | 'image';
  text: string;
  options?: string[];
  correct_answer?: number | number[] | string;
  explanation: string;
  // This array now contains Base64 Data URIs (e.g., "data:image/png;base64,...")
  images?: string[]; 
  difficulty: 'easy' | 'medium' | 'hard';
  marks: number;
  topic_id: string;
  user_id: string;
  created_at?: string;
}

export interface Worksheet {
  id: string;
  name: string;
  topic_id: string;
  question_ids: string[];
  user_id: string;
  created_at?: string;
  updated_at?: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  created_at?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

// Auth APIs
export async function register(username: string, email: string, password: string): Promise<Token> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  return response.json();
}

export async function login(username: string, password: string): Promise<Token> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
}

export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get current user');
  }

  return response.json();
}

// Grade APIs
export async function getGrades(): Promise<Grade[]> {
  const response = await fetch(`${API_BASE_URL}/grades`);

  if (!response.ok) {
    throw new Error('Failed to fetch grades');
  }

  return response.json();
}

// Subject APIs
export async function getSubjects(): Promise<Subject[]> {
  const response = await fetch(`${API_BASE_URL}/subjects`);

  if (!response.ok) {
    throw new Error('Failed to fetch subjects');
  }

  return response.json();
}

export async function getSubjectsByGrade(gradeId: string): Promise<Subject[]> {
  const response = await fetch(`${API_BASE_URL}/grades/${gradeId}/subjects`);

  if (!response.ok) {
    throw new Error('Failed to fetch subjects for grade');
  }

  return response.json();
}

// Chapter APIs
export async function getChapters(subjectId: string): Promise<Chapter[]> {
  const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}/chapters`);

  if (!response.ok) {
    throw new Error('Failed to fetch chapters');
  }

  return response.json();
}

// Topic APIs
export async function getTopics(chapterId: string): Promise<Topic[]> {
  const response = await fetch(`${API_BASE_URL}/chapters/${chapterId}/topics`);

  if (!response.ok) {
    throw new Error('Failed to fetch topics');
  }

  return response.json();
}

// Question APIs
export async function generateWorksheet(
  topicId: string,
  mcqCount: number,
  shortAnswerCount: number,
  longAnswerCount: number,
  difficulty: 'easy' | 'medium' | 'hard' = 'medium',
  includeImages: boolean = false,
  subjectName: string = '', // Added subjectName parameter
  token: string = ''
): Promise<Question[]> {
  const response = await fetch(`${API_BASE_URL}/generate-worksheet`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
    body: JSON.stringify({
      topic_id: topicId,
      mcq_count: mcqCount,
      short_answer_count: shortAnswerCount,
      long_answer_count: longAnswerCount,
      difficulty,
      include_images: includeImages,
      subject_name: subjectName, // CRITICAL FIX: Pass subject name to the backend
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate worksheet');
  }

  return response.json();
}

export async function getQuestions(
  topicId?: string,
  token: string = ''
): Promise<Question[]> {
  let url = `${API_BASE_URL}/questions`;
  if (topicId) {
    url += `?topic_id=${topicId}`;
  }

  const response = await fetch(url, {
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch questions');
  }

  return response.json();
}

export async function getQuestion(
  questionId: string,
  token: string = ''
): Promise<Question> {
  const response = await fetch(`${API_BASE_URL}/questions/${questionId}`, {
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch question');
  }

  return response.json();
}

// Worksheet APIs
export async function saveWorksheet(
  name: string,
  topicId: string,
  questionIds: string[],
  token: string = ''
): Promise<Worksheet> {
  const response = await fetch(`${API_BASE_URL}/worksheets`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
    body: JSON.stringify({
      id: `ws-${Date.now()}`,
      name,
      topic_id: topicId,
      question_ids: questionIds,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to save worksheet');
  }

  return response.json();
}

export async function getWorksheets(token: string = ''): Promise<Worksheet[]> {
  const response = await fetch(`${API_BASE_URL}/worksheets`, {
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch worksheets');
  }

  return response.json();
}

export async function getWorksheet(
  worksheetId: string,
  token: string = ''
): Promise<Worksheet> {
  const response = await fetch(`${API_BASE_URL}/worksheets/${worksheetId}`, {
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch worksheet');
  }

  return response.json();
}

export async function deleteWorksheet(
  worksheetId: string,
  token: string = ''
): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE_URL}/worksheets/${worksheetId}`, {
    method: 'DELETE',
    headers: {
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    throw new Error('Failed to delete worksheet');
  }

  return response.json();
}