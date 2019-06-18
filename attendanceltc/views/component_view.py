import datetime
import math
from collections import OrderedDict

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
from attendanceltc.models.session import Session

school_component_view = Blueprint('school_component_view', __name__)


@school_component_view.route('/component/<component>/<subject_id>/<catalog_id>', methods=["GET"])
@login_required
def view_attendance_for_component(component, subject_id, catalog_id):

    # get all students that are enrolled for that component_id
    students = db.session.query(Student).join(Enrollment, CourseComponent) \
        .filter(CourseComponent.name == component) \
        .filter(Course.subject_id == subject_id) \
        .filter(Course.catalog_id == catalog_id) \
        .filter(CourseComponent.course_id == Enrollment.coursecomponent_id) \
        .filter(Enrollment.student_id == Student.id) \
        .all()

    print("++++++++")
    print(students)
    print("++++++++")

    tier4_students = [s for s in students if s.tier4]

    attendance = db.session.query(Attendance) \
        .with_entities(Attendance.timestamp, Attendance.student_id) \
        .filter(Attendance.student_id.in_((s.id for s in students))) \
        .all()

    session = db.session.query(Session).first()
    raw_weeks, week_labels = session.get_weeks_and_labels()
    weekly_attendance_count = [0]*len(raw_weeks)

    for a in attendance:
        ts = a.timestamp
        for i in range(0, len(raw_weeks)):
            if raw_weeks[i][0] <= ts and raw_weeks[i][1] >= ts:
                weekly_attendance_count[i] += 1
                break

    # Get beginning of last weekday.
    today = datetime.date.today()
    start_of_last_weekday = datetime.timedelta(days=today.weekday(), weeks=1)
    start_of_last_weekday = today - start_of_last_weekday
    start_of_last_weekday = datetime.datetime.combine(start_of_last_weekday, datetime.time(0, 0))
    two_weeks_ago = today - datetime.timedelta(days=14)
    two_weeks_ago = datetime.datetime.combine(two_weeks_ago, datetime.time(0, 0))

    student_attendance = []
    for s in students:
        attendance_data = [a.timestamp for a in attendance if int(a.student_id) == int(s.id)]
        student_attendance.append([
            s.firstname + " " + s.lastname,
            str(len(attendance_data)) + "/" + str(len(raw_weeks)),
            has_attended(attendance_data, start_of_last_weekday),
            has_attended(attendance_data, two_weeks_ago, start_of_last_weekday)
        ])

    result = OrderedDict()
    for i in range(0, len(students)):
        result[i] = student_attendance[i]

    context = {
        "weeks": week_labels,
        "attendance_per_week": weekly_attendance_count,
        "components": result
    }

    return render_template(
        "component_view.html",
        **context
    )


def has_attended(attendance_dates, begin_week, end_week=None):
    for i in attendance_dates:
        print("---------", i)
        if i > begin_week and (not end_week or i < end_week):
            return True

    return False
