import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"

EMAIL = "phase6_test@example.com"
PASSWORD = "Phase6Test@123"


def main():
    print("\n=== PHASE 6 ADAPTATION REGRESSION TEST ===\n")

    # 1. Login
    r = httpx.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": EMAIL,
            "password": PASSWORD,
        },
    )

    assert r.status_code == 200, f"Login failed: {r.text}"

    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("PASS 1: Login")

    # 2. Progress endpoint
    r = httpx.get(
        f"{BASE_URL}/progress/current",
        headers=headers,
    )

    assert r.status_code == 200, f"Progress failed: {r.text}"

    progress = r.json()

    assert progress["previous_assessment_id"] == 50
    assert progress["current_assessment_id"] == 51
    assert progress["current_overall_score"] == 100.0
    assert progress["overall_score_change"] == 20.0
    assert progress["improved_skills"] == 7
    assert progress["declined_skills"] == 0

    print("PASS 2: Progress calculation")

    # 3. Adaptive plan
    r = httpx.post(
        f"{BASE_URL}/study-plans/adapt",
        headers=headers,
    )

    assert r.status_code == 200, f"Adaptation failed: {r.text}"

    plan = r.json()

    assert plan["assessment_id"] == 51
    assert plan["duration_weeks"] == 4
    assert len(plan["tasks"]) == 20

    print("PASS 3: Adaptive plan generated")

    # 4. Validate tasks
    tasks = plan["tasks"]

    assert all(task["status"] == "pending" for task in tasks)

    week_counts = {}

    for task in tasks:
        week = task["week_number"]
        week_counts[week] = week_counts.get(week, 0) + 1

    assert week_counts == {
        1: 5,
        2: 5,
        3: 5,
        4: 5,
    }, f"Unexpected distribution: {week_counts}"

    print("PASS 4: 20 tasks / 5 tasks per week")

    # 5. Validate skills exist
    skills = {task["skill"] for task in tasks}

    expected_skills = {
        "Python",
        "C",
        "DSA",
        "SQL",
        "OOP",
        "DBMS",
        "Aptitude",
    }

    assert skills.issubset(expected_skills)

    print("PASS 5: Valid skills")

    # 6. Idempotency
    first_plan_id = plan["id"]

    r = httpx.post(
        f"{BASE_URL}/study-plans/adapt",
        headers=headers,
    )

    assert r.status_code == 200, f"Second adaptation failed: {r.text}"

    second_plan = r.json()

    assert second_plan["id"] == first_plan_id
    assert len(second_plan["tasks"]) == 20

    print("PASS 6: Adaptation idempotency")

    print("\n======================================")
    print("PHASE 6 ADAPTATION TEST: PASS")
    print("======================================\n")


if __name__ == "__main__":
    main()