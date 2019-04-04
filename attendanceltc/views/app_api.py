import datetime

from flask import Blueprint, jsonify, request, abort, g
from flask_login import LoginManager, login_user, logout_user, current_user

from .login import authenticate

from attendanceltc.models.shared import db
from attendanceltc.models.subject import Subject
from attendanceltc.models.department import Department
from attendanceltc.models.course import Course
from attendanceltc.models.coursecomponent import CourseComponent
from attendanceltc.models.student import Student
from attendanceltc.models.enrollment import Enrollment
from attendanceltc.models.attendance import Attendance
from attendanceltc.models.user import User

from .shared import APIResponseMaker

app_api = Blueprint('app_api', __name__)

def login_required(func):
    def wrapper():
        if not current_user.is_authenticated:
            resp = {"message" : "You do not have permission to access this service."}
            return jsonify(resp), 403
        
        return func()
    
    wrapper.__name__ = func.__name__
    return wrapper

@app_api.route("/phone-api/login", methods=["POST"])
def login():
    login_data = request.get_json()
    g.resp = APIResponseMaker()

    username = login_data["guid"]
    password = login_data["password"]

    auth_result, error = authenticate(username, password)
    if auth_result:
        l = login_user(User(username))

        resp = {"isTutor": True}
        return jsonify(resp), 200
    else:
        resp = {"message": "Invalid GUID or password."}
        return jsonify(resp), 401


@app_api.route("/phone-api/get-groups", methods=["POST"])
@login_required
def get_groups():
    resp = []

    components = db.session.query(Course, CourseComponent) \
        .with_entities(Course.name, Course.id, CourseComponent.name, CourseComponent.id) \
        .order_by(Course.id, CourseComponent.id).limit(10).all()
    
    for component in components:
        course_name, course_id, component_name, component_id = component

        c = {"id": component_id, "name": component_name, "courseId": course_id, "course": course_name}
        resp.append(c)

    return jsonify(resp), 200

@app_api.route("/phone-api/get-students", methods=["POST"])
@login_required
def get_students():
    data = request.get_json()
    component_id = int(data["groupId"])
    course_name = data["course"]

    students_all = db.session.query(Student) \
        .with_entities(Student.id, Student.lastname, Student.firstname, Student.barcode) \
        .join(CourseComponent.students, Enrollment.student) \
        .filter(CourseComponent.id == component_id) \
        .order_by(Student.lastname, Student.firstname).all()

    # Get beginning of the week two weeks ago.
    today = datetime.date.today()
    two_weeks_ago = datetime.timedelta(days=today.weekday(), weeks=2)
    two_weeks_ago = today - two_weeks_ago

    students_attended_today = db.session.query(Student) \
        .with_entities(Student.id) \
        .join(Student.enrollment, Enrollment.component) \
        .join(Attendance, (CourseComponent.id == Attendance.coursecomponent_id) & (Student.id == Attendance.student_id)) \
        .filter(CourseComponent.id == component_id) \
        .filter(Attendance.date == today) \
        .order_by(Student.lastname, Student.firstname).all()

    students_attended_two_weeks_ago = db.session.query(Student) \
        .with_entities(Student.id) \
        .join(Student.enrollment, Enrollment.component) \
        .join(Attendance, (CourseComponent.id == Attendance.coursecomponent_id) & (Student.id == Attendance.student_id)) \
        .filter(CourseComponent.id == component_id) \
        .filter(Attendance.date >= two_weeks_ago) \
        .order_by(Student.lastname, Student.firstname).all()

    attendance = {}
    
    for student in students_all:
        login, last_name, first_name, barcode = student

        fully_qualified_name = last_name + ", " + first_name

        record = {"barcode": barcode,"login": login, "name": fully_qualified_name,
                    "attendedPastTwoWeeks": False, "attendedToday": False}
        
        attendance[login] = record
    
    for student in students_attended_today:
        login, = student

        attendance[login]["attendedToday"] = True
    
    for student in students_attended_two_weeks_ago:
        login, = student

        attendance[login]["attendedPastTwoWeeks"] = True

    return jsonify(list(attendance.values())), 200

@app_api.route("/phone-api/submit-attendance", methods=["POST"])
@login_required
def submit_attendance():
    pass


@app_api.route("/phone-api/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return "", 200