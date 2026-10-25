
from datetime import date, datetime, timedelta

from app import app
from extensions import db, bcrypt
from models import User, Task, StudyAvailability, PlanItem


def seed_data():
    with app.app_context():
        # Find or create the demo user
        user = User.query.filter_by(username="demo_student").first()

        if user is None:
            user = User(
                username="demo_student",
                password_hash=bcrypt.generate_password_hash(
                    "DemoPass123!"
                ).decode("utf-8"),
            )
            db.session.add(user)
            db.session.flush()

        # Find or create a sample task
        task = Task.query.filter_by(
            user_id=user.id,
            title="Complete Flask authentication",
        ).first()

        if task is None:
            task = Task(
                user_id=user.id,
                title="Complete Flask authentication",
                task_type="coding",
                estimated_minutes=60,
                deadline=datetime.combine(
                    date.today() + timedelta(days=7),
                    datetime.min.time(),
                ),
                priority="high",
                status="pending",
                recording_url=None,
            )
            db.session.add(task)
            db.session.flush()

        # Find or create study availability for today
        availability = StudyAvailability.query.filter_by(
            user_id=user.id,
            date=date.today(),
        ).first()

        if availability is None:
            availability = StudyAvailability(
                user_id=user.id,
                date=date.today(),
                available_minutes=120,
            )
            db.session.add(availability)

        # Find or create the planned task
        plan_item = PlanItem.query.filter_by(
            user_id=user.id,
            task_id=task.id,
            plan_date=date.today(),
            position=1,
        ).first()

        if plan_item is None:
            db.session.add(
                PlanItem(
                    user_id=user.id,
                    task_id=task.id,
                    plan_date=date.today(),
                    planned_minutes=60,
                    position=1,
                )
            )

        db.session.commit()
        print("Seed data created successfully.")


if __name__ == "__main__":
    seed_data()

