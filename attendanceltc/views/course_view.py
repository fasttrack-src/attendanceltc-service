from collections import OrderedDict

from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import func

from attendanceltc.models.shared import db
from attendanceltc.models.course import Course, CourseComponent, Enrollment
from attendanceltc.models.student import Student

school_course_view = Blueprint('school_course_view', __name__)


@school_course_view.route('/course/<name>/<id>', methods=["GET"])
def view_courses(name, id):
    course_id = id
    course_name = name

    # who tutors
    tutor_name = "Adam Kurkiewicz"

    # attendance last taken
    attendance_last_taken = "2019-03-08"

    # attendance last week in percent
    attendance_percent = 66

    result = OrderedDict()
    # Create the context for the render template, keyed by
    # (course_id, course_name) and valued by [tutor_name, attendance_last_taken, attendance_percent]
    result[(course_id, course_name)] = [tutor_name,
                                        attendance_last_taken, attendance_percent]

    return render_template("course_view.html", course_details=result, course_name=course_name)
