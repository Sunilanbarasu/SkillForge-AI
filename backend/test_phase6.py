import httpx
from app.db.session import SessionLocal
from app.models.question import Question

BASE_URL = "http://127.0.0.1:8000/api/v1"

EMAIL = "phase6_test@example.com"
PASSWORD = "Phase6Test@123"


def register_or_login(client):
    r = client.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": EMAIL,
            "password": PASSWORD,
            "name": "Phase 6 Test User",
        },
    )

    if r.status_code == 201:
        print("Registered test user")
    elif r.status_code == 400:
        print("Test user already exists")
    else:
        print("Register:", r.status_code, r.text)

    r = client.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": EMAIL,
            "password": PASSWORD,
        },
    )

    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    print("Login: PASS")

    return {"Authorization": f"Bearer {token}"}


def get_correct_answers():
    db = SessionLocal()
    try:
        questions = db.query(Question).order_by(Question.id).all()
        return {
            q.id: q.correct_answer
            for q in questions
        }
    finally:
        db.close()


def start_assessment(client, headers):
    r = client.post(
        f"{BASE_URL}/assessments/start",
        headers=headers,
    )

    assert r.status_code == 201, r.text

    data = r.json()

    print(
        f"Started assessment {data['assessment_id']} "
        f"with {len(data['questions'])} questions"
    )

    return data


def submit_assessment(client, headers, assessment, correct_answers, make_all_correct):
    answers = []

    for question in assessment["questions"]:
        qid = question["id"]
        correct = correct_answers[qid]

        if make_all_correct:
            selected = correct
        else:
            # Deliberately make every 5th question wrong.
            if qid % 5 == 0:
                selected = "A" if correct != "A" else "B"
            else:
                selected = correct

        answers.append(
            {
                "question_id": qid,
                "selected_answer": selected,
            }
        )

    r = client.post(
        f"{BASE_URL}/assessments/{assessment['assessment_id']}/submit",
        headers=headers,
        json={"answers": answers},
    )

    assert r.status_code == 200, r.text

    result = r.json()

    print(
        f"Assessment {assessment['assessment_id']} completed: "
        f"{result['total_correct']}/{result['total_questions']} "
        f"({result['overall_score']}%)"
    )

    return result


def main():
    correct_answers = get_correct_answers()

    with httpx.Client(timeout=30) as client:
        headers = register_or_login(client)

        # Assessment 1: intentionally weaker
        assessment1 = start_assessment(client, headers)
        result1 = submit_assessment(
            client,
            headers,
            assessment1,
            correct_answers,
            make_all_correct=False,
        )

        # Assessment 2: perfect score
        assessment2 = start_assessment(client, headers)
        result2 = submit_assessment(
            client,
            headers,
            assessment2,
            correct_answers,
            make_all_correct=True,
        )

        # Progress endpoint
        r = client.get(
            f"{BASE_URL}/progress/current",
            headers=headers,
        )

        print("\nProgress endpoint:")
        print("Status:", r.status_code)
        print(r.text)

        assert r.status_code == 200

        progress = r.json()

        assert progress["previous_assessment_id"] == assessment1["assessment_id"]
        assert progress["current_assessment_id"] == assessment2["assessment_id"]

        expected_overall_change = round(
            result2["overall_score"] - result1["overall_score"],
            2,
        )

        assert progress["overall_score_change"] == expected_overall_change

        print("\nPhase 6 progress calculation: PASS")

        # Verify idempotency
        r2 = client.get(
            f"{BASE_URL}/progress/current",
            headers=headers,
        )

        assert r2.status_code == 200
        assert r2.json()["current_assessment_id"] == assessment2["assessment_id"]

        print("Progress endpoint repeat request: PASS")

        print("\n========== PHASE 6 STEP 3 PASS ==========")


if __name__ == "__main__":
    main()