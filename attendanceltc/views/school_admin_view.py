from collections import OrderedDict

from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import func

from attendanceltc.models.shared import db
from attendanceltc.models.course import Course, CourseComponent, Enrollment
from attendanceltc.models.student import Student

school_admin_view = Blueprint('school_admin_view', __name__)


@school_admin_view.route('/', methods=["GET"])
def view_course():

    # Get student count per course
    students_count = db.session.query(Course, Student) \
        .with_entities(Course.id, Course.name, func.count(func.distinct(Student.id))) \
        .join(Student.components, Enrollment.component, CourseComponent.course) \
        .group_by(Course.id).order_by(Course.id).all()

    # Get Tier 4 student count per course
    tier4_count = db.session.query(Course, Student) \
        .with_entities(Course.id, Course.name, func.count(func.distinct(Student.id))) \
        .join(Student.components, Enrollment.component, CourseComponent.course) \
        .filter(Student.tier4).group_by(Course.id) \
        .order_by(Course.id).all()

    # Create the context for the render template, keyed by
    # (course_id, course_name) and valued by [student_count,
    # tier4_count]
    result = OrderedDict()

    # First, go through the student count query. We will assume
    # the course has no tier 4 students.
    for student in students_count:
        course_id, course_name, student_count = student

        result[(course_id, course_name)] = [student_count, 0]

    # Now, go through the tier 4 query, updating the original dictionary
    # as required.
    for student in tier4_count:
        course_id, course_name, tier4_count = student

        result[(course_id, course_name)][-1] = tier4_count

    return render_template("school_admin_view.html", courses=result)
