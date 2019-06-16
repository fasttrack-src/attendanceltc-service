import datetime

from flask import Blueprint, jsonify, request, abort, g
from flask_login import LoginManager, login_user, logout_user, current_user

from sqlalchemy import Date, cast

from .login import authenticate
from attendanceltc.models import db, Subject, Department, Course, CourseComponent, Student, Enrollment, Attendance, User

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

    try:
        username = login_data["guid"]
        password = login_data["password"]
    except:
        resp = {"message": "Invalid JSON submitted."}
        return jsonify(resp), 400
    
    auth_result, error = authenticate(username, password)
    if auth_result:
        l = login_user(User(username))

        resp = {"isTutor": True}
        return jsonify(resp), 200
    else:
        resp = {"message": "Invalid GUID or password."}
        return jsonify(resp), 401


@app_api.route("/phone-api/get-groups", methods=["GET"])
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

    try:
        component_id = int(data["componentId"])
    except:
        resp = {"message": "Invalid JSON submitted."}
        return jsonify(resp), 400

    students_all = db.session.query(Student) \
        .with_entities(Student.id, Student.lastname, Student.firstname, Student.barcode) \
        .join(CourseComponent.students, Enrollment.student) \
        .filter(CourseComponent.id == component_id) \
        .order_by(Student.lastname, Student.firstname).all()

    # Get beginning of the week two weeks ago.
    # TODO: this is really hacky, sqlite does not support datetime-to-date casting.
    # change this once migrated to mysql
    today = datetime.date.today()
    today_start = datetime.datetime.combine(today, datetime.datetime.min.time())
    today_end = datetime.datetime.combine(today, datetime.datetime.max.time())

    two_weeks_ago = datetime.timedelta(days=today.weekday(), weeks=2)
    two_weeks_ago = today_start - two_weeks_ago

    students_attended_today = db.session.query(Student) \
        .with_entities(Student.id) \
        .join(Student.enrollment, Enrollment.component) \
        .join(Attendance, (CourseComponent.id == Attendance.coursecomponent_id) & (Student.id == Attendance.student_id)) \
        .filter(CourseComponent.id == component_id) \
        .filter((Attendance.timestamp >= today_start) & (Attendance.timestamp <= today_end)) \
        .group_by(Student.id) \
        .order_by(Student.lastname, Student.firstname).all()

    students_attended_two_weeks_ago = db.session.query(Student) \
        .with_entities(Student.id) \
        .join(Student.enrollment, Enrollment.component) \
        .join(Attendance, (CourseComponent.id == Attendance.coursecomponent_id) & (Student.id == Attendance.student_id)) \
        .filter(CourseComponent.id == component_id) \
        .filter(Attendance.timestamp >= two_weeks_ago) \
        .group_by(Student.id) \
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
    data = request.get_json()

    try:
        barcode = str(data["barcode"])
        student = db.session.query(Student).filter(Student.barcode == barcode).one()

        component = int(data["componentId"])
        component = db.session.query(CourseComponent).get(component)

        date = datetime.date.fromtimestamp(int(data["timestamp"]) / 1e3)
        date_start = datetime.datetime.combine(date, datetime.datetime.min.time())
        date_end = datetime.datetime.combine(date, datetime.datetime.max.time())
        timestamp = datetime.datetime.fromtimestamp(int(data["timestamp"]) / 1e3)

    except:
        resp = {"message": "Invalid request submitted."}
        return jsonify(resp), 400

    db.session.query(Attendance) \
        .filter(Attendance.student == student) \
        .filter(Attendance.component == component) \
        .filter((Attendance.timestamp >= date_start) & (Attendance.timestamp <= date_end)).delete()

    att = Attendance(timestamp=timestamp, student=student, component=component)
    db.session.add(att)
    db.session.commit()

    return "", 200

@app_api.route("/phone-api/delete-attendance", methods=["POST"])
@login_required
def delete_attendance():
    data = request.get_json()

    try:
        barcode = str(data["barcode"])
        student = db.session.query(Student).filter(Student.barcode == barcode).one()

        component = int(data["componentId"])
        component = db.session.query(CourseComponent).get(component)

        date = datetime.date.fromtimestamp(int(data["timestamp"]) / 1e3)
        date_start = datetime.datetime.combine(date, datetime.datetime.min.time())
        date_end = datetime.datetime.combine(date, datetime.datetime.max.time())        
    except:
        resp = {"message": "Invalid request submitted."}
        return jsonify(resp), 400

    matching_attendance = db.session.query(Attendance) \
        .filter(Attendance.student == student) \
        .filter(Attendance.component == component) \
        .filter((Attendance.timestamp >= date_start) & (Attendance.timestamp <= date_end)).delete()
    db.session.commit()

    return "", 200

@app_api.route("/phone-api/get-attendance", methods=["POST"])
@login_required
def get_attendance():
    data = request.get_json()
    resp = []

    try:
        login = str(data["studentLogin"])
        student = db.session.query(Student).get(login)
    except:
        resp = {"message": "Invalid request submitted."}
        return jsonify(resp), 400
    
    all_attendance = db.session.query(Attendance, Course) \
        .with_entities(Course.name, Attendance.timestamp) \
        .join(Attendance.component, CourseComponent.course) \
        .filter(Attendance.student == student) \
        .all()
    
    for attendance in all_attendance:
        course, timestamp = attendance

        record = {"course": course, "date": timestamp.day, "month": timestamp.month, "year": timestamp.year}
        resp.append(record)

    return jsonify(resp), 200

@app_api.route("/phone-api/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return "", 200