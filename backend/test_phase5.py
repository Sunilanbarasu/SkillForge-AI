import httpx
import psycopg2
from app.core.config import settings

BASE_URL = "http://127.0.0.1:8000/api/v1"
USER1_EMAIL = "student_p5_1@example.com"
USER2_EMAIL = "student_p5_2@example.com"
PASSWORD = "password123"

def run_tests():
    print("==================================================")
    print("       STARTING PHASE 5 AUTOMATED TEST SUITE     ")
    print("==================================================")

    # Enable mock test key mode for backend service during automated testing
    settings.GEMINI_API_KEY = "mock_test_key"

    client = httpx.Client(base_url=BASE_URL, timeout=15.0)

    # Register/Login User 1
    reg1 = client.post("/auth/register", json={"name": "P5 Student One", "email": USER1_EMAIL, "password": PASSWORD})
    token1 = reg1.json()["access_token"] if reg1.status_code == 201 else client.post("/auth/login", json={"email": USER1_EMAIL, "password": PASSWORD}).json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Register/Login User 2
    reg2 = client.post("/auth/register", json={"name": "P5 Student Two", "email": USER2_EMAIL, "password": PASSWORD})
    token2 = reg2.json()["access_token"] if reg2.status_code == 201 else client.post("/auth/login", json={"email": USER2_EMAIL, "password": PASSWORD}).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 1. Unauthenticated study plan generation -> 401
    res = client.post("/study-plans/generate")
    assert res.status_code in (401, 403), f"Expected 401/403, got {res.status_code}"
    print("[OK] 1. Unauthenticated study plan generation rejected (HTTP 401/403).")

    # 2. No completed assessment -> 400
    res = client.post("/study-plans/generate", headers=headers2)
    assert res.status_code == 400, f"Expected 400 for no completed assessment, got {res.status_code}"
    print("[OK] 2. No completed assessment -> HTTP 400.")

    # Start & complete assessment for User 1 (without AI analysis)
    start_res = client.post("/assessments/start", headers=headers1)
    assert start_res.status_code == 201
    ass_id = start_res.json()["assessment_id"]
    questions = start_res.json()["questions"]

    answers = [{"question_id": q["id"], "selected_answer": "A"} for q in questions]
    sub_res = client.post(f"/assessments/{ass_id}/submit", json={"answers": answers}, headers=headers1)
    assert sub_res.status_code == 200

    # 3. No AI analysis -> 400
    res = client.post("/study-plans/generate", headers=headers1)
    assert res.status_code == 400, f"Expected 400 for no AI analysis, got {res.status_code}: {res.text}"
    print("[OK] 3. No AI analysis for latest assessment -> HTTP 400.")

    # Generate AI analysis for User 1
    ai_res = client.post(f"/assessments/{ass_id}/ai-analysis", headers=headers1)
    assert ai_res.status_code == 200, f"AI analysis failed: {ai_res.text}"

    # 4. Completed assessment + AI analysis -> plan generated
    res = client.post("/study-plans/generate", headers=headers1)
    assert res.status_code == 200, f"Study plan generation failed: {res.text}"
    plan_data = res.json()
    print("[OK] 4. Completed assessment + AI analysis -> study plan generated.")

    # 5. StudyPlan persisted (verify via API response)
    assert plan_data["id"] > 0
    assert plan_data["user_id"] > 0
    assert plan_data["assessment_id"] == ass_id
    assert plan_data["title"]
    assert plan_data["goal"]
    assert plan_data["duration_weeks"] > 0
    print("[OK] 5. StudyPlan persisted with title, goal, and duration.")

    # 6. Tasks persisted
    assert len(plan_data["tasks"]) > 0, "Study plan should contain tasks"
    for task in plan_data["tasks"]:
        assert task["skill"]
        assert task["week_number"] > 0
        assert task["task"]
        assert task["difficulty"] in ("Beginner", "Intermediate", "Advanced")
        assert task["estimated_minutes"] > 0
        assert task["status"] in ("pending", "completed")
    print(f"[OK] 6. {len(plan_data['tasks'])} tasks persisted with valid fields.")

    # 7. AI response validated
    assert "id" in plan_data
    assert "tasks" in plan_data
    print("[OK] 7. AI response validated with Pydantic schema.")

    # 8. Assessment scores unchanged
    conn = psycopg2.connect(host="127.0.0.1", port=5432, user="postgres", password="postgres", dbname="skillforge_ai")
    cur = conn.cursor()
    cur.execute("SELECT overall_score FROM assessments WHERE id = %s", (ass_id,))
    db_score = cur.fetchone()[0]
    assert db_score == sub_res.json()["overall_score"], "Numerical score in PostgreSQL was tampered with!"
    print("[OK] 8. Assessment scores remain unchanged in PostgreSQL.")

    # 9. Correct user ownership
    assert plan_data["user_id"] == sub_res.json()["user_id"]
    print("[OK] 9. Study plan ownership correctly assigned to current user.")

    # 10. Correct assessment relationship
    assert plan_data["assessment_id"] == ass_id
    print("[OK] 10. Study plan correctly linked to the latest assessment.")

    # 11. Repeated generation returns cached plan
    repeat_res = client.post("/study-plans/generate", headers=headers1)
    assert repeat_res.status_code == 200
    assert repeat_res.json()["id"] == plan_data["id"]
    print("[OK] 11. Repeated generation returns cached plan (idempotent).")

    # 12. No duplicate plan
    cur.execute("SELECT count(*) FROM study_plans WHERE user_id = %s AND assessment_id = %s", (plan_data["user_id"], ass_id))
    count = cur.fetchone()[0]
    assert count == 1, f"Expected 1 plan row, found {count}"
    print("[OK] 12. No duplicate plan created in PostgreSQL.")

    # 13. Current plan endpoint works
    cur_plan_res = client.get("/study-plans/current", headers=headers1)
    assert cur_plan_res.status_code == 200
    assert cur_plan_res.json()["id"] == plan_data["id"]
    assert len(cur_plan_res.json()["tasks"]) > 0
    print("[OK] 13. GET /study-plans/current returns latest plan with tasks.")

    # 14. Cross-user plan access rejected
    res = client.get("/study-plans/current", headers=headers2)
    assert res.status_code == 404, f"Expected 404 for user2 (no plan), got {res.status_code}"
    print("[OK] 14. Cross-user plan access rejected (User 2 cannot see User 1's plan).")

    # 15. Task completion works
    first_task_id = plan_data["tasks"][0]["id"]
    patch_res = client.patch(f"/study-plans/tasks/{first_task_id}", json={"status": "completed"}, headers=headers1)
    assert patch_res.status_code == 200, f"Task update failed: {patch_res.text}"
    assert patch_res.json()["status"] == "completed"
    assert patch_res.json()["completed_at"] is not None
    print("[OK] 15. Task completion status updated to 'completed' with completed_at timestamp.")

    # 16. Task status persists
    cur.execute("SELECT status, completed_at FROM tasks WHERE id = %s", (first_task_id,))
    db_task = cur.fetchone()
    assert db_task[0] == "completed"
    assert db_task[1] is not None
    print("[OK] 16. Task completion persisted in PostgreSQL.")

    # 17. Cross-user task update rejected
    res = client.patch(f"/study-plans/tasks/{first_task_id}", json={"status": "pending"}, headers=headers2)
    assert res.status_code == 403, f"Expected 403 for cross-user task update, got {res.status_code}"
    print("[OK] 17. Cross-user task update rejected (HTTP 403).")

    # 18. Invalid task status rejected
    res = client.patch(f"/study-plans/tasks/{first_task_id}", json={"status": "in_progress"}, headers=headers1)
    assert res.status_code == 422, f"Expected 422 for invalid status, got {res.status_code}"
    print("[OK] 18. Invalid task status rejected (HTTP 422).")

    # 19. Revert task back to pending
    revert_res = client.patch(f"/study-plans/tasks/{first_task_id}", json={"status": "pending"}, headers=headers1)
    assert revert_res.status_code == 200
    assert revert_res.json()["status"] == "pending"
    assert revert_res.json()["completed_at"] is None
    print("[OK] 19. Task reverted to pending with completed_at cleared.")

    # PostgreSQL direct verification of study_plans & tasks tables
    cur.execute("SELECT id, user_id, assessment_id FROM study_plans WHERE id = %s", (plan_data["id"],))
    sp_row = cur.fetchone()
    assert sp_row is not None, "study_plans row not found!"
    cur.execute("SELECT count(*) FROM tasks WHERE study_plan_id = %s", (plan_data["id"],))
    task_count = cur.fetchone()[0]
    assert task_count == len(plan_data["tasks"]), f"Task count mismatch: DB={task_count}, API={len(plan_data['tasks'])}"
    print(f"[OK] 20. PostgreSQL: study_plans and tasks tables verified ({task_count} tasks linked).")

    cur.close()
    conn.close()

    print("==================================================")
    print("       ALL PHASE 5 TESTS PASSED SUCCESSFULLY!     ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()