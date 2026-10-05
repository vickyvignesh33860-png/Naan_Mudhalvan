import os
from fastapi import FastAPI, Request, Query, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Import module logic
from qna import answer_question_with_gemini
from explanation_module import explain_topic
from summary_module import summarize_text
from quiz_module import generate_quiz
from learning_path import get_learning_recommendations
from database import (
    init_db,
    log_quiz_score,
    get_recent_interactions,
    get_quiz_scores,
    get_interaction_stats,
    clear_all_logs,
    set_db_setting,
    get_db_setting
)
from ai_config import is_api_configured, get_api_key

load_dotenv()

# Initialize FastAPI App
app = FastAPI(
    title="EduGenie: Google Gemini Powered Learning Assistant",
    description="Lightweight AI-powered educational assistant built with FastAPI",
    version="1.0.0"
)

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount Static Files and Templates
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Admin Auth Helper
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def verify_admin_token(authorization: str = Header(None)):
    """Simple admin verification header for API protection."""
    if not authorization or authorization != f"Bearer {ADMIN_PASSWORD}":
        raise HTTPException(status_code=401, detail="Unauthorized admin access")
    return True

# ---------------------------------------------------------
# Core Student Web Page
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Renders the EduGenie Student Interface as shown in the project documentation."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"api_configured": is_api_configured()}
    )

# ---------------------------------------------------------
# Core API Endpoints (as defined in documentation)
# ---------------------------------------------------------

# 1. Q&A - GET API using Gemini
@app.get("/qa")
async def answer_question(question: str = Query(...)):
    answer = answer_question_with_gemini(question)
    return {"answer": answer}

# 2. Explanation - POST API
@app.post("/explain")
async def explain_api(request: Request):
    data = await request.json()
    topic = data.get("topic")
    if not topic:
        return JSONResponse(content={"error": "Please provide a topic."}, status_code=400)
    explanation = explain_topic(topic)
    return {"topic": topic, "explanation": explanation}

# 3. Summarization - POST API
@app.post("/summarize")
async def summarize_api(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        return JSONResponse(content={"error": "Please provide text to summarize."}, status_code=400)
    summary = summarize_text(text)
    return {"summary": summary}

# 4. Quiz Generation - POST API
@app.post("/quiz")
async def quiz_api(request: Request):
    data = await request.json()
    text = data.get("text")
    count = data.get("count", 3)
    if not text:
        return JSONResponse(content={"error": "Please provide text for quiz."}, status_code=400)
    quiz = generate_quiz(text, count=count)
    return JSONResponse(content={"quiz": quiz})

# 5. Learning Recommendations - GET API
@app.get("/learn/recommendations")
async def learning_recommendation_api(topic: str = Query(...)):
    recommendation = get_learning_recommendations(topic)
    return {"topic": topic, "recommendation": recommendation}

# ---------------------------------------------------------
# Quiz Score Submission (Record student performance in SQLite)
# ---------------------------------------------------------
@app.post("/api/quiz/record")
async def record_quiz_score(request: Request):
    data = await request.json()
    topic = data.get("topic", "General Quiz")
    score = int(data.get("score", 0))
    total = int(data.get("total", 0))
    log_quiz_score(topic, score, total)
    return {"status": "success", "recorded": {"topic": topic, "score": score, "total": total}}

# ---------------------------------------------------------
# Admin Web Portal (Exclusive Database Visibility)
# ---------------------------------------------------------
@app.get("/admin", response_class=HTMLResponse)
async def admin_portal(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"api_configured": is_api_configured()}
    )

@app.post("/api/admin/auth")
async def admin_auth(request: Request):
    """Authenticates admin credentials."""
    data = await request.json()
    password = data.get("password")
    if password == ADMIN_PASSWORD:
        return {"authenticated": True, "token": ADMIN_PASSWORD}
    return JSONResponse(content={"authenticated": False, "error": "Invalid admin password."}, status_code=401)

@app.get("/api/admin/interactions")
async def admin_interactions(
    limit: int = 100,
    module: str = None,
    authenticated: bool = Depends(verify_admin_token)
):
    """Fetches logged user interactions exclusively for the Admin Web."""
    logs = get_recent_interactions(limit=limit, module=module)
    return {"interactions": logs}

@app.get("/api/admin/stats")
async def admin_stats(authenticated: bool = Depends(verify_admin_token)):
    """Fetches system metrics and SQLite statistics for Admin Web."""
    stats = get_interaction_stats()
    stats["api_configured"] = is_api_configured()
    stats["quiz_scores"] = get_quiz_scores(limit=10)
    return stats

@app.post("/api/admin/clear-logs")
async def admin_clear(authenticated: bool = Depends(verify_admin_token)):
    """Clears interaction records from SQLite database."""
    clear_all_logs()
    return {"status": "success", "message": "All database logs cleared."}

@app.post("/api/admin/set-api-key")
async def admin_set_key(request: Request, authenticated: bool = Depends(verify_admin_token)):
    """Dynamically updates the Gemini API key from the Admin Web Dashboard."""
    data = await request.json()
    new_key = data.get("api_key", "").strip()
    if not new_key:
        return JSONResponse(content={"error": "API key cannot be empty"}, status_code=400)
    set_db_setting("GEMINI_API_KEY", new_key)
    return {"status": "success", "message": "Gemini API key updated successfully."}

@app.get("/api/health")
async def health_check():
    """Health status endpoint."""
    return {
        "status": "healthy",
        "app": "EduGenie",
        "api_configured": is_api_configured()
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"Starting EduGenie server at http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
