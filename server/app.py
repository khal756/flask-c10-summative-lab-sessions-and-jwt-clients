from flask import Flask, jsonify, request
from extensions import db, migrate, bcrypt, jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

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

@app.route("/api/login", methods=["POST"])
def login_user():
   data = request.get_json() or {}

   username = data.get("username")
   password = data.get("password")

   missing_user = User.query.filter_by(username=username).first()
   if not missing_user:
      return jsonify({"error": "User does not exist"}), 401
   
   if not bcrypt.check_password_hash(
      missing_user.password_hash,
      password
   ):
      return jsonify({"error": "Invalid username or password"}), 401

   access_token = create_access_token(identity=str(missing_user.id))
   return jsonify({
      "access_token": access_token,
      "message": "successfully logged in"
   }), 200

@app.route("/api/me", methods=["GET"])
@jwt_required()
def get_current_user():
   user_id = get_jwt_identity()
   user=User.query.get(user_id)
   return jsonify({
      "id" : user.id,
      "username" : user.username
    })
      
   
if __name__ == "__main__":
  app.run(debug=True)