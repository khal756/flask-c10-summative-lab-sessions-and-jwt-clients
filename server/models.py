from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(30), nullable=False)
    estimated_minutes =db.Column(db.Integer, nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    recording_url = db.Column(db.String(500), nullable=True)
    user = db.relationship("User", backref="tasks")

class StudyAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id =db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    available_minutes = db.Column(db.Integer, nullable=False)

class PlanItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    plan_date = db.Column(db.Date, nullable=False)
    planned_minutes = db.Column(db.Integer, nullable=False)
    position = db.Column(db.Integer, nullable=False)
