import io
import csv
import json

from flask import current_app as app
from flask import Blueprint, request, g
from flask_login import login_required

from sqlalchemy import func
from sqlalchemy.sql import functions
from sqlalchemy.sql.expression import Tuple

from attendanceltc.models.shared import db, get_one_or_create
from attendanceltc.models import Course, CourseComponent, Student, Enrollment, Subject, AdministrativeStaffUser, Department

from .shared import APIResponseMaker

import_db = Blueprint('import_db', __name__)

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

    try:
        db.session.commit()
    except:
        return g.resp.error("There has been an error updating the database.")

    g.resp.message("Successful import.")


@import_db.route('/students', methods=["POST"])
@login_required
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