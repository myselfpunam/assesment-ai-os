# Assessment AI OS

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.15-red?style=flat)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=flat&logo=postgresql&logoColor=white)
![Groq AI](https://img.shields.io/badge/AI-Groq%20Llama%203.3-F54033?style=flat)
![License](https://img.shields.io/badge/License-Proprietary-lightgrey?style=flat)

Enterprise AI-powered Assessment Management Platform — built with Django REST Framework, PostgreSQL, and Groq AI.

---

## 📖 Full Documentation

> **Looking for the complete API reference, installation guide, and frontend integration map?**
>
> 👉 **[View Full Documentation →](https://claude.ai/code/artifact/c7c670da-f4ea-4f5f-b231-c202f6db8339)**
>
> Interactive docs covering every endpoint, request/response format, and a page-by-page frontend guide.

Lecturers upload course materials (PDF/DOCX/PPTX) and the AI automatically generates quiz questions. Universities can manage departments, programmes, courses, sections, and student enrollments end-to-end.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2, Django REST Framework 3.15 |
| Database | PostgreSQL (psycopg v3) |
| Auth | JWT via SimpleJWT (access + refresh tokens) |
| AI | Groq API — Llama 3.3 70B (free tier) |
| File Parsing | PyMuPDF, python-docx, python-pptx |
| Cache / Queue | Redis + Celery (optional) |
| API Docs | drf-spectacular (Swagger + ReDoc) |

---

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional — only needed for Celery tasks)
- A free Groq API key → [console.groq.com](https://console.groq.com)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/assessment-ai-os.git
cd assessment-ai-os
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Mac / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create PostgreSQL database

```sql
CREATE USER assessment_ai_user WITH PASSWORD 'assessment_ai_password';
CREATE DATABASE assessment_ai_db OWNER assessment_ai_user;
GRANT ALL PRIVILEGES ON DATABASE assessment_ai_db TO assessment_ai_user;
```

### 5. Configure environment variables

Copy the example and fill in your values:

```bash
cp .env.example .env
```

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=assessment_ai_db
DB_USER=assessment_ai_user
DB_PASSWORD=assessment_ai_password
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# AI (free at console.groq.com)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

### 6. Run migrations

```bash
cd assessment_ai
python3 manage.py migrate
```

### 7. Seed roles (required)

```bash
python3 manage.py shell -c "
from apps.roles.models import Role
for name in ['super_admin', 'university_admin', 'lecturer', 'reviewer', 'student']:
    Role.objects.get_or_create(name=name)
print('Roles created.')
"
```

### 8. Create a super admin user

```bash
python3 manage.py createsuperuser
```

### 9. Start the server

```bash
python3 manage.py runserver
```

API is live at `http://127.0.0.1:8000`

### 10. View API documentation

| Interface | URL |
|-----------|-----|
| Swagger UI | [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/) |
| ReDoc | [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/) |
| Raw Schema | [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/) |

---

## API Reference

All endpoints require `Authorization: Bearer <access_token>` in the header unless marked **[Public]**.

Base URL: `http://127.0.0.1:8000`

---

### Authentication

| Method | Endpoint | Description | Frontend Use |
|--------|----------|-------------|--------------|
| POST | `/api/v1/auth/login/` | Login with email + password. Returns access & refresh tokens | Login page |
| POST | `/api/v1/auth/logout/` | Blacklist the refresh token | Logout button |
| POST | `/api/v1/auth/token/refresh/` | Get a new access token using refresh token | Auto token refresh |
| POST | `/api/v1/auth/forgot-password/` | Send password reset email | Forgot password page |
| POST | `/api/v1/auth/reset-password/` | Reset password using OTP | Reset password page |

**Login request body:**
```json
{
  "email": "admin@university.edu",
  "password": "yourpassword"
}
```

**Login response:**
```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "access": "eyJ...",
    "refresh": "eyJ...",
    "user": { "id": "...", "email": "...", "role": "super_admin" }
  }
}
```

---

### Users

| Method | Endpoint | Description | Frontend Use |
|--------|----------|-------------|--------------|
| GET | `/api/v1/users/` | List all users (super admin only) | Admin user list |
| POST | `/api/v1/users/` | Create a new user | Add user form |
| GET | `/api/v1/users/me/` | Get logged-in user's profile | Navbar avatar, profile page |
| PATCH | `/api/v1/users/me/` | Update own profile (name, phone, avatar) | Edit profile form |
| POST | `/api/v1/users/change-password/` | Change own password | Change password form |
| GET | `/api/v1/users/<user_id>/` | Get any user's detail | User detail page |
| PATCH | `/api/v1/users/<user_id>/` | Update a user | Edit user (admin) |
| DELETE | `/api/v1/users/<user_id>/` | Soft delete a user | Remove user |
| GET | `/api/v1/users/<lecturer_id>/teaching-profile/` | Lecturer's full profile + all sections they teach + student/assessment counts | **Lecturer profile page** |

**Roles available:** `super_admin`, `university_admin`, `lecturer`, `reviewer`, `student`

---

### Roles

| Method | Endpoint | Description | Frontend Use |
|--------|----------|-------------|--------------|
| GET | `/api/v1/roles/` | List all system roles | Role dropdown when creating users |

---

### Universities

| Method | Endpoint | Description | Frontend Use |
|--------|----------|-------------|--------------|
| GET | `/api/v1/universities/` | List all universities | University list |
| POST | `/api/v1/universities/` | Create a university | Add university form |
| GET | `/api/v1/universities/<university_id>/` | University detail | University page |
| PATCH | `/api/v1/universities/<university_id>/` | Update university info | Edit university |
| DELETE | `/api/v1/universities/<university_id>/` | Soft delete university | Remove university |
| GET/PATCH | `/api/v1/universities/<university_id>/settings/` | University settings (logo, timezone, etc.) | Settings page |
| GET | `/api/v1/universities/<university_id>/admins/` | List university admins | Admin management |
| DELETE | `/api/v1/universities/<university_id>/admins/<user_id>/` | Remove an admin | Remove admin button |

---

### Academic Structure

The hierarchy is: **University → Department → Programme → Academic Level → Semester**

| Method | Endpoint | Description | Frontend Use |
|--------|----------|-------------|--------------|
| GET | `/api/v1/universities/<university_id>/departments/` | List departments in a university | Department list |
| POST | `/api/v1/universities/<university_id>/departments/` | Create a department | Add department form |
| GET/PATCH/DELETE | `/api/v1/academic/departments/<department_id>/` | Department detail/update/delete | Department page |
| GET | `/api/v1/academic/departments/<department_id>/programmes/` | List programmes in a department | Programme list |
| POST | `/api/v1/academic/departments/<department_id>/programmes/` | Create a programme | Add programme form |
| GET/PATCH/DELETE | `/api/v1/academic/programmes/<programme_id>/` | Programme detail/update/delete | Programme page |
| GET | `/api/v1/academic/programmes/<programme_id>/levels/` | List academic levels (Year 1, Year 2…) | Level list |
| POST | `/api/v1/academic/programmes/<programme_id>/levels/` | Create an academic level | Add level form |
| GET/PATCH/DELETE | `/api/v1/academic/levels/<level_id>/` | Level detail/update/delete | Level page |
| GET | `/api/v1/academic/levels/<level_id>/semesters/` | List semesters in a level | Semester list |
| POST | `/api/v1/academic/levels/<level_id>/semesters/` | Create a semester | Add semester form |
| DELETE | `/api/v1/academic/semesters/<semester_id>/` | Delete a semester | Remove semester |

---

### Courses & Sections

| Method | Endpoint | Description | Frontend Use |
|--------|----------|-------------|--------------|
| GET | `/api/v1/universities/<university_id>/departments/<department_id>/courses/` | List courses in a department | Course list |
| POST | `/api/v1/universities/<university_id>/departments/<department_id>/courses/` | Create a course | Add course form |
| GET/PATCH/DELETE | `/api/v1/courses/<course_id>/` | Course detail/update/delete | Course page |
| GET | `/api/v1/courses/<course_id>/sections/` | List sections of a course | Section list |
| POST | `/api/v1/courses/<course_id>/sections/` | Create a course section | Add section form |
| GET/PATCH/DELETE | `/api/v1/courses/sections/<section_id>/` | Section detail (includes assigned lecturers) | Section page |
| POST | `/api/v1/courses/sections/<section_id>/assign-lecturer/` | Assign a lecturer to a section | Assign lecturer |
| DELETE | `/api/v1/courses/sections/<section_id>/lecturers/<lecturer_id>/` | Remove a lecturer from a section | Remove lecturer |
| GET | `/api/v1/courses/sections/<section_id>/students/` | All students enrolled in a section (with grades) | **Class roster / Lecturer's student list** |

---

### Course Materials

Lecturers upload once — AI uses the extracted text to generate quizzes anytime without re-uploading.

| Method | Endpoint | Description | Frontend Use |
|--------|----------|-------------|--------------|
| GET | `/api/v1/courses/sections/<section_id>/materials/` | List uploaded materials for a section | Materials library |
| POST | `/api/v1/courses/sections/<section_id>/materials/` | Upload PDF/DOCX/PPTX (multipart/form-data) | Upload material button |
| DELETE | `/api/v1/courses/materials/<material_id>/` | Delete a material | Remove material |

**Upload form fields:** `title` (text), `file` (File — PDF, DOCX, or PPTX)

---

### Students & Enrollments

| Method | Endpoint | Description | Frontend Use |
|--------|----------|-------------|--------------|
| GET | `/api/v1/students/batches/` | List all batches | Batch list |
| POST | `/api/v1/students/batches/` | Create a batch | Add batch form |
| GET/PATCH/DELETE | `/api/v1/students/batches/<batch_id>/` | Batch detail/update/delete | Batch page |
| GET | `/api/v1/students/` | List all students | Student list |
| POST | `/api/v1/students/` | Create a student profile | Add student form |
| GET | `/api/v1/students/<student_id>/` | Student profile detail | Student detail page |
| PATCH | `/api/v1/students/<student_id>/` | Update student info | Edit student |
| GET | `/api/v1/students/<student_id>/enrolled-courses/` | All courses a student is enrolled in (with grades, semester, university) | **Student profile page — My Courses** |
| GET | `/api/v1/students/<student_id>/assessments/` | All published quizzes/exams available to a student (based on enrollments) | **Student dashboard — Upcoming Assessments** |
| GET | `/api/v1/students/enrollments/` | List enrollments (filter: `?section_id=` or `?student_id=`) | Admin enrollment list |
| POST | `/api/v1/students/enrollments/` | Enroll a student in a section | Enroll student |
| PATCH | `/api/v1/students/enrollments/<enrollment_id>/` | Update enrollment status or grade | Grade entry, drop |
| DELETE | `/api/v1/students/enrollments/<enrollment_id>/` | Drop a student from a section | Drop student |

---

### Assessments & Question Bank

| Method | Endpoint | Description | Frontend Use |
|--------|----------|-------------|--------------|
| **POST** | `/api/v1/assessments/generate-from-file/` | **AI auto-generate quiz** from uploaded file OR saved material | AI quiz generator |
| GET | `/api/v1/assessments/sections/<section_id>/assessments/` | List all assessments for a section | Assessment list |
| POST | `/api/v1/assessments/sections/<section_id>/assessments/` | Create a manual assessment | Create assessment |
| GET | `/api/v1/assessments/<assessment_id>/` | Assessment detail with all questions | View assessment |
| DELETE | `/api/v1/assessments/<assessment_id>/` | Delete assessment | Remove assessment |
| POST | `/api/v1/assessments/<assessment_id>/publish/` | Publish assessment (makes it visible to students) | Publish button |
| GET | `/api/v1/assessments/<assessment_id>/questions/` | List all questions in an assessment | Question list |
| POST | `/api/v1/assessments/<assessment_id>/questions/` | Add a question manually | Add question form |
| DELETE | `/api/v1/assessments/questions/<question_id>/` | Delete a question | Remove question |
| GET | `/api/v1/assessments/questions/<question_id>/options/` | List options for a question | Options list |
| POST | `/api/v1/assessments/questions/<question_id>/options/` | Add an option to a question | Add option form |
| DELETE | `/api/v1/assessments/options/<option_id>/` | Delete an option | Remove option |

#### AI Quiz Generation — two ways

**Option A: From a saved material (recommended)**
```json
POST /api/v1/assessments/generate-from-file/
Content-Type: application/json

{
  "material_id": "<uuid of uploaded material>",
  "section_id": "<uuid>",
  "title": "Week 3 Quiz",
  "num_questions": 10,
  "question_type": "mcq",
  "topic": "Linked Lists",
  "pass_marks": 5,
  "duration_minutes": 30
}
```

**Option B: One-time file upload**
```
POST /api/v1/assessments/generate-from-file/
Content-Type: multipart/form-data

file: <PDF/DOCX/PPTX>
section_id: <uuid>
title: Week 3 Quiz
num_questions: 10
question_type: mcq
topic: Linked Lists
```

**question_type options:** `mcq` | `true_false` | `mixed` | `short_answer`

---

### Student Attempts & Auto Grading

Students take assessments through these endpoints. MCQ and True/False are graded automatically on submission. Short answer and essays are flagged for manual lecturer review.

| Method | Endpoint | Description | Frontend Use |
|--------|----------|-------------|--------------|
| POST | `/api/v1/attempts/assessments/<assessment_id>/start/` | Start a new attempt (or resume in-progress) | "Start Quiz" button |
| POST | `/api/v1/attempts/<attempt_id>/submit/` | Submit answers — auto-grades MCQ/T-F instantly | "Submit" button |
| GET | `/api/v1/attempts/<attempt_id>/` | View attempt detail with all answers and scores | Results page |
| GET | `/api/v1/attempts/assessments/<assessment_id>/all/` | All attempts for an assessment (lecturer view) | Submissions list |
| GET | `/api/v1/attempts/students/<student_profile_id>/all/` | All attempts by a student | Student attempt history |
| PATCH | `/api/v1/attempts/answers/<answer_id>/grade/` | Manually grade a short answer / essay | Lecturer grading panel |

**Submit body example:**
```json
{
  "answers": [
    {
      "question_id": "<uuid>",
      "selected_option_ids": ["<uuid>"]
    },
    {
      "question_id": "<uuid>",
      "text_answer": "The answer to the short question..."
    }
  ]
}
```

**Manual grading body:**
```json
{
  "marks_obtained": 8,
  "feedback": "Good explanation, missed one key point."
}
```

**Attempt statuses:** `in_progress` → `submitted` → `graded`

---

### Analytics & Results

No new data — pure aggregation over attempt results. All responses are ready for charts/dashboards.

| Method | Endpoint | Description | Frontend Use |
|--------|----------|-------------|--------------|
| GET | `/api/v1/analytics/assessments/<assessment_id>/summary/` | Pass rate, average score, score distribution in 5 bands, manual grading count | Assessment results page |
| GET | `/api/v1/analytics/assessments/<assessment_id>/leaderboard/?limit=10` | Top N students ranked by score | Leaderboard widget |
| GET | `/api/v1/analytics/students/<student_profile_id>/report/` | Student's overall pass rate, average %, per-assessment breakdown | Student performance tab |
| GET | `/api/v1/analytics/sections/<section_id>/report/` | Class enrolled count, per-assessment stats, top 5 students | Lecturer analytics dashboard |

**Assessment summary response example:**
```json
{
  "assessment_title": "Midterm Exam",
  "total_attempts": 45,
  "graded": 43,
  "passed": 31,
  "pass_rate_percent": 72.1,
  "average_percentage": 68.4,
  "highest_score": 95.0,
  "lowest_score": 22.0,
  "needs_manual_grading": 2,
  "score_distribution": {
    "0-20": 1, "21-40": 3, "41-60": 8, "61-80": 19, "81-100": 12
  }
}
```

---

## Standard API Response Format

All endpoints return this shape:

```json
{
  "success": true,
  "message": "Human-readable result message.",
  "data": { }
}
```

Error response:
```json
{
  "success": false,
  "message": "What went wrong.",
  "errors": { "field": ["detail"] }
}
```

---

## Frontend Integration Guide

### Which API goes on which page?

| Page | APIs to call |
|------|-------------|
| **Login** | `POST /auth/login/` |
| **Navbar / Session** | `GET /users/me/` |
| **Dashboard (Admin)** | `GET /universities/`, `GET /users/` |
| **Lecturer Profile Page** | `GET /users/<id>/teaching-profile/` |
| **Lecturer Analytics Dashboard** | `GET /analytics/sections/<id>/report/` |
| **Assessment Results Page** | `GET /analytics/assessments/<id>/summary/`, `GET /analytics/assessments/<id>/leaderboard/` |
| **Grading Panel** | `GET /attempts/assessments/<id>/all/`, `PATCH /attempts/answers/<id>/grade/` |
| **Student Profile Page** | `GET /students/<id>/`, `GET /students/<id>/enrolled-courses/` |
| **Student Performance Tab** | `GET /analytics/students/<id>/report/` |
| **Student Dashboard** | `GET /students/<id>/assessments/` |
| **Student Attempt History** | `GET /attempts/students/<id>/all/` |
| **Take Quiz / Exam** | `POST /attempts/assessments/<id>/start/`, `POST /attempts/<id>/submit/` |
| **View My Results** | `GET /attempts/<id>/` |
| **Class Roster** | `GET /courses/sections/<id>/students/` |
| **Materials Library** | `GET /courses/sections/<id>/materials/` |
| **AI Quiz Generator** | `POST /assessments/generate-from-file/` |
| **Assessment Detail** | `GET /assessments/<id>/` |

### Authentication flow

```
1. POST /api/v1/auth/login/       → store access token + refresh token
2. Every request                  → Authorization: Bearer <access_token>
3. On 401 response                → POST /api/v1/auth/token/refresh/
4. Logout                         → POST /api/v1/auth/logout/
```

---

## Build Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Foundation — Django, PostgreSQL, JWT auth, BaseModel | ✅ Done |
| 2 | RBAC — 5 roles, permission system | ✅ Done |
| 3 | University & Academic Structure | ✅ Done |
| 4 | Course & Section Management | ✅ Done |
| 5 | Student Profiles & Enrollment | ✅ Done |
| 6 | Assessment & Question Bank | ✅ Done |
| 7 | AI Quiz Generation (Groq / Llama 3) + Material Library | ✅ Done |
| 8 | Student Attempt & Auto Grading | ✅ Done |
| 9 | Results & Analytics | ✅ Done |
| 10 | Notifications & Reports | 🔜 Next |
| 11 | Docker & Production Deploy | 🔜 Planned |

---

## License

Proprietary — All rights reserved.
