# CatchUp API

CatchUp is a Flask backend for a productivity app that helps users manage tasks, track study availability, and plan their study sessions.

## Features
- User registration and JWT authentication
- Create, view, update, and delete tasks
- Manage study availability and study plans
- Secure user data and protected routes
- Task pagination

## Technologies
Python, Flask, SQLAlchemy, Flask-Migrate, Flask-Bcrypt, JWT, and SQLite.

## Setup
1. Install dependencies using `python -m pipenv install`.
2. Run database migrations using `python -m flask db upgrade`.
3. Seed sample data using `python seed.py`.
4. Start the server using `python app.py`.

## Authentication
Log in to receive a JWT access token. Include it in protected requests using `Authorization: Bearer YOUR_ACCESS_TOKEN`.

