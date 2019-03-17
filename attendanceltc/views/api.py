import io
import csv
import time

from flask import Blueprint, jsonify, request

from attendanceltc.models.shared import db
from attendanceltc.models.course import Course, CourseComponent, Enrollment
from attendanceltc.models.student import Student

from .shared import APIResponseMaker

api = Blueprint('api', __name__)
resp = APIResponseMaker()

"""

def read_config():
    #
    #Looks up the name of the database, in the following order:
    #1. config file `$HOME/.config/bulk_ltc.conf`
    #2. config file `./bulk_ltc.conf`
    #
    home_conf = os.path.join(os.environ["HOME"], ".config", "bulk_ltc.conf")
    local_conf = os.path.join(os.environ["PWD"], "bulk_ltc.conf")
    try:
        with open(home_conf) as f:
            cfg = json.load(f)
        return cfg
    except FileNotFoundError:
        try:
            with open(local_conf) as f:
                cfg = json.load(f)
            return cfg
        except FileNotFoundError:
            raise Exception("bulk ltc requires a config file to reside in {home_path} or locally as {local_conf}".format(home_path=home_conf, local_conf=local_conf))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, name):
        self.id = name
    def __repr__(self):
        return "<User: %d>" % (self.id)

@app.route('/test-login')
@login_required
def test():
    return Response("Wu -- It works! I told you it would -- RV")

@app.route("/rest-login", methods=["PUT"])
def rest_login():
    login_data = json.loads(request.get_data().decode("utf-8"))
    username = login_data["username"]
    password = login_data["password"]
    cfg = read_config()
    auth_result, error = authenticate_with_dcs_ldap(username, password)
    if auth_result:
        l = login_user(User(username))
        return "", 200
    return "Couldn't authenticate: {error}".format(error=error), 401

#### LDAP login ####

def get_ldap():
    cfg = read_config()
    return ldap.initialize(cfg["ldap_URL"])

def authenticate_with_dcs_ldap(username, password):
    cfg = read_config()
    if username == "admin":
        import hashlib
        m = hashlib.sha256()
        m.update(password.encode("utf-8"))
        m.update("dcs.gla.ac.uk".encode("utf-8"))
        hashed_password = m.hexdigest()
        if hashed_password == cfg["admin_password"]:
            return True, ""
        else:
            return False, "you're no admin of mine"
    elif re.match("^[a-zA-z]*$", username) and len(username) < 32:
        try:
            auth_string = cfg["ldap_user_string"].format(username=username)
            l = get_ldap()
            l.simple_bind_s(auth_string, password)
            user_record = l.search_s(cfg["ldap_person_base"], ldap.SCOPE_SUBTREE, cfg["ldap_search_query"].format(username=username))
            if len(user_record) > 1:
                return False, "your username corresponds to more than 1 ldap record."
            if len(user_record) < 1:
                return False, "although we can log you in OK, we can't find your ldap record."
            result = bytes(cfg["ldap_check_member_of"], "utf-8") in user_record[0][1]['memberOf']
            if result:
                return True, ""
            else:
                return False, "If you're an undergraduate: get your hands off of my microservice! Otherwise, please ask Stewart to set you up as the AMS Tutor."
        except ldap.INVALID_CREDENTIALS:
            return False, "Couldn't authenticate username '{username}'  with ldap user string '{auth_string}'".format(username=username, auth_string=auth_string)
        except ldap.UNWILLING_TO_PERFORM as e:
            return False, "empty passwords are not OK or something else: " + str(e)

"""


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
