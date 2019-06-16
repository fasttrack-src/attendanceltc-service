from collections import OrderedDict
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required

from sqlalchemy import func

from attendanceltc.models import db, Course, CourseComponent, Subject, Student, Enrollment, Session, Attendance, Department

school_admin_view = Blueprint('school_admin_view', __name__)


@school_admin_view.route('/', methods=["GET"])
@login_required
def view_course():

    # Get current session
    # TODO: make this work properly with the department and current date and stuff
    session = db.session.query(Session).first()
    raw_weeks, week_labels = session.get_weeks_and_labels()
    attendance_per_week = []
    now = datetime.now()

    for week_start, week_end in raw_weeks:
        print(week_start, week_end)
        if week_start > now:
            break
        
        attendance_count, = db.session.query(Attendance) \
            .with_entities(func.count(Attendance.id)) \
            .join(Attendance.component, CourseComponent.course, Course.subject, Subject.department) \
            .filter(Department.name == "School of Mathematics and Statistics") \
            .filter(week_start <= Attendance.timestamp) \
            .filter(Attendance.timestamp <= week_end) \
            .one()

        attendance_per_week.append(attendance_count)
        
    # Get student count per course
    students_count = db.session.query(Course, Student) \
        .with_entities(Course.subject_id, Course.catalog_id, Course.name, func.count(func.distinct(Student.id))) \
        .join(Student.enrollment, Enrollment.component, CourseComponent.course) \
        .group_by(Course.id).order_by(Course.id).all()

    # Get Tier 4 student count per course
    tier4_count = db.session.query(Course, Student) \
        .with_entities(Course.subject_id, Course.catalog_id, Course.name, func.count(func.distinct(Student.id))) \
        .join(Student.enrollment, Enrollment.component, CourseComponent.course) \
        .filter(Student.tier4).group_by(Course.id) \
        .order_by(Course.id).all()

    # Create the context for the render template, keyed by
    # (course_id, course_name) and valued by [student_count,
    # tier4_count]
    result = OrderedDict()

    # First, go through the student count query. We will assume
    # the course has no tier 4 students.
    for student in students_count:
        subject_id, catalog_id, course_name, student_count = student

        result[(subject_id, catalog_id, course_name)] = [student_count, 0]

    # Now, go through the tier 4 query, updating the original dictionary
    # as required.
    for student in tier4_count:
        subject_id, catalog_id, course_name, tier4_count = student

        result[(subject_id, catalog_id, course_name)][-1] = tier4_count

    return render_template("school_admin_view.html", courses=result, weeks=week_labels, attendance_per_week=attendance_per_week)
