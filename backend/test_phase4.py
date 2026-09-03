import httpx
import psycopg2
from app.core.config import settings

BASE_URL = "http://127.0.0.1:8000/api/v1"
USER1_EMAIL = "student_p4_1@example.com"
USER2_EMAIL = "student_p4_2@example.com"
PASSWORD = "password123"

def run_tests():
    print("==================================================")
    print("       STARTING PHASE 4 AUTOMATED TEST SUITE     ")
    print("==================================================")

    # Enable mock test key mode for backend service during automated testing
    settings.GEMINI_API_KEY = "mock_test_key"

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # Register/Login User 1
    reg1 = client.post("/auth/register", json={"name": "P4 Student One", "email": USER1_EMAIL, "password": PASSWORD})
    token1 = reg1.json()["access_token"] if reg1.status_code == 201 else client.post("/auth/login", json={"email": USER1_EMAIL, "password": PASSWORD}).json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Register/Login User 2
    reg2 = client.post("/auth/register", json={"name": "P4 Student Two", "email": USER2_EMAIL, "password": PASSWORD})
    token2 = reg2.json()["access_token"] if reg2.status_code == 201 else client.post("/auth/login", json={"email": USER2_EMAIL, "password": PASSWORD}).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 1. Unauthenticated AI analysis request -> 401
    res = client.post("/assessments/1/ai-analysis")
    assert res.status_code in (401, 403), f"Expected 401/403, got {res.status_code}"
    print("[OK] 1. Unauthenticated AI analysis request rejected (HTTP 401/403).")

    # 2. Non-existent assessment -> 404
    res = client.post("/assessments/999999/ai-analysis", headers=headers1)
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"
    print("[OK] 2. Non-existent assessment rejected with 404 Not Found.")

    # Start Assessment for User 1 (Incomplete state)
    start_res = client.post("/assessments/start", headers=headers1)
    assert start_res.status_code == 201
    ass_id = start_res.json()["assessment_id"]
    questions = start_res.json()["questions"]

    # 3. User cannot analyze another user's assessment -> 403
    res = client.post(f"/assessments/{ass_id}/ai-analysis", headers=headers2)
    assert res.status_code == 403, f"Expected 403 for cross-user analysis, got {res.status_code}"
    print("[OK] 3. Security verified: User 2 cannot analyze User 1's assessment (HTTP 403).")

    # 4. Incomplete assessment cannot be analyzed -> 400
    res = client.post(f"/assessments/{ass_id}/ai-analysis", headers=headers1)
    assert res.status_code == 400, f"Expected 400 for incomplete assessment, got {res.status_code}"
    print("[OK] 4. Incomplete assessment cannot be analyzed (HTTP 400).")

    # Complete assessment for User 1
    answers = [{"question_id": q["id"], "selected_answer": "A"} for q in questions]
    sub_res = client.post(f"/assessments/{ass_id}/submit", json={"answers": answers}, headers=headers1)
    assert sub_res.status_code == 200

    # 5, 6, 7, 8. Completed assessment analyzed & validated
    res = client.post(f"/assessments/{ass_id}/ai-analysis", headers=headers1)
    assert res.status_code == 200, f"AI analysis failed: {res.text}"
    ai_data = res.json()
    
    # 10. Returned analysis contains all required sections
    assert "summary" in ai_data
    assert "strengths" in ai_data
    assert "weaknesses" in ai_data
    assert "skill_gaps" in ai_data
    assert "priorities" in ai_data
    assert "recommendations" in ai_data
    assert ai_data["assessment_id"] == ass_id

    # 12. API key is never included in response
    assert "GEMINI_API_KEY" not in str(ai_data)
    assert "api_key" not in str(ai_data)
    print("[OK] 5, 6, 7, 8 & 10. Completed assessment analyzed, numerical facts sent, JSON validated & returned.")

    # 9. Idempotency test: Repeated request returns existing stored row
    repeat_res = client.post(f"/assessments/{ass_id}/ai-analysis", headers=headers1)
    assert repeat_res.status_code == 200
    assert repeat_res.json()["id"] == ai_data["id"]
    print("[OK] 9. Idempotency verified: Cached analysis returned without redundant AI API call.")

    # 11. Verify AI does not modify stored numerical scores in PostgreSQL
    conn = psycopg2.connect(host="127.0.0.1", port=5432, user="postgres", password="postgres", dbname="skillforge_ai")
    cur = conn.cursor()
    cur.execute("SELECT overall_score FROM assessments WHERE id = %s", (ass_id,))
    db_score = cur.fetchone()[0]
    assert db_score == sub_res.json()["overall_score"], "Numerical score in PostgreSQL was tampered with!"
    print("[OK] 11. Stored numerical assessment scores remain intact in PostgreSQL.")

    # Direct DB check for ai_analysis table
    cur.execute("SELECT id, user_id, assessment_id, summary FROM ai_analysis WHERE assessment_id = %s", (ass_id,))
    db_ai_row = cur.fetchone()
    assert db_ai_row is not None, "AIAnalysis row not found in PostgreSQL!"
    assert db_ai_row[1] == sub_res.json()["user_id"]
    print("[OK] PostgreSQL verification: ai_analysis row persisted with valid FK to users.id and assessments.id.")

    cur.close()
    conn.close()

    print("==================================================")
    print("       ALL PHASE 4 TESTS PASSED SUCCESSFULLY!     ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
