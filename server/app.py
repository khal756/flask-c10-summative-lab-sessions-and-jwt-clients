
from flask import Flask, jsonify, request
from extensions import db, migrate, bcrypt, jwt
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from models import User, Task
from datetime import date
from models import StudyAvailability, PlanItem

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///catchup.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "my-development-secret-change-later"

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
jwt.init_app(app)


@app.route("/", methods=["GET"])
def test_app():
    return jsonify({"message": "CatchUp API is running"}), 200


@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if (
        not isinstance(username, str)
        or not username.strip()
        or not isinstance(password, str)
        or not password.strip()
    ):
        return jsonify({
            "error": "Username and password are required"
        }), 400

    username = username.strip()

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({"error": "Username already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(
        username=username,
        password_hash=hashed_password,
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "success": "You have successfully registered"
    }), 201


@app.route("/api/login", methods=["POST"])
def login_user():
    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({
            "error": "Username and password are required"
        }), 400

    user = User.query.filter_by(username=username.strip()).first()

    if not user or not bcrypt.check_password_hash(
        user.password_hash, password
    ):
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "message": "Successfully logged in",
    }), 200


@app.route("/api/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
    }), 200


def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "task_type": task.task_type,
        "estimated_minutes": task.estimated_minutes,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "priority": task.priority,
        "status": task.status,
        "recording_url": task.recording_url,
    }


def get_authenticated_user():
    user_id = get_jwt_identity()
    return db.session.get(User, int(user_id))



@app.route("/api/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    user = get_authenticated_user()

    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        page = max(1, request.args.get("page", 1, type=int))
        per_page = request.args.get("per_page", 10, type=int)

        if per_page is None or per_page < 1:
            return jsonify({"error": "per_page must be a positive integer"}), 400

        per_page = min(per_page, 100)

    except (TypeError, ValueError):
        return jsonify({"error": "Invalid pagination parameters"}), 400

    pagination = (
        Task.query
        .filter_by(user_id=user.id)
        .order_by(Task.id)
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        "tasks": [task_to_dict(task) for task in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_previous": pagination.has_prev
        }
    }), 200

@app.route("/api/tasks", methods=["POST"])
@jwt_required()
def create_task():
    user = get_authenticated_user()

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}

    required_fields = [
        "title",
        "task_type",
        "estimated_minutes",
        "priority",
        "status",
    ]

    for field in required_fields:
        if field not in data or data[field] is None:
            return jsonify({"error": f"{field} is required"}), 400

    if not isinstance(data["title"], str) or not data["title"].strip():
        return jsonify({"error": "Title must not be empty"}), 400

    if (
        type(data["estimated_minutes"]) is not int
        or data["estimated_minutes"] <= 0
    ):
        return jsonify({
            "error": "estimated_minutes must be a positive integer"
        }), 400

    allowed_priorities = {"low", "medium", "high"}
    allowed_statuses = {"pending", "in_progress", "completed"}

    if data["priority"] not in allowed_priorities:
        return jsonify({
            "error": "priority must be low, medium, or high"
        }), 400

    if data["status"] not in allowed_statuses:
        return jsonify({
            "error": "status must be pending, in_progress, or completed"
        }), 400

    deadline = None

    if data.get("deadline"):
        from datetime import datetime

        try:
            deadline = datetime.fromisoformat(data["deadline"])
        except (ValueError, TypeError):
            return jsonify({
                "error": "deadline must be a valid ISO date/time"
            }), 400

    task = Task(
        user_id=user.id,
        title=data["title"].strip(),
        task_type=data["task_type"],
        estimated_minutes=data["estimated_minutes"],
        deadline=deadline,
        priority=data["priority"],
        status=data["status"],
        recording_url=data.get("recording_url"),
    )

    db.session.add(task)
    db.session.commit()

    return jsonify(task_to_dict(task)), 201


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    user = get_authenticated_user()

    if not user:
        return jsonify({"error": "User not found"}), 404

    task = Task.query.filter_by(
        id=task_id, user_id=user.id
    ).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task_to_dict(task)), 200


@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
@jwt_required()
def update_task(task_id):
    user = get_authenticated_user()

    if not user:
        return jsonify({"error": "User not found"}), 404

    task = Task.query.filter_by(
        id=task_id, user_id=user.id
    ).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Provide task fields to update"}), 400

    allowed_fields = {
        "title",
        "task_type",
        "estimated_minutes",
        "deadline",
        "priority",
        "status",
        "recording_url",
    }

    unknown_fields = set(data) - allowed_fields

    if unknown_fields:
        return jsonify({
            "error": "Unknown fields",
            "fields": sorted(unknown_fields),
        }), 400

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return jsonify({"error": "Title must not be empty"}), 400
        task.title = data["title"].strip()

    if "task_type" in data:
        if not isinstance(data["task_type"], str) or not data["task_type"].strip():
            return jsonify({"error": "task_type must not be empty"}), 400
        task.task_type = data["task_type"].strip()

    if "estimated_minutes" in data:
        minutes = data["estimated_minutes"]
        if type(minutes) is not int or minutes <= 0:
            return jsonify({
                "error": "estimated_minutes must be a positive integer"
            }), 400
        task.estimated_minutes = minutes

    if "priority" in data:
        if data["priority"] not in {"low", "medium", "high"}:
            return jsonify({
                "error": "priority must be low, medium, or high"
            }), 400
        task.priority = data["priority"]

    if "status" in data:
        if data["status"] not in {"pending", "in_progress", "completed"}:
            return jsonify({
                "error": "status must be pending, in_progress, or completed"
            }), 400
        task.status = data["status"]

    if "deadline" in data:
        if data["deadline"] is None or data["deadline"] == "":
            task.deadline = None
        elif not isinstance(data["deadline"], str):
            return jsonify({"error": "deadline must be a string"}), 400
        else:
            from datetime import datetime

            try:
                task.deadline = datetime.fromisoformat(data["deadline"])
            except ValueError:
                return jsonify({
                    "error": "deadline must be a valid ISO date/time"
                }), 400

    if "recording_url" in data:
        if data["recording_url"] is not None and not isinstance(
            data["recording_url"], str
        ):
            return jsonify({"error": "recording_url must be a string or null"}), 400
        task.recording_url = data["recording_url"]

    db.session.commit()

    return jsonify(task_to_dict(task)), 200


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user = get_authenticated_user()

    if not user:
        return jsonify({"error": "User not found"}), 404

    task = Task.query.filter_by(
        id=task_id, user_id=user.id
    ).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return "", 204


def parse_date(value):
    if not isinstance(value, str):
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


@app.route("/api/availability", methods=["GET"])
@jwt_required()
def get_availability():
    user_id = int(get_jwt_identity())

    records = StudyAvailability.query.filter_by(
        user_id=user_id
    ).order_by(StudyAvailability.date).all()

    return jsonify([
        {
            "id": record.id,
            "date": record.date.isoformat(),
            "available_minutes": record.available_minutes,
        }
        for record in records
    ]), 200


@app.route("/api/availability", methods=["POST"])
@jwt_required()
def create_availability():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    study_date = parse_date(data.get("date"))
    minutes = data.get("available_minutes")

    if study_date is None:
        return jsonify({
            "error": "date must be a valid YYYY-MM-DD date"
        }), 400

    if type(minutes) is not int or minutes <= 0:
        return jsonify({
            "error": "available_minutes must be a positive integer"
        }), 400

    existing = StudyAvailability.query.filter_by(
        user_id=user_id,
        date=study_date,
    ).first()

    if existing:
        return jsonify({
            "error": "Availability already exists for this date"
        }), 409

    record = StudyAvailability(
        user_id=user_id,
        date=study_date,
        available_minutes=minutes,
    )

    db.session.add(record)
    db.session.commit()

    return jsonify({
        "id": record.id,
        "date": record.date.isoformat(),
        "available_minutes": record.available_minutes,
    }), 201


@app.route("/api/plan", methods=["GET"])
@jwt_required()
def get_study_plan():
    user_id = int(get_jwt_identity())

    items = PlanItem.query.filter_by(
        user_id=user_id
    ).order_by(
        PlanItem.plan_date,
        PlanItem.position,
    ).all()

    return jsonify([
        {
            "id": item.id,
            "task_id": item.task_id,
            "plan_date": item.plan_date.isoformat(),
            "planned_minutes": item.planned_minutes,
            "position": item.position,
        }
        for item in items
    ]), 200


@app.route("/api/plan", methods=["POST"])
@jwt_required()
def create_plan_item():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    task_id = data.get("task_id")
    plan_date = parse_date(data.get("plan_date"))
    minutes = data.get("planned_minutes")
    position = data.get("position")

    if type(task_id) is not int:
        return jsonify({"error": "task_id must be an integer"}), 400

    task = Task.query.filter_by(
        id=task_id,
        user_id=user_id,
    ).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    if plan_date is None:
        return jsonify({
            "error": "plan_date must be a valid YYYY-MM-DD date"
        }), 400

    if type(minutes) is not int or minutes <= 0:
        return jsonify({
            "error": "planned_minutes must be a positive integer"
        }), 400

    if type(position) is not int or position < 1:
        return jsonify({
            "error": "position must be a positive integer"
        }), 400

    availability = StudyAvailability.query.filter_by(
        user_id=user_id,
        date=plan_date,
    ).first()

    if not availability:
        return jsonify({
            "error": "Set study availability for this date first"
        }), 400

    already_planned = PlanItem.query.filter_by(
        user_id=user_id,
        plan_date=plan_date,
    ).all()

    used_minutes = sum(item.planned_minutes for item in already_planned)

    if used_minutes + minutes > availability.available_minutes:
        return jsonify({
            "error": "Plan exceeds available study time",
            "available_minutes": availability.available_minutes,
            "already_planned_minutes": used_minutes,
        }), 400

    item = PlanItem(
        user_id=user_id,
        task_id=task_id,
        plan_date=plan_date,
        planned_minutes=minutes,
        position=position,
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "id": item.id,
        "task_id": item.task_id,
        "plan_date": item.plan_date.isoformat(),
        "planned_minutes": item.planned_minutes,
        "position": item.position,
    }), 201


@app.route("/api/plan/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_plan_item(item_id):
    user_id = int(get_jwt_identity())

    item = PlanItem.query.filter_by(
        id=item_id,
        user_id=user_id,
    ).first()

    if not item:
        return jsonify({"error": "Plan item not found"}), 404

    db.session.delete(item)
    db.session.commit()

    return "", 204




if __name__ == "__main__":
    app.run(debug=True)
