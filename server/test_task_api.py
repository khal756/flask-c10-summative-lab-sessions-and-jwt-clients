
import sys
sys.path.insert(0, "server")

from app import app

client = app.test_client()

# 1. Log in
login = client.post(
    "/login",
    json={
        "username": "demo_student",
        "password": "DemoPass123!"
    }
)
print("LOGIN:", login.status_code)

assert login.status_code == 200, login.json

token = login.json["token"]
headers = {"Authorization": f"Bearer {token}"}

task_id = None

try:
    # 2. Create a temporary task
    response = client.post(
        "/api/tasks",
        headers=headers,
        json={
            "title": "Temporary API Test",
            "task_type": "coding",
            "estimated_minutes": 25,
            "priority": "medium",
            "status": "pending"
        }
    )
    print("CREATE:", response.status_code, response.json)
    assert response.status_code == 201, response.json

    task_id = response.json["id"]

    # 3. Retrieve the new task
    response = client.get(
        f"/api/tasks/{task_id}",
        headers=headers
    )
    print("GET ONE:", response.status_code, response.json)
    assert response.status_code == 200
    assert response.json["title"] == "Temporary API Test"

    # 4. Update the task
    response = client.patch(
        f"/api/tasks/{task_id}",
        headers=headers,
        json={
            "title": "Updated API Test",
            "status": "in_progress"
        }
    )
    print("UPDATE:", response.status_code, response.json)
    assert response.status_code == 200, response.json
    assert response.json["title"] == "Updated API Test"
    assert response.json["status"] == "in_progress"

    # 5. Check pagination
    response = client.get(
        "/api/tasks?page=1&per_page=10",
        headers=headers
    )
    print("LIST/PAGINATION:", response.status_code, response.json)
    assert response.status_code == 200
    assert "pagination" in response.json

finally:
    # 6. Delete the temporary task, even if a test fails
    if task_id is not None:
        cleanup = client.delete(
            f"/api/tasks/{task_id}",
            headers=headers
        )
        print("CLEANUP:", cleanup.status_code)
