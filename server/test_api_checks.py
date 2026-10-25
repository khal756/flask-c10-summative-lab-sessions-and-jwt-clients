
from app import app

client = app.test_client()

# Log in as the demo user
login = client.post(
    "/login",
    json={
        "username": "demo_student",
        "password": "DemoPass123!"
    }
)
assert login.status_code == 200, login.json

token = login.json["token"]
headers = {"Authorization": f"Bearer {token}"}

# Test 1: Missing task fields should be rejected
response = client.post(
    "/api/tasks",
    headers=headers,
    json={"title": "Incomplete task"}
)
print("MISSING FIELDS:", response.status_code, response.json)
assert response.status_code == 400

# Test 2: Zero estimated minutes should be rejected
response = client.post(
    "/api/tasks",
    headers=headers,
    json={
        "title": "Invalid duration",
        "task_type": "coding",
        "estimated_minutes": 0,
        "priority": "medium",
        "status": "pending"
    }
)
print("INVALID DURATION:", response.status_code, response.json)
assert response.status_code == 400

# Test 3: Invalid priority should be rejected
response = client.post(
    "/api/tasks",
    headers=headers,
    json={
        "title": "Invalid priority",
        "task_type": "coding",
        "estimated_minutes": 20,
        "priority": "urgent",
        "status": "pending"
    }
)
print("INVALID PRIORITY:", response.status_code, response.json)
assert response.status_code == 400

# Test 4: Protected route without a token should be rejected
response = client.get("/api/tasks")
print("NO TOKEN:", response.status_code, response.json)
assert response.status_code == 401

# Test 5: Invalid login should be rejected
response = client.post(
    "/login",
    json={
        "username": "demo_student",
        "password": "wrong-password"
    }
)
print("INVALID LOGIN:", response.status_code, response.json)
assert response.status_code == 401

print("\nAll validation and authentication checks passed!")
