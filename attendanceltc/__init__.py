from flask import Flask, jsonify

from flask_login import UserMixin

from .models.shared import db
from .models.user import User

from .views.login import login, login_manager
from .views.import_db import import_db
from .views.school_admin_view import school_admin_view
from .views.course_view import school_course_view

app = Flask(__name__)

app.config.from_object('config_defaults')

try:
    app.config.from_envvar('ATTENDANCELTC_SERVICE_CONFIG')
except:
    print('No configuration file specified, loading with default settings...')

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(login)
app.register_blueprint(import_db)
app.register_blueprint(school_admin_view)
app.register_blueprint(school_course_view)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "server error"}), 500