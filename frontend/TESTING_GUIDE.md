# Frontend API Integration - Quick Test Guide

## Prerequisites
1. Backend running on `http://localhost:8000`
2. Frontend running on `http://localhost:5173` (Vite default)
3. Database with sample data initialized

## Testing Workflow

### Step 1: Start Backend
```powershell
cd .\backend
.\venv\Scripts\activate
python -m uvicorn main:app --reload
```

Expected output: `Uvicorn running on http://127.0.0.1:8000`

### Step 2: Start Frontend
```powershell
cd ..
npm install  # if not already installed
npm run dev
```

Expected output: `VITE v5.x.x  ready in x ms`

### Step 3: Test in Browser
1. Open `http://localhost:5173`
2. You should see the FilterPanel load dynamically with grades
3. Select Grade → Subjects appear
4. Select Subject → Chapters appear
5. Select Chapter → Topics appear
6. Select Topic → Generate button enables
7. Click Generate → Worksheet with questions appears
8. Save worksheet → Dialog appears, can save

## Expected API Calls (Network Tab)

### Initial Load
- `GET /api/grades` → Returns list of grades (Grade 1-12)

### Grade Selection
- `GET /api/grades/{grade_id}/subjects` → Returns subjects for grade

### Subject Selection
- `GET /api/subjects/{subject_id}/chapters` → Returns chapters

### Chapter Selection
- `GET /api/chapters/{chapter_id}/topics` → Returns topics

### Generate Click
- `POST /api/generate-worksheet` → Returns array of questions
  - Input: topic_id, mcq_count, short_answer_count, long_answer_count, difficulty
  - Output: Array of Question objects with id, type, text, options, correct_answer, etc.

### Save Click
- `POST /api/worksheets` → Returns saved worksheet
  - Input: id, name, topic_id, question_ids
  - Output: Worksheet object with created_at, updated_at

## Troubleshooting

### "Cannot GET /api/grades"
- Backend not running
- Check `http://localhost:8000` is accessible
- Backend CORS configured for localhost

### Questions not generating
- OpenRouter API key not set in `.env`
- Backend will use mock fallback data
- Check console logs in browser Network tab

### Type errors
- Clear node_modules: `rm -r node_modules` then `npm install`
- Restart dev server: `npm run dev`

### Database issues
- Backend initializes grades automatically
- Check `backend/database.py` for database location
- Run `python backend/init_sample_data.py` to add sample data

## Data Structure Example

### Generated Question Response
```json
{
  "id": "q-uuid",
  "type": "mcq",
  "text": "Question text here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": 2,
  "explanation": "Explanation of why answer C is correct",
  "images": [],
  "difficulty": "medium",
  "marks": 1,
  "topic_id": "topic-uuid",
  "user_id": "dev-user",
  "created_at": "2025-12-03T10:00:00"
}
```

## Component Hierarchy

```
App.tsx
└── BrowserRouter
    └── Index.tsx (Main Page)
        ├── Header.tsx
        ├── FilterPanel.tsx (Left sidebar)
        │   └── Calls: getGrades, getSubjectsByGrade, getChapters, getTopics
        │   └── Calls: generateWorksheet (on Generate click)
        └── ResultsPanel.tsx (Main content)
            ├── QuestionCard.tsx (Multiple)
            │   └── Displays question with edit/regenerate options
            └── Save Dialog
                └── Calls: saveWorksheet
```

## API Service Functions (src/lib/api.ts)

All functions are async and return typed responses:

```typescript
// Grades
getGrades(): Promise<Grade[]>

// Subjects
getSubjectsByGrade(gradeId): Promise<Subject[]>
getSubjects(): Promise<Subject[]>

// Chapters
getChapters(subjectId): Promise<Chapter[]>

// Topics
getTopics(chapterId): Promise<Topic[]>

// Questions
generateWorksheet(topicId, mcqCount, shortAnswerCount, longAnswerCount, difficulty, includeImages): Promise<Question[]>
getQuestions(topicId?, token?): Promise<Question[]>
getQuestion(questionId, token?): Promise<Question>

// Worksheets
saveWorksheet(name, topicId, questionIds, token?): Promise<Worksheet>
getWorksheets(token?): Promise<Worksheet[]>
getWorksheet(worksheetId, token?): Promise<Worksheet>
deleteWorksheet(worksheetId, token?): Promise<{message: string}>
```

## Development Notes

- Frontend state management uses React hooks (useState)
- React Query not used for API (can be added later for caching)
- Drag-and-drop implemented with @dnd-kit
- Toast notifications via Sonner/shadcn
- Dark theme applied by default
- Question types: 'mcq' | 'short' | 'long' (from backend)

## Next Steps (Optional)

1. Add React Query for better API state management
2. Add authentication (login/register forms)
3. Add saved worksheets viewing/downloading
4. Add PDF export functionality
5. Add image upload for custom questions
6. Add user dashboard for worksheet history
