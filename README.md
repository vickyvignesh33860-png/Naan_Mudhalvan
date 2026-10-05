# 🎓 EduGenie: Google Gemini Powered Learning Assistant

EduGenie is a lightweight AI-powered educational assistant built with **FastAPI**, **HTML/CSS**, and **Generative AI** (Google Gemini & LaMini-Flan-T5). It is designed to assist learners across all academic levels by simplifying complex concepts, answering academic questions, creating interactive quizzes with custom question counts and real-time grading, summarizing passages, and designing structured learning paths.

EduGenie includes an **exclusive Admin Web Portal** where SQLite database interactions, logs, and quiz scores are strictly protected and visible only to administrators.

---

## 📂 Project Architecture

The codebase directly follows the project specification and folder architecture:

```text
EduGenie/
├── main.py                  # FastAPI application with REST endpoints & template routes
├── explanation_module.py    # Concept explanation logic (LaMini-Flan-T5-783M + Gemini fallback)
├── qna.py                   # Question answering with Gemini 1.5 Pro
├── quiz_module.py           # 3-question MCQ generator with JSON parsing & sanitization
├── summary_module.py        # Educational passage summarization module
├── learning_path.py         # Structured, adaptive learning recommendations
├── database.py              # SQLite database manager for interaction logs & quiz scores
├── ai_config.py             # Centralized Gemini AI configuration & API key management
├── test_app.py              # Complete automated test suite
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (Gemini API key, Admin password)
├── .env.example             # Example environment file template
├── static/
│   └── style.css            # Responsive CSS styling matching project documentation
└── templates/
    ├── index.html           # Student Web Interface (matching PDF documentation)
    └── admin.html           # Admin Web Portal (Exclusive database records & analytics)
```

---

## 🚀 Quick Setup & Installation in VS Code

### 1. Open Project in VS Code
Open VS Code, click **File > Open Folder...**, and select the project directory:
```
c:\Users\p\OneDrive\Desktop\Naan_Mudhalvan
```

### 2. Open Terminal in VS Code
Press ``Ctrl + ` `` (backtick) or select **Terminal > New Terminal** in the top menu.

### 3. (Optional) Create and Activate Virtual Environment
```bash
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows Command Prompt (cmd):
venv\Scripts\activate.bat
```

### 4. Install Dependencies
Install all required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## 🔑 Configuration (.env)

Open the `.env` file in the root directory. You can optionally add your free Google Gemini API key:

```env
# Google Gemini API Key (Get free from https://aistudio.google.com/)
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Default Model
GEMINI_MODEL=models/gemini-3.1-flash-lite

# Admin Web Portal Password
ADMIN_PASSWORD=admin123

# Server Settings
HOST=127.0.0.1
PORT=8000
```

> **Note:** EduGenie includes an offline demonstration mode and automatic fallback. Even without an API key, all UI elements, quiz checking, forms, database logging, and admin portals work out of the box. You can also set or change the Gemini API key anytime directly inside the **Admin Web Portal**!

---

## 💻 Running the Application

Start the FastAPI application with Uvicorn using either command:

```bash
python -m uvicorn main:app --reload
```
*Alternatively, you can run directly:*
```bash
python main.py
```

Once started, the server will output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 🌐 Web Interfaces & Features

### 1. Student Web Interface
Navigate to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

The student interface reproduces the exact layout and features from the documentation:
* **Ask EduGenie a Question (`GET /qa`)**:
  - Input: *"Which is the largest ocean?"* or *"Why is the sky blue?"*
  - Output: Instant, accurate answer formatted in a clean response card.
* **Need an Explanation? (`POST /explain`)**:
  - Input: *"Photosynthesis"* or *"Quantum computing"*
  - Output: School-student-friendly simplified breakdown using LaMini-Flan-T5 / Gemini.
* **Summarize a Paragraph (`POST /summarize`)**:
  - Input: Paste lengthy paragraphs or study material.
  - Output: Concise summary preserving key takeaways and eliminating redundancy.
* **Generate a Quiz (`POST /quiz`)**:
  - Input: Topic or concept name like *"Solar System"* or *"The Pythagoras Theorem"*.
  - Output: Generates 3 MCQs with 4 options each.
  - **Interactive Verification**: Click *Check Answer* on any question to instantly see `✅ Correct!` or `❌ Incorrect. Correct answer: ...`.
  - **Auto-Grading**: When all questions are attempted, your final score is calculated and securely stored in the SQLite database.
* **Get Learning Recommendations (`GET /learn/recommendations`)**:
  - Input: Any domain or skill like *"SQL"* or *"Machine Learning"*.
  - Output: Step-by-step roadmap across Beginner, Intermediate, and Advanced stages, with suggested timelines, books, and courses.

---

### 2. Admin Web Portal (Exclusive Database Visibility)
Navigate to: **[http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)**

As specified in the requirements, **the database is strictly visible only to administrators**:
* **Authentication**: Protected by admin password (default: `admin123`).
* **Live Database Records (`interactions` table)**:
  - Inspect all historical student queries and AI-generated outputs.
  - Filter by module (`/qa`, `/explain`, `/summarize`, `/quiz`, `/learn/recommendations`).
  - Search by keyword across questions and answers.
  - Model engine identification (`Gemini 1.5 Pro`, `LaMini-Flan-T5-783M`, etc.).
* **Quiz Performance Logs (`quiz_scores` table)**:
  - View students' quiz attempts, topic names, scores, and percentage grades.
* **Real-time Analytics**:
  - Total queries served, total quizzes taken, average score %, database size (KB).
* **Dynamic API Key Manager**:
  - Update or test the Google Gemini API key without restarting the server.
* **Database Maintenance**:
  - One-click database log clearing.

---

## 🧪 Automated Testing

To run the complete automated test suite verifying all 9 core features, REST APIs, and database security:

```bash
python test_app.py
```

Expected output:
```text
==================================================
       Running EduGenie Complete Test Suite       
==================================================

[Test 1] Testing Student Web Interface (GET /)...
  -> PASSED: Student UI rendered correctly.

[Test 2] Testing Q&A Endpoint (GET /qa)...
  -> PASSED: Q&A Response received...

[Test 3] Testing Concept Explanation Endpoint (POST /explain)...
  -> PASSED: Explanation received...

[Test 4] Testing Summarization Endpoint (POST /summarize)...
  -> PASSED: Summary received...

[Test 5] Testing Quiz Generation Endpoint (POST /quiz)...
  -> PASSED: Generated 3 MCQs successfully.

[Test 6] Testing Learning Recommendations (GET /learn/recommendations)...
  -> PASSED: Learning path received for topic: SQL

[Test 7] Testing Quiz Score Recording (POST /api/quiz/record)...
  -> PASSED: Student quiz score recorded in database.

[Test 8] Testing Admin Portal Web Interface (GET /admin)...
  -> PASSED: Admin UI rendered correctly.

[Test 9] Testing Admin Auth & Protected Database APIs...
  -> PASSED: Database is strictly hidden from unauthorized users.
  -> PASSED: Admin retrieved records from SQLite database.
  -> PASSED: SQLite Database Stats verified.

==================================================
     ALL 9 TESTS PASSED COMPLETELY & FLAWLESSLY!    
==================================================
```

---

## 🛠️ API Reference Summary

| Endpoint | Method | Input | Description |
|---|---|---|---|
| `/` | `GET` | None | Renders Student Web Application |
| `/qa` | `GET` | `question=...` (query param) | Academic and General Q&A with Gemini |
| `/explain` | `POST` | `{"topic": "..."}` (JSON) | School-level concept explanation |
| `/summarize` | `POST` | `{"text": "..."}` (JSON) | Summarizes text into concise bullet points |
| `/quiz` | `POST` | `{"text": "..."}` (JSON) | Generates 3 MCQs with 4 options |
| `/learn/recommendations` | `GET` | `topic=...` (query param) | Structured learning roadmap |
| `/api/quiz/record` | `POST` | `{"topic", "score", "total"}` | Saves quiz score into SQLite |
| `/admin` | `GET` | None | Admin Web Portal |
| `/api/admin/auth` | `POST` | `{"password": "..."}` | Admin password verification |
| `/api/admin/interactions` | `GET` | `limit`, `module` (Bearer Token) | Retrieves database records |
| `/api/admin/stats` | `GET` | Bearer Token | Retrieves system & database metrics |
| `/api/admin/set-api-key` | `POST` | `{"api_key": "..."}` | Updates Gemini API key dynamically |
| `/api/admin/clear-logs` | `POST` | Bearer Token | Clears SQLite database tables |
