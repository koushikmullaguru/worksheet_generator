# Classroom Canvas Backend

This is the backend API for the Classroom Canvas application, built with FastAPI and PostgreSQL.

## Features

- User authentication with JWT tokens
- Content management for subjects, chapters, and topics
- Worksheet generation using multimodal LLM (Google Gemini 2.0 Flash)
- Question and worksheet management
- PostgreSQL database integration

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- PostgreSQL database
- OpenRouter API key for LLM access

### 2. Installation

1. Clone this repository
2. Navigate to the backend directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Database Setup

1. Create a PostgreSQL database
2. Update the database connection string in the `.env` file:

```
DATABASE_URL=postgresql://username:password@localhost/classroom_canvas
```

3. Run the database migrations:

```bash
python seed_data.py
```

### 4. Environment Configuration

Create a `.env` file in the root directory and add the following:

```
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/classroom_canvas

# Security Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenRouter API Configuration
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Application Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### 5. Running the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 6. API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token

### Content Management

- `GET /api/subjects` - Get all subjects
- `GET /api/subjects/{subject_id}/chapters` - Get chapters for a subject
- `GET /api/chapters/{chapter_id}/topics` - Get topics for a chapter

### Worksheet Generation

- `POST /api/generate-worksheet` - Generate a worksheet using LLM

### Question Management

- `GET /api/questions` - Get questions (optionally filtered by topic)

### Worksheet Management

- `POST /api/worksheets` - Save a worksheet
- `GET /api/worksheets` - Get user's worksheets
- `GET /api/worksheets/{worksheet_id}` - Get a specific worksheet
- `DELETE /api/worksheets/{worksheet_id}` - Delete a worksheet

## Frontend Integration

The frontend is a React application that connects to this backend API. See the frontend documentation for integration details.

## LLM Integration

This application uses Google Gemini 2.0 Flash via OpenRouter for worksheet generation. You need an OpenRouter API key to use this feature.

## License

This project is licensed under the MIT License.