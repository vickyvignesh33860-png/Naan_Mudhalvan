import sys
import io
# Ensure UTF-8 output on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient
from main import app
import database

def run_tests():
    print("==================================================")
    print("       Running EduGenie Complete Test Suite       ")
    print("==================================================")
    client = TestClient(app)

    # 1. Test Home Web Page (GET /)
    print("\n[Test 1] Testing Student Web Interface (GET /)...")
    res = client.get("/")
    assert "Welcome to EduGenie" in res.text
    print("  -> PASSED: Student UI rendered correctly.")

    # 2. Test Q&A Endpoint (GET /qa)
    print("\n[Test 2] Testing Q&A Endpoint (GET /qa)...")
    res = client.get("/qa?question=What is the speed of light?")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert "answer" in data and len(data["answer"]) > 0
    print(f"  -> PASSED: Q&A Response received: {data['answer'][:60]}...")

    # 3. Test Explanation Endpoint (POST /explain)
    print("\n[Test 3] Testing Concept Explanation Endpoint (POST /explain)...")
    res = client.post("/explain", json={"topic": "Gravity"})
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert "explanation" in data and len(data["explanation"]) > 0
    print(f"  -> PASSED: Explanation received: {data['explanation'][:60]}...")

    # 4. Test Summarization Endpoint (POST /summarize)
    print("\n[Test 4] Testing Summarization Endpoint (POST /summarize)...")
    sample_text = (
        "The Industrial Revolution marked a period of development in the latter half of the 18th century "
        "that transformed largely rural, agrarian societies in Europe and America into industrialized, urban ones."
    )
    res = client.post("/summarize", json={"text": sample_text})
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert "summary" in data and len(data["summary"]) > 0
    print(f"  -> PASSED: Summary received: {data['summary'][:60]}...")

    # 5. Test Quiz Generation Endpoint (POST /quiz)
    print("\n[Test 5] Testing Quiz Generation Endpoint (POST /quiz)...")
    res = client.post("/quiz", json={"text": "Solar System"})
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert "quiz" in data and isinstance(data["quiz"], list)
    assert len(data["quiz"]) > 0
    first_q = data["quiz"][0]
    assert "question" in first_q and "options" in first_q and "answer" in first_q
    print(f"  -> PASSED: Generated {len(data['quiz'])} MCQs successfully.")

    # 6. Test Learning Recommendations Endpoint (GET /learn/recommendations)
    print("\n[Test 6] Testing Learning Recommendations (GET /learn/recommendations)...")
    res = client.get("/learn/recommendations?topic=SQL")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert "recommendation" in data and len(data["recommendation"]) > 0
    print(f"  -> PASSED: Learning path received for topic: {data['topic']}")

    # 7. Test Student Quiz Score Logging (POST /api/quiz/record)
    print("\n[Test 7] Testing Quiz Score Recording (POST /api/quiz/record)...")
    res = client.post("/api/quiz/record", json={"topic": "Solar System", "score": 3, "total": 3})
    assert res.status_code == 200
    print("  -> PASSED: Student quiz score recorded in database.")

    # 8. Test Admin Portal Page (GET /admin)
    print("\n[Test 8] Testing Admin Portal Web Interface (GET /admin)...")
    res = client.get("/admin")
    assert res.status_code == 200
    assert "Admin Database Portal" in res.text
    print("  -> PASSED: Admin UI rendered correctly.")

    # 9. Test Admin Authentication & Protected Database APIs
    print("\n[Test 9] Testing Admin Auth & Protected Database APIs...")
    # Unauthorized attempt
    unauth_res = client.get("/api/admin/interactions")
    assert unauth_res.status_code == 401, "Expected 401 for unauthorized access"
    print("  -> PASSED: Database is strictly hidden from unauthorized users.")

    # Authorized login
    auth_res = client.post("/api/admin/auth", json={"password": "admin123"})
    assert auth_res.status_code == 200
    token = auth_res.json()["token"]

    # Authorized interactions fetch
    inter_res = client.get("/api/admin/interactions", headers={"Authorization": f"Bearer {token}"})
    assert inter_res.status_code == 200
    interactions = inter_res.json()["interactions"]
    assert len(interactions) > 0, "Expected logged interactions in SQLite"
    print(f"  -> PASSED: Admin retrieved {len(interactions)} records from SQLite database.")

    # Authorized stats fetch
    stats_res = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_interactions"] >= len(interactions)
    print(f"  -> PASSED: SQLite Database Stats: Total Interactions={stats['total_interactions']}, Size={stats['db_size_kb']} KB")

    print("\n==================================================")
    print("     ALL 9 TESTS PASSED COMPLETELY & FLAWLESSLY!    ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
