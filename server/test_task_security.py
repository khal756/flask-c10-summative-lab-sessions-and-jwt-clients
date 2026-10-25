
from app import app

client = app.test_client()

# Log in as the existing demo user
login = client.post(
    "/login",
    json={
        "username": "demo_student",
        "password": "DemoPass123!"
    }
)
assert login.status_code == 200
headers = {
    "Authorization": f"Bearer {login.json['token']}"
}

# Register a second, temporary user
signup = client.post(
    "/signup",
    json={
        "username": "security_test_user",
        "password": "SecurityPass123!",
        "password_confirmation": "SecurityPass123!"
    }
)
print("CREATE SECOND USER:", signup.status_code)
assert signup.status_code == 201, signup.json

# Log in as the second user
login2 = client.post(
    "/login",
    json={
        "username": "security_test_user",
        "password": "SecurityPass123!"
    }
)
assert login2.status_code == 200
headers2 = {
    "Authorization": f"Bearer {login2.json['token']}"
}

# Demo user creates a temporary task
created = client.post(
    "/api/tasks",
    headers=headers,
    json={
        "title": "Private security test task",
        "task_type": "coding",
        "estimated_minutes": 15,
        "priority": "low",
        "status": "pending"
    }
)
assert created.status_code == 201, created.json
task_id = created.json["id"]

try:
    # Second user must not read the task
    response = client.get(
        f"/api/tasks/{task_id}",
        headers=headers2
    )
    print("OTHER USER READ:", response.status_code, response.json)
    assert response.status_code == 404

    # Second user must not update the task
    response = client.patch(
        f"/api/tasks/{task_id}",
        headers=headers2,
        json={"title": "Unauthorized change"}
    )
    print("OTHER USER UPDATE:", response.status_code, response.json)
    assert response.status_code == 404

    # Second user must not delete the task
    response = client.delete(
        f"/api/tasks/{task_id}",
        headers=headers2
    )
    print("OTHER USER DELETE:", response.status_code, response.json)
    assert response.status_code == 404

    # Confirm the original owner can still read it
    response = client.get(
        f"/api/tasks/{task_id}",
        headers=headers
    )
    print("OWNER READ:", response.status_code)
    assert response.status_code == 200

finally:
    # Clean up the temporary task and test account
    client.delete(f"/api/tasks/{task_id}", headers=headers)

    from models import User
    from extensions import db

    with app.app_context():
        test_user = User.query.filter_by(
            username="security_test_user"
        ).first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()

print("\nAll cross-user security checks passed!")
