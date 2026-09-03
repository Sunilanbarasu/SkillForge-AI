import sys
import httpx
import psycopg2

BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_EMAIL = "test_student@example.com"
TEST_PASSWORD = "secret123"
TEST_NAME = "Test Student"

def run_tests():
    print("==================================================")
    print("       STARTING PHASE 2 AUTOMATED TEST SUITE     ")
    print("==================================================")
    
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # 1. Health Check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    assert res.json()["database"]["status"] == "connected", "DB disconnected!"
    print("[OK] 1. Health endpoint active and PostgreSQL connected.")

    # 2. Register New User
    reg_payload = {"name": TEST_NAME, "email": TEST_EMAIL, "password": TEST_PASSWORD}
    res = client.post("/auth/register", json=reg_payload)
    if res.status_code == 400 and "already exists" in res.text:
        print("[INFO] Test user already exists, proceeding to login...")
    else:
        assert res.status_code == 201, f"Registration failed: {res.text}"
        data = res.json()
        assert "access_token" in data, "Token missing from register response"
        assert "hashed_password" not in data["user"], "SECURITY FAIL: hashed_password exposed in registration response!"
        print("[OK] 2. User registration successful (hashed_password NOT returned).")

    # 3. Duplicate Email Rejection
    res = client.post("/auth/register", json=reg_payload)
    assert res.status_code == 400, f"Expected 400 for duplicate email, got {res.status_code}: {res.text}"
    print("[OK] 3. Duplicate email registration rejected with 400 Bad Request.")

    # 4. Invalid Password Login Rejection
    res = client.post("/auth/login", json={"email": TEST_EMAIL, "password": "wrongpassword123"})
    assert res.status_code == 401, f"Expected 401 for wrong password, got {res.status_code}: {res.text}"
    print("[OK] 4. Invalid password login rejected with 401 Unauthorized.")

    # 5. Valid Password Login
    res = client.post("/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token_data = res.json()
    assert "access_token" in token_data, "access_token missing from login response"
    token = token_data["access_token"]
    assert "hashed_password" not in token_data["user"], "SECURITY FAIL: hashed_password exposed in login response!"
    print("[OK] 5. Valid login successful (JWT token generated, hashed_password NOT returned).")

    # 6. Unauthenticated Access Protection
    for endpoint in ["/users/me", "/profile"]:
        res_no_auth = client.get(endpoint)
        assert res_no_auth.status_code in (401, 403), f"Expected 401/403 for unauthenticated {endpoint}, got {res_no_auth.status_code}"
    print("[OK] 6. Protected endpoints (/users/me, /profile) properly reject unauthenticated requests.")

    # 7. Invalid/Expired JWT Rejection
    res_bad_token = client.get("/users/me", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert res_bad_token.status_code == 401, f"Expected 401 for invalid JWT, got {res_bad_token.status_code}"
    print("[OK] 7. Invalid JWT correctly rejected with 401 Unauthorized.")

    # 8. Authenticated Access with Valid JWT
    auth_headers = {"Authorization": f"Bearer {token}"}
    res_me = client.get("/users/me", headers=auth_headers)
    assert res_me.status_code == 200, f"Failed GET /users/me: {res_me.text}"
    user_me = res_me.json()
    assert user_me["email"] == TEST_EMAIL, f"Email mismatch: {user_me['email']}"
    assert "hashed_password" not in user_me, "SECURITY FAIL: hashed_password returned in /users/me!"
    print("[OK] 8. Authenticated /users/me returned user details (hashed_password omitted).")

    # 9. Get & Update Student Profile
    res_prof = client.get("/profile", headers=auth_headers)
    assert res_prof.status_code == 200, f"Failed GET /profile: {res_prof.text}"
    
    update_payload = {
        "target_role": "Backend Software Engineer",
        "experience_level": "Intermediate",
        "interests": ["System Design", "Databases"],
        "selected_skills": ["Python", "DSA", "SQL"]
    }
    res_upd = client.put("/profile", json=update_payload, headers=auth_headers)
    assert res_upd.status_code == 200, f"Failed PUT /profile: {res_upd.text}"
    updated_prof = res_upd.json()
    assert updated_prof["target_role"] == "Backend Software Engineer"
    assert updated_prof["selected_skills"] == ["Python", "DSA", "SQL"]
    print("[OK] 9. Student Profile created & updated via REST API.")

    # 10. Direct PostgreSQL Verification
    conn = psycopg2.connect(host="127.0.0.1", port=5432, user="postgres", password="postgres", dbname="skillforge_ai")
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, hashed_password FROM users WHERE email = %s", (TEST_EMAIL,))
    db_user = cur.fetchone()
    assert db_user is not None, "User not found in PostgreSQL database!"
    u_id, u_name, u_email, u_hash = db_user
    
    # Verify password security
    assert u_hash != TEST_PASSWORD, f"SECURITY CRITICAL: Plaintext password saved in database!"
    assert u_hash.startswith("$2b$"), f"Password is not a valid bcrypt hash: {u_hash}"
    print("[OK] 10. Direct PostgreSQL check: Password is stored as a valid bcrypt hash ($2b$) and NEVER as plaintext.")

    cur.execute("SELECT id, target_role, experience_level, selected_skills FROM profiles WHERE user_id = %s", (u_id,))
    db_prof = cur.fetchone()
    assert db_prof is not None, "Profile row not found in PostgreSQL database!"
    print("[OK] 11. Direct PostgreSQL check: Profile row exists and is linked via Foreign Key.")

    cur.close()
    conn.close()

    print("==================================================")
    print("       ALL PHASE 2 TESTS PASSED SUCCESSFULLY!     ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
