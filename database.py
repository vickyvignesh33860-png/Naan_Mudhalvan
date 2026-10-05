import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edugenie.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Interactions Table: logs all module requests and answers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module TEXT NOT NULL,
            input_text TEXT NOT NULL,
            output_text TEXT NOT NULL,
            model_used TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Quiz Scores Table: records quiz evaluations taken by users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Settings Table: stores runtime configurations (e.g. custom Gemini API keys)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def log_interaction(module: str, input_text: str, output_text: str, model_used: str = "Gemini 1.5 Pro"):
    """Logs an educational query and generated response into the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO interactions (module, input_text, output_text, model_used, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (module, str(input_text), str(output_text), model_used, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB Warning] Could not log interaction: {e}")

def log_quiz_score(topic: str, score: int, total: int):
    """Records user performance on generated quizzes."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_scores (topic, score, total, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (str(topic), int(score), int(total), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB Warning] Could not log quiz score: {e}")

def get_recent_interactions(limit: int = 100, module: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves interaction records for the Admin Dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    if module:
        cursor.execute(
            "SELECT * FROM interactions WHERE module = ? ORDER BY id DESC LIMIT ?",
            (module, limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM interactions ORDER BY id DESC LIMIT ?",
            (limit,)
        )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_quiz_scores(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves recent quiz scores for the Admin Dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_scores ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_interaction_stats() -> Dict[str, Any]:
    """Computes summary statistics for the Admin Dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM interactions")
    total_interactions = cursor.fetchone()[0]
    
    cursor.execute("SELECT module, COUNT(*) as count FROM interactions GROUP BY module")
    module_breakdown = {row["module"]: row["count"] for row in cursor.fetchall()}
    
    cursor.execute("SELECT COUNT(*) FROM quiz_scores")
    total_quizzes_taken = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(score * 100.0 / total) FROM quiz_scores WHERE total > 0")
    avg_score_row = cursor.fetchone()[0]
    avg_quiz_score = round(avg_score_row, 1) if avg_score_row is not None else 0.0
    
    db_size_bytes = os.path.getsize(DB_FILE) if os.path.exists(DB_FILE) else 0
    db_size_kb = round(db_size_bytes / 1024, 2)
    
    conn.close()
    return {
        "total_interactions": total_interactions,
        "module_breakdown": module_breakdown,
        "total_quizzes_taken": total_quizzes_taken,
        "avg_quiz_score": avg_quiz_score,
        "db_size_kb": db_size_kb,
        "db_path": DB_FILE
    }

def clear_all_logs():
    """Wipes all interaction and quiz records from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM interactions")
    cursor.execute("DELETE FROM quiz_scores")
    conn.commit()
    conn.close()

def set_db_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO settings (key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        """,
        (key, value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_db_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

# Initialize database on import
init_db()
