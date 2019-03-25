import re
import io
import csv
import time
import ldap
import json
import functools

from flask import current_app as app
from flask import Blueprint, jsonify, request, Response, redirect, url_for, g
from flask_login import login_required, login_user, logout_user

from sqlalchemy import func
from sqlalchemy.sql import functions
from sqlalchemy.sql.expression import Tuple

from attendanceltc.models.shared import db, get_one_or_create
from attendanceltc.models.course import Course
from attendanceltc.models.coursecomponent import CourseComponent
from attendanceltc.models.student import Student
from attendanceltc.models.enrollment import Enrollment
from attendanceltc.models.subject import Subject
from attendanceltc.models.department import Department
from attendanceltc.models.user import User

from .shared import APIResponseMaker

api = Blueprint('api', __name__)


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
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(
            "utf-8"), b'attendance.gla.ac.uk', 1000)
        hashed_password = binascii.hexlify(dk).decode()
        if hashed_password == app.config["ADMIN_PASSWORD"]:
            return True, ""
        else:
            return False, "you're no admin of mine"
    elif re.match("^[a-zA-z]*$", username) and len(username) < 32:
        try:
            auth_string = app.config["LDAP_USER_STRING"].format(
                username=username)
            l = get_ldap()
            l.simple_bind_s(auth_string, password)
            return True, ""
        except ldap.INVALID_CREDENTIALS:
            return False, "Couldn't authenticate username '{username}'  with ldap user string '{auth_string}'".format(username=username, auth_string=auth_string)
        except ldap.UNWILLING_TO_PERFORM as e:
            return False, "empty passwords are not OK or something else: " + str(e)

def import_mycampus_feed():
    try:
        students = request.get_data().decode("utf-8")
    except:
        return g.resp.error("Request must contain a valid UTF-8 formatted CSV file.")

    buf = io.StringIO(students)
    reader = csv.DictReader(buf)

    # First upsert students and courses
    subjects = {}
    students = {}
    courses = {}
    components = {}
    enrollments = {}

    for row in reader:
        subject_id = row["Subject"]
        catalog_id = row["Catalog"]
        student_id = row["ID"]
        component_name = row["Lecture"]
        component_type = row["Component"]

        course_key = (subject_id, catalog_id)
        student_key = (student_id,)
        component_key = (subject_id, catalog_id, component_name)
        enrollment_key = (student_id, subject_id, catalog_id, component_name)

        if subject_id not in subjects:
            existing_enrollment = db.session.query(Enrollment).join(
                Enrollment.component, CourseComponent.course, Course.subject).filter_by(id=subject_id).all()
            
            for enrollment in existing_enrollment:
                db.session.delete(enrollment)
            
            subject = db.session.query(Subject).get(subject_id)

            if not subject:
                error = "Subject code {} does not correspond to a valid department.".format(
                    subject_id)
                return g.resp.error(error, status=400)

            subjects[subject_id] = subject
        
        if course_key not in courses:
            course, found = get_one_or_create(db.session, Course,
                catalog_id=catalog_id,
                subject_id=subject_id,
                name=row["Long Title"])

            if not found:
                db.session.add(course)
                db.session.flush()
            
            print("course w id", (course.id, course.name), "created")

            courses[course_key] = course        

        if student_key not in students:
            student, found = get_one_or_create(db.session, Student,
                id=student_id,
                firstname=row["First Name"],
                lastname=row["Last"],
                year=row["Year"],
                email= "{}{}@student.gla.ac.uk".format(student_id, row["Last"][0].capitalize()),
                barcode=row["Barcode"],
                tier4=(row["CAS Number"] != ""))

            if not found:
                db.session.add(student)
                db.session.flush()

            students[student_key] = student

        if component_key not in components:
            component, found = get_one_or_create(db.session, CourseComponent, name=component_name, course_id=courses[course_key].id)

            if not found:
                db.session.add(component)
                db.session.flush()
            
            components[component_key] = component
        
        if enrollment_key not in enrollments:
            enrollment = Enrollment(student=students[student_key], component=components[component_key])
        
            enrollments[enrollment_key] = enrollment
    
    db.session.add_all(enrollments.values())

    #try:
    db.session.commit()
    #except:
    #    return g.resp.error("There has been an error updating the database.")

    g.resp.data("Successful import.")


@api.route('/students', methods=["POST"])
def import_students():
    g.resp = APIResponseMaker()

    # This parameter describes the type of data we are expecting
    # for student import.
    method = request.args.get('uploadType')

    if method == "MATHS_STATS_CSV_1" and request.mimetype == "text/csv":

        import_mycampus_feed()
    else:
        g.resp.error("Invalid uploadType specified.")

    return g.resp.get_response()
