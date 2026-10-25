# CatchUp API

CatchUp is a Flask REST API for managing tasks and planning study sessions.

## Features

- User registration and login
- JWT authentication
- Create, view, update, and delete tasks
- Task pagination
- Manage study availability and study plans
- Protect user data

## Technologies

- Python and Flask
- SQLAlchemy
- SQLite
- Flask-Migrate
- Flask-Bcrypt
- Flask-JWT-Extended
- React

## Setup

1. Open the `server` directory.
2. Install dependencies:

   ```bash
   python -m pipenv install
   ```

3. Run database migrations:

   ```bash
   python -m pipenv run python -m flask --app app db upgrade
   ```

4. Seed the database:

   ```bash
   python -m pipenv run python seed.py
   ```

5. Start the backend:

   ```bash
   python -m pipenv run python app.py
   ```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/signup` | Register |
| POST | `/login` | Login |
| GET | `/me` | Get current user |
| GET | `/api/tasks` | List tasks |
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks/<task_id>` | View task |
| PATCH | `/api/tasks/<task_id>` | Update task |
| DELETE | `/api/tasks/<task_id>` | Delete task |
| GET | `/api/availability` | View availability |
| POST | `/api/availability` | Set availability |
| GET | `/api/plan` | View study plan |
| POST | `/api/plan` | Add plan item |
| DELETE | `/api/plan/<item_id>` | Delete plan item |

Protected endpoints require a valid JWT access token.

## Testing

Run the test scripts from the `server` directory:

```bash
python test_task_api.py
python test_api_checks.py
python test_task_security.py
```

## Author

Moringa School backend summative project.
