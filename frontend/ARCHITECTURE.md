# Integration Architecture

## Frontend → Backend Communication

```
┌─────────────────────────────────────────────────────────────────┐
│                       React Frontend                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Index.tsx                                                   │ │
│  │ ├─ State: questions, isGenerating, currentTopic            │ │
│  │ └─ Handlers: handleGenerate()                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│         ↓                                          ↓              │
│  ┌─────────────────┐                      ┌──────────────────┐  │
│  │ FilterPanel.tsx │                      │ ResultsPanel.tsx │  │
│  │                 │                      │                  │  │
│  │ State:          │                      │ State:           │  │
│  │ - grade         │ ────────────────→   │ - showAnswers    │  │
│  │ - subject       │ worksheet filters   │ - saveDialogOpen │  │
│  │ - chapter       │                      │ - worksheetName  │  │
│  │ - topic         │ ←────────────────   │ - isSaving       │  │
│  │ - difficulty    │ generated questions │                  │  │
│  │ - mcqCount      │                      │ Renders:         │  │
│  │ - shortCount    │                      │ - QuestionCard   │  │
│  │ - longCount     │                      │ - Save Dialog    │  │
│  │                 │                      │ - Answer Toggle  │  │
│  │ Calls:          │                      │                  │  │
│  │ → getGrades()   │                      │ Calls:           │  │
│  │ → getSubjects() │                      │ → saveWorksheet()│  │
│  │ → getChapters() │                      │                  │  │
│  │ → getTopics()   │                      │                  │  │
│  │ → generateWS()  │                      │                  │  │
│  └─────────────────┘                      └──────────────────┘  │
│         ↓                                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ src/lib/api.ts                                             │ │
│  │                                                             │ │
│  │ API Service Layer                                          │ │
│  │ ├─ Type Definitions (Question, Grade, Subject, etc.)      │ │
│  │ ├─ getGrades()                                             │ │
│  │ ├─ getSubjectsByGrade(gradeId)                             │ │
│  │ ├─ getChapters(subjectId)                                  │ │
│  │ ├─ getTopics(chapterId)                                    │ │
│  │ ├─ generateWorksheet(topicId, ...)                         │ │
│  │ ├─ getQuestions(topicId)                                   │ │
│  │ ├─ saveWorksheet(name, topicId, questionIds)               │ │
│  │ └─ deleteWorksheet(worksheetId)                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│         ↓                                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ HTTP Requests                                              │ │
│  │ Content-Type: application/json                             │ │
│  │ Base URL: http://localhost:8000/api                        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ main.py                                                    │ │
│  │                                                             │ │
│  │ GET  /api/grades                 → List[Grade]            │ │
│  │ GET  /api/grades/{id}/subjects   → List[Subject]          │ │
│  │ GET  /api/subjects               → List[Subject]          │ │
│  │ GET  /api/subjects/{id}/chapters → List[Chapter]          │ │
│  │ GET  /api/chapters/{id}/topics   → List[Topic]            │ │
│  │ POST /api/generate-worksheet     → List[Question]         │ │
│  │ GET  /api/questions              → List[Question]         │ │
│  │ POST /api/worksheets             → Worksheet              │ │
│  │ GET  /api/worksheets             → List[Worksheet]        │ │
│  │ GET  /api/worksheets/{id}        → Worksheet              │ │
│  │ DELETE /api/worksheets/{id}      → {message: string}      │ │
│  │                                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│         ↓                                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ LLMService (OpenRouter)                                    │ │
│  │ └─ generate_questions(prompt)                              │ │
│  │    └─ Calls OpenRouter GPT API                             │ │
│  │       └─ Generates educational questions                  │ │
│  │          └─ Returns JSON with question data               │ │
│  └────────────────────────────────────────────────────────────┘ │
│         ↓                                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Database (SQLAlchemy)                                      │ │
│  │                                                             │ │
│  │ Tables:                                                    │ │
│  │ ├─ User                                                    │ │
│  │ ├─ Grade (Grades 1-12)                                    │ │
│  │ ├─ Subject                                                 │ │
│  │ ├─ Chapter                                                 │ │
│  │ ├─ Topic                                                   │ │
│  │ ├─ Question (Generated)                                    │ │
│  │ └─ Worksheet (User worksheets)                             │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy with API Calls

```
<App />
│
└── <BrowserRouter>
    │
    └── <Routes>
        │
        └── <Index /> (Main Page)
            │
            ├── <Header />
            │
            └── <div className="flex">
                │
                ├── <FilterPanel />
                │   │
                │   ├─ useEffect: getGrades()
                │   │   API Call: GET /api/grades
                │   │   Response: Grade[]
                │   │
                │   ├─ useEffect: getSubjectsByGrade(grade)
                │   │   API Call: GET /api/grades/{id}/subjects
                │   │   Response: Subject[]
                │   │
                │   ├─ useEffect: getChapters(subject)
                │   │   API Call: GET /api/subjects/{id}/chapters
                │   │   Response: Chapter[]
                │   │
                │   ├─ useEffect: getTopics(chapter)
                │   │   API Call: GET /api/chapters/{id}/topics
                │   │   Response: Topic[]
                │   │
                │   └─ onClick (Generate Button):
                │       API Call: POST /api/generate-worksheet
                │       Payload: {
                │         "topic_id": "...",
                │         "mcq_count": 5,
                │         "short_answer_count": 3,
                │         "long_answer_count": 2,
                │         "difficulty": "medium",
                │         "include_images": false
                │       }
                │       Response: Question[]
                │
                └── <ResultsPanel questions={questions}>
                    │
                    ├── Displays questions
                    │   └── <QuestionCard /> (Multiple)
                    │       ├── Display question text
                    │       ├── Edit functionality
                    │       ├── Toggle answer visibility
                    │       └── Drag-and-drop reordering
                    │
                    └── <Dialog> (Save Worksheet)
                        │
                        └── onClick (Save Button):
                            API Call: POST /api/worksheets
                            Payload: {
                              "id": "ws-...",
                              "name": "My Worksheet",
                              "topic_id": "...",
                              "question_ids": [...]
                            }
                            Response: Worksheet
```

## State Management Flow

```
User Interaction
       ↓
┌──────────────────┐
│ FilterPanel      │
│ State Updates    │
└──────────────────┘
       ↓
┌──────────────────────────────┐
│ API Call via api.ts          │
│ (getGrades, getSubjects,     │
│  getChapters, getTopics,     │
│  generateWorksheet)          │
└──────────────────────────────┘
       ↓ Response
┌──────────────────┐
│ Index Component  │
│ Updates State    │
│ (questions, etc) │
└──────────────────┘
       ↓
┌──────────────────┐
│ ResultsPanel     │
│ Re-renders with  │
│ new Questions    │
└──────────────────┘
```

## Question Generation Flow

```
User selects Grade/Subject/Chapter/Topic
                    ↓
              Clicks "Generate"
                    ↓
    ┌───────────────────────────────┐
    │ handleGenerate() in Index.tsx  │
    │ Creates filter object:         │
    │ - topic                        │
    │ - mcqCount                     │
    │ - shortAnswerCount             │
    │ - longAnswerCount              │
    │ - difficulty                   │
    └───────────────────────────────┘
                    ↓
    ┌───────────────────────────────┐
    │ API Call:                      │
    │ generateWorksheet(             │
    │   topicId,                     │
    │   mcqCount,                    │
    │   shortAnswerCount,            │
    │   longAnswerCount,             │
    │   difficulty,                  │
    │   false,                       │
    │   ''                           │
    │ )                              │
    └───────────────────────────────┘
                    ↓
    ┌───────────────────────────────┐
    │ Backend: POST /generate-ws     │
    │ 1. Get Topic details           │
    │ 2. Get Chapter details         │
    │ 3. Get Subject details         │
    │ 4. Build LLM prompt            │
    │ 5. Call OpenRouter API         │
    │ 6. Parse LLM response          │
    │ 7. Save to database            │
    │ 8. Return Question[]           │
    └───────────────────────────────┘
                    ↓
    ┌───────────────────────────────┐
    │ Frontend: Render Questions     │
    │ Display in ResultsPanel        │
    │ Show answer toggle             │
    │ Enable save/edit/delete        │
    └───────────────────────────────┘
                    ↓
            User saves worksheet
                    ↓
    ┌───────────────────────────────┐
    │ API Call:                      │
    │ saveWorksheet(                 │
    │   worksheetName,               │
    │   topicId,                     │
    │   questionIds                  │
    │ )                              │
    └───────────────────────────────┘
                    ↓
    ┌───────────────────────────────┐
    │ Backend: POST /worksheets      │
    │ 1. Validate worksheet data     │
    │ 2. Create worksheet record     │
    │ 3. Save to database            │
    │ 4. Return Worksheet object     │
    └───────────────────────────────┘
                    ↓
            Success Toast shown
```

## API Response Examples

### GET /api/grades
```json
[
  {"id": "grade-1", "name": "Grade 1"},
  {"id": "grade-2", "name": "Grade 2"},
  ...
  {"id": "grade-12", "name": "Grade 12"}
]
```

### GET /api/grades/grade-10/subjects
```json
[
  {
    "id": "biology",
    "name": "Biology",
    "grade_id": "grade-10"
  },
  {
    "id": "physics",
    "name": "Physics",
    "grade_id": "grade-10"
  }
]
```

### POST /api/generate-worksheet (Response)
```json
[
  {
    "id": "q-uuid-1",
    "type": "mcq",
    "text": "Which organelle is responsible for energy production?",
    "options": ["Nucleus", "Mitochondria", "Endoplasmic Reticulum", "Golgi Apparatus"],
    "correct_answer": 1,
    "explanation": "Mitochondria is the powerhouse of the cell",
    "images": [],
    "difficulty": "easy",
    "marks": 1,
    "topic_id": "topic-1",
    "user_id": "dev-user",
    "created_at": "2025-12-03T10:00:00"
  }
]
```

### POST /api/worksheets (Response)
```json
{
  "id": "ws-1701577200000",
  "name": "Cell Structure - Practice Set 1",
  "topic_id": "topic-1",
  "question_ids": ["q-uuid-1", "q-uuid-2", "q-uuid-3"],
  "user_id": "dev-user",
  "created_at": "2025-12-03T10:05:00",
  "updated_at": "2025-12-03T10:05:00"
}
```

## Error Handling

```
API Call
   ↓
Response Status Check
   ├─ 2xx Success → Parse JSON & Return
   │
   └─ 4xx/5xx Error → Throw Error
                ↓
            Catch in Component
                ↓
            Display Toast Notification
                ↓
            Log to Console
                ↓
            Graceful Degradation
```

## Authentication (Future Enhancement)

Currently bypassed in development:
- Backend: `verify_token()` returns default dev-user
- Frontend: All API calls optional with token parameter

For production:
1. Add Login/Register forms
2. Store JWT token in localStorage
3. Pass token to all API calls
4. Handle 401 Unauthorized responses
5. Redirect to login on token expiry
