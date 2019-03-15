from flask import Flask, jsonify
from .views.api import api
from .models.shared import db

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

with app.app_context():
	db.create_all()

app.register_blueprint(api)

@app.errorhandler(404)
def not_found(error):
	return jsonify({"error": "not found"}), 404

@app.errorhandler(500)
def server_error(error):
	return jsonify({"error": "server error"}), 500