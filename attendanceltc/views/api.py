import re
import io
import csv
import time
import ldap
import json

from flask import current_app as app
from flask import Blueprint, jsonify, request, Response, redirect, url_for
from flask_login import login_required, login_user, logout_user

from attendanceltc.models.shared import db
from attendanceltc.models.course import Course, CourseComponent, Enrollment
from attendanceltc.models.student import Student
from attendanceltc.models.user import User

from .shared import APIResponseMaker

api = Blueprint('api', __name__)
resp = APIResponseMaker()

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result, error = authenticate_with_ldap(username, password)
        if result:
            user = User(username)
            login_user(user)
            n = request.args.get("next")
            if not is_safe_url(n):
                return flask.abort(400)
            if n:
                return redirect(n)
            else:
                return "eat your cookie"
        else:
            return error, 401            
    else:
        return Response('''
        <p>Please log in.</p>
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')

@api.route('/test-login')
@login_required
def test():
    return Response("Wu -- It works! I told you it would -- RV")

@api.route("/rest-login", methods=["PUT"])
def rest_login():
    login_data = json.loads(request.get_data().decode("utf-8"))
    username = login_data["username"]
    password = login_data["password"]
    auth_result, error = authenticate_with_ldap(username, password)
    if auth_result:
        l = login_user(User(username))
        return "", 200
    return "Couldn't authenticate: {error}".format(error=error), 401

def get_ldap():
    return ldap.initialize(app.config["LDAP_URL"])

def authenticate_with_ldap(username, password):
    if username == "admin":
        import hashlib
        import binascii
        dk = hashlib.pbkdf2_hmac('sha256', password.encode("utf-8"), b'attendance.gla.ac.uk', 1000)
        hashed_password = binascii.hexlify(dk).decode()
        if hashed_password == app.config["ADMIN_PASSWORD"]:
            return True, ""
        else:
            return False, "you're no admin of mine"
    elif re.match("^[a-zA-z]*$", username) and len(username) < 32:
        try:
            auth_string = app.config["LDAP_USER_STRING"].format(username=username)
            l = get_ldap()
            l.simple_bind_s(auth_string, password)
            return True, ""
        except ldap.INVALID_CREDENTIALS:
            return False, "Couldn't authenticate username '{username}'  with ldap user string '{auth_string}'".format(username=username, auth_string=auth_string)
        except ldap.UNWILLING_TO_PERFORM as e:
            return False, "empty passwords are not OK or something else: " + str(e)

def add_student(row):
    uid = row["ID"]
    firstname = row["First Name"]
    lastname = row["Last"]
    year = row["Year"]

    # TODO: change these values when feed updates
    email = uid + lastname[0].capitalize() + "@student.gla.ac.uk"

    barcode = row["Barcode"]
    tier4 = (row["CAS Number"] != "")

    student = Student(id=uid, firstname=firstname, lastname=lastname,
                      year=year, email=email, barcode=barcode, tier4=tier4)
    db.session.add(student)

    return student


def add_course(courseid, name):
    course = Course(id=courseid, name=name)
    db.session.add(course)

    return course


def add_course_component(course, component):
    component = CourseComponent(name=component, course=course)
    db.session.add(component)

    return component


def add_student_course_enrollment(student, component):
    e = Enrollment()
    e.component = component
    student.components.append(e)
    db.session.add(e)


def import_mycampus_feed():
    try:
        students = request.get_data().decode("utf-8")
    except:
        return resp.error("Request must contain a valid UTF-8 formatted CSV file.")

    buf = io.StringIO(students)
    reader = csv.DictReader(buf)

    students = {}
    courses = {}
    components = {}
    student_enrollment = set()

    for row in reader:
        guid = row["ID"]

        courseid = row["Subject"] + row["Catalog"]
        coursename = row["Long Title"]

        component = row["Component"]
        compid = row["Lecture"]

        if courseid not in courses:
            course = add_course(courseid, coursename)
            courses[courseid] = course

        if component != "LEC" and (courseid, compid) not in components:
            component = add_course_component(courses[courseid], compid)
            components[(courseid, compid)] = component

        if guid not in students:
            student = add_student(row)
            students[guid] = student

        if component != "LEC" and (guid, courseid, compid) not in student_enrollment:
            student = students[guid]
            component = components[(courseid, compid)]

            add_student_course_enrollment(student, component)

            student_enrollment.add((guid, courseid, compid))

    try:
        db.session.commit()
    except:
        return resp.error("There has been an error updating the database.")

    obj = {
        "message": "Import successful",
        "students": len(students), "courses": len(courses),
        "course_components": len(components),
        "enrollments": len(student_enrollment)
    }

    print(resp)

    resp.data(obj)


@api.route('/students', methods=["POST"])
def import_students():
    # This parameter describes the type of data we are expecting
    # for student import.
    method = request.args.get('uploadType')

    if method == "MATHS_STATS_CSV_1" and request.mimetype == "text/csv":
        import_mycampus_feed()
    else:
        resp.error("Invalid uploadType specified.")

    return resp.get_response()


@api.route('/test', methods=["GET"])
def benchmark():
    q = db.session.query(Student).with_entities(Student.firstname, Student.lastname).join(
        Student.components, Enrollment.component, CourseComponent.course).filter(Course.name == "MATHEMATICS 2P: GRAPHS AND NETWORKS").all()
    return jsonify(q), 200
