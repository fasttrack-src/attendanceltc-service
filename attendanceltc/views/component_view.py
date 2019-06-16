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

    tier4_students = [s for s in students if s.tier4]

    attendance = db.session.query(Attendance) \
        .with_entities(Attendance.timestamp) \
        .filter(Attendance.student_id.in_((s.id for s in students))) \
        .all()

    session = db.session.query(Session).first()
    raw_weeks, week_labels = session.get_weeks_and_labels()
    weekly_attendance_count = [0]*len(raw_weeks)

    for a in attendance:
        ts = a.timestamp
        print("&&&", ts)
        for i in range(0, len(raw_weeks)):
            if raw_weeks[i][0] <= ts and raw_weeks[i][1] >= ts:
                weekly_attendance_count[i] += 1
                print(ts, "yes", raw_weeks[i][0], raw_weeks[i][1])
                break

    print(weekly_attendance_count)


    return render_template("component_view.html", weeks=week_labels, attendance_per_week=weekly_attendance_count)
