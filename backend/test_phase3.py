import httpx
import psycopg2

BASE_URL = "http://127.0.0.1:8000/api/v1"
USER1_EMAIL = "student_p3_1@example.com"
USER2_EMAIL = "student_p3_2@example.com"
PASSWORD = "password123"

def run_tests():
    print("==================================================")
    print("       STARTING PHASE 3 AUTOMATED TEST SUITE     ")
    print("==================================================")

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # Register/Login User 1
    reg1 = client.post("/auth/register", json={"name": "Student One", "email": USER1_EMAIL, "password": PASSWORD})
    token1 = reg1.json()["access_token"] if reg1.status_code == 201 else client.post("/auth/login", json={"email": USER1_EMAIL, "password": PASSWORD}).json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Register/Login User 2
    reg2 = client.post("/auth/register", json={"name": "Student Two", "email": USER2_EMAIL, "password": PASSWORD})
    token2 = reg2.json()["access_token"] if reg2.status_code == 201 else client.post("/auth/login", json={"email": USER2_EMAIL, "password": PASSWORD}).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 1. Unauthenticated user cannot start assessment
    res = client.post("/assessments/start")
    assert res.status_code in (401, 403), f"Expected 401/403 unauthenticated start, got {res.status_code}"
    print("[OK] 1. Unauthenticated user cannot start assessment (HTTP 401/403).")

    # 2. Authenticated user can start assessment
    res = client.post("/assessments/start", headers=headers1)
    assert res.status_code == 201, f"Failed to start assessment: {res.text}"
    start_data = res.json()
    assert "assessment_id" in start_data, "assessment_id missing"
    assert "questions" in start_data, "questions missing"
    ass_id = start_data["assessment_id"]
    questions = start_data["questions"]
    assert len(questions) == 35, f"Expected 35 questions, got {len(questions)}"
    print(f"[OK] 2. Authenticated user started assessment #{ass_id} with {len(questions)} questions.")

    # 3. Questions are returned WITHOUT correct answers
    for q in questions:
        assert "correct_answer" not in q, f"SECURITY FAILURE: correct_answer exposed in question {q['id']}!"
        assert "option_a" in q and "option_b" in q and "option_c" in q and "option_d" in q
    print("[OK] 3. Security verified: correct_answer is NEVER exposed in start response.")

    # 4. Assessment is persisted in PostgreSQL
    conn = psycopg2.connect(host="127.0.0.1", port=5432, user="postgres", password="postgres", dbname="skillforge_ai")
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, total_questions FROM assessments WHERE id = %s", (ass_id,))
    db_ass = cur.fetchone()
    assert db_ass is not None, "Assessment not found in PostgreSQL!"
    print("[OK] 4. Assessment persisted in PostgreSQL database.")

    # Fetch actual correct answers directly from PostgreSQL for controlled scoring verification
    cur.execute("SELECT id, skill, correct_answer FROM questions ORDER BY id ASC")
    q_db_rows = cur.fetchall()
    q_correct_map = {row[0]: (row[1], row[2]) for row in q_db_rows}

    # Prepare answers submission: 30 correct, 5 incorrect
    answers_to_submit = []
    expected_correct = 0
    expected_skill_stats = {}

    for idx, q in enumerate(questions):
        q_id = q["id"]
        skill, correct_ans = q_correct_map[q_id]
        if skill not in expected_skill_stats:
            expected_skill_stats[skill] = {"total": 0, "correct": 0}
        expected_skill_stats[skill]["total"] += 1

        # Intentionally answer the first 30 correctly, last 5 incorrectly
        if idx < 30:
            user_choice = correct_ans
            expected_correct += 1
            expected_skill_stats[skill]["correct"] += 1
        else:
            user_choice = "A" if correct_ans != "A" else "B"

        answers_to_submit.append({
            "question_id": q_id,
            "selected_answer": user_choice
        })

    # 5. Submit valid answers
    res = client.post(f"/assessments/{ass_id}/submit", json={"answers": answers_to_submit}, headers=headers1)
    assert res.status_code == 200, f"Submit assessment failed: {res.text}"
    result_data = res.json()
    print("[OK] 5. Valid answers accepted by submit endpoint.")

    # 6 & 7. Overall score calculated correctly
    expected_overall = round((expected_correct / 35.0) * 100.0, 2)
    assert result_data["total_correct"] == expected_correct, f"Expected {expected_correct} correct, got {result_data['total_correct']}"
    assert abs(result_data["overall_score"] - expected_overall) < 0.01, f"Expected {expected_overall}%, got {result_data['overall_score']}%"
    print(f"[OK] 6 & 7. Correct answers scored correctly: {expected_correct}/35 ({result_data['overall_score']}%).")

    # 8. Skill-wise scores calculated correctly
    for sk_res in result_data["skill_scores"]:
        s_name = sk_res["skill"]
        s_exp = expected_skill_stats[s_name]
        assert sk_res["total_questions"] == s_exp["total"]
        assert sk_res["correct_answers"] == s_exp["correct"]
        s_exp_score = round((s_exp["correct"] / s_exp["total"]) * 100.0, 2)
        assert abs(sk_res["score"] - s_exp_score) < 0.01
    print("[OK] 8. Skill-wise scores calculated accurately per skill category.")

    # 9. Completed assessment stored in PostgreSQL
    cur.execute("SELECT completed_at, total_correct, overall_score FROM assessments WHERE id = %s", (ass_id,))
    db_completed = cur.fetchone()
    assert db_completed[0] is not None, "completed_at timestamp was not updated!"
    cur.execute("SELECT count(*) FROM answers WHERE assessment_id = %s", (ass_id,))
    assert cur.fetchone()[0] == 35, "35 answer rows should be saved in DB"
    cur.execute("SELECT count(*) FROM skill_scores WHERE assessment_id = %s", (ass_id,))
    assert cur.fetchone()[0] == 7, "7 skill score rows should be saved in DB"
    print("[OK] 9. Completed assessment, answers, and skill scores stored in PostgreSQL.")

    # 10. Assessment history works
    res = client.get("/assessments/history", headers=headers1)
    assert res.status_code == 200, f"Failed GET /assessments/history: {res.text}"
    history_items = res.json()
    assert len(history_items) >= 1, "History should contain at least 1 assessment"
    assert history_items[0]["id"] == ass_id
    print("[OK] 10. Assessment history endpoint works.")

    # 11. Result endpoint works
    res = client.get(f"/assessments/{ass_id}/result", headers=headers1)
    assert res.status_code == 200, f"Failed GET /assessments/{ass_id}/result: {res.text}"
    res_payload = res.json()
    assert res_payload["overall_score"] == result_data["overall_score"]
    assert len(res_payload["skill_scores"]) == 7
    print("[OK] 11. Result endpoint GET /assessments/{id}/result works.")

    # 12. User cannot access or submit another user's assessment
    res = client.get(f"/assessments/{ass_id}/result", headers=headers2)
    assert res.status_code == 403, f"Expected 403 for cross-user result access, got {res.status_code}"
    res = client.post(f"/assessments/{ass_id}/submit", json={"answers": answers_to_submit}, headers=headers2)
    assert res.status_code == 403, f"Expected 403 for cross-user submit, got {res.status_code}"
    print("[OK] 12. Security verified: User 2 cannot access or submit User 1's assessment (HTTP 403).")

    # 13. Invalid assessment ID is rejected
    res = client.get("/assessments/999999/result", headers=headers1)
    assert res.status_code == 404, f"Expected 404 for non-existent assessment, got {res.status_code}"
    print("[OK] 13. Invalid assessment ID rejected with 404 Not Found.")

    # 14. Invalid question/answer submission rejected
    res_start2 = client.post("/assessments/start", headers=headers1)
    ass_id2 = res_start2.json()["assessment_id"]
    bad_answers = [{"question_id": 999999, "selected_answer": "A"}]
    res = client.post(f"/assessments/{ass_id2}/submit", json={"answers": bad_answers}, headers=headers1)
    assert res.status_code == 400, f"Expected 400 for invalid question ID, got {res.status_code}"
    print("[OK] 14. Invalid question ID in submission rejected with 400 Bad Request.")

    cur.close()
    conn.close()

    print("==================================================")
    print("       ALL PHASE 3 TESTS PASSED SUCCESSFULLY!     ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
