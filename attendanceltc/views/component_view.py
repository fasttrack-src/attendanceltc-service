from flask import Blueprint, jsonify, request, render_template, abort
from flask_login import login_required

from sqlalchemy import func

from attendanceltc.models.shared import db
from attendanceltc.models.subject import Subject
from attendanceltc.models.department import Department
from attendanceltc.models.course import Course
from attendanceltc.models.coursecomponent import CourseComponent
from attendanceltc.models.student import Student
from attendanceltc.models.enrollment import Enrollment
from attendanceltc.models.attendance import Attendance

school_component_view = Blueprint('school_component_view', __name__)

@school_component_view.route('/<component>/<subject_id>/<catalog_id>', methods=["GET"])
@login_required
def view_attendance_for_component(component, subject_id, catalog_id):

    students = db.session.query(Student).join(Enrollment, CourseComponent) \
        .filter(CourseComponent.name == component) \
        .filter(Course.subject_id == subject_id) \
        .filter(Course.catalog_id == catalog_id) \
        .filter(CourseComponent.course_id == Enrollment.coursecomponent_id) \
        .filter(Enrollment.student_id == Student.id) \
        .all()

    print(students)
    print(len(students))

    # get the number of all students that are enrolled for that component_id
    
    # get the same number for tier 4

    return "Iva was here and changed the component name"
