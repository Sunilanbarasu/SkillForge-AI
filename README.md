# SkillForge AI

**SkillForge AI** is an AI-powered adaptive placement preparation platform for college students preparing for software engineering placements.

---

## Central Core Loop

```
ASSESS → ANALYZE → PERSONALIZE → PRACTICE → REASSESS → ADAPT
```

The system maintains each student's skill profile, measures performance across core computer science & software engineering topics, and continuously updates personalized study plans when new assessment results become available.

---

## Tech Stack

- **Frontend**: React + Vite + JavaScript
- **Backend**: Python + FastAPI
- **Database**: PostgreSQL (via SQLAlchemy ORM)
- **Authentication**: JWT (`PyJWT` + direct `bcrypt` password hashing)
- **API Architecture**: REST
- **AI**: Gemini API

---

## Project Structure

```
SkillForge-AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── assessments.py
│   │   │       │   ├── auth.py
│   │   │       │   ├── health.py
│   │   │       │   ├── profile.py
│   │   │       │   └── users.py
│   │   │       └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── seed_questions.py
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── assessment.py
│   │   │   ├── profile.py
│   │   │   ├── question.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── assessment.py
│   │   │   ├── auth.py
│   │   │   └── profile.py
│   │   └── main.py
│   ├── .env.example
│   ├── .env
│   ├── requirements.txt
│   ├── test_phase2.py
│   └── test_phase3.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── components/
│   │   │   ├── Assessment.jsx
│   │   │   ├── HealthStatus.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Profile.jsx
│   │   │   └── Register.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── .gitignore
└── README.md
```

---

## Setup & Local Run Instructions

### 1. Database Configuration (PostgreSQL)
Ensure PostgreSQL is running locally on port 5432. Create a database named `skillforge_ai`:
```sql
CREATE DATABASE skillforge_ai;
```

Update `backend/.env`:
```env
DATABASE_URL="postgresql://postgres:<your_password>@localhost:5432/skillforge_ai"
SECRET_KEY="your-secure-jwt-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 2. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Backend API will be accessible at `http://localhost:8000`  
Interactive API Docs (Swagger): `http://localhost:8000/docs`

### 3. Frontend Setup (React + Vite)
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Frontend development server will run at `http://localhost:5173`.

---

## API Endpoints (v1)

### Public Endpoints
- `GET /api/v1/health` - Verify backend & PostgreSQL connection health
- `POST /api/v1/auth/register` - Register new student account (`name`, `email`, `password`)
- `POST /api/v1/auth/login` - Authenticate student and obtain JWT access token

### Protected Endpoints (Requires `Authorization: Bearer <token>`)
- `GET /api/v1/users/me` - Retrieve current authenticated student user info
- `GET /api/v1/profile` - Retrieve student target role & skill preferences
- `PUT /api/v1/profile` - Update target role, experience level, interests, and selected skills (`Python`, `C`, `DSA`, `SQL`, `OOP`, `DBMS`, `Aptitude`)
- `POST /api/v1/assessments/start` - Initialize new diagnostic placement assessment & fetch questions (without correct answers)
- `POST /api/v1/assessments/{id}/submit` - Submit student choices for server-side evaluation & skill-wise scoring
- `GET /api/v1/assessments/history` - Retrieve student's past completed assessment history
- `GET /api/v1/assessments/{id}/result` - Fetch detailed overall & skill-wise performance result
