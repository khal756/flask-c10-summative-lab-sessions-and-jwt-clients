from flask import Flask, jsonify
from extensions import db, migrate

app = Flask(__name__)
app.config ["SQLALCHEMY_DATABASE_URI"]="sqlite:///catchup.db"

db.init_app(app)

migrate.init_app(app, db)

from models import User

@app.route("/", methods=["GET"])
def test_app():
    return jsonify({"message": "CatchUp API is running"})

if __name__ == "__main__":
  app.run(debug=True)