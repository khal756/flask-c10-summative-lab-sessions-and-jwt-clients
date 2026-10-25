from flask import Flask, jsonify, request
from extensions import db, migrate, bcrypt, jwt

app = Flask(__name__)
app.config ["SQLALCHEMY_DATABASE_URI"]="sqlite:///catchup.db"
app.config["JWT_SECRET_KEY"] = "my-development-secret-change-later"

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
jwt.init_app(app)

from models import User

@app.route("/", methods=["GET"])
def test_app():
    return jsonify({"message": "CatchUp API is running"})

@app.route("/api/register", methods=["POST"])
def register_user():
   data = request.get_json() or {}
   username =data.get("username")
   password = data.get("password")

   if not username or not username.strip() or not password or not password.strip():
      return jsonify({"error": "Username and password are required"}), 400
   existing_user = User.query.filter_by(username=username).first()
   if existing_user:
      return jsonify({"error": "Username already exists"}),409
   username = username.strip()
   hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

   new_user= User(
      username=username,
      password_hash=hashed_password
   )
   db.session.add(new_user)
   db.session.commit()
   return jsonify({"success": "you have successfully registered"}), 201

if __name__ == "__main__":
  app.run(debug=True)