import datetime
from collections import OrderedDict

from flask import Blueprint, jsonify, request, render_template, abort
from flask_login import login_required

from sqlalchemy import func

from attendanceltc.models.shared import db
from attendanceltc.models.course import Course
from attendanceltc.models.coursecomponent import CourseComponent
from attendanceltc.models.student import Student
from attendanceltc.models.enrollment import Enrollment
from attendanceltc.models.attendance import Attendance

school_course_view = Blueprint('school_course_view', __name__)


@school_course_view.route('/course/<subject>/<catalog>/', methods=["GET"])
@login_required
def view_courses(subject, catalog, name=None):

    course_count = db.session.query(Course, CourseComponent) \
        .with_entities(Course.name, CourseComponent.name, func.count(func.distinct(Student.id))) \
        .join(Student.components, Enrollment.component, CourseComponent.course) \
        .filter(Course.subject_id==subject).filter(Course.catalog_id==catalog) \
        .group_by(CourseComponent.id).order_by(CourseComponent.name).all()

    course_count_tier4 = db.session.query(Course, CourseComponent) \
        .with_entities(Course.name, CourseComponent.name, func.count(func.distinct(Student.id))) \
        .join(Student.components, Enrollment.component, CourseComponent.course) \
        .filter(Course.subject_id==subject).filter(Course.catalog_id==catalog) \
        .filter(Student.tier4) \
        .group_by(CourseComponent.id).order_by(CourseComponent.name).all()
    
    attendance_last = db.session.query(Course, CourseComponent, Attendance) \
        .with_entities(Course.name, CourseComponent.name, func.max(Attendance.date)) \
        .join(Attendance.component, CourseComponent.course) \
        .filter(Course.subject_id==subject).filter(Course.catalog_id==catalog) \
        .group_by(CourseComponent.id).order_by(CourseComponent.name).all()
    
    today = datetime.date.today()
    start_of_last_weekday = datetime.timedelta(days=today.weekday(), weeks=1)
    start_of_last_weekday = today - start_of_last_weekday

    attendance_last_week = db.session.query(Course, CourseComponent, Attendance) \
        .with_entities(Course.name, CourseComponent.name, func.max(Attendance.date)) \
        .join(Attendance.component, CourseComponent.course) \
        .filter(Course.subject_id==subject).filter(Course.catalog_id==catalog) \
        .filter(Attendance.date >= start_of_last_weekday) \
        .group_by(CourseComponent.id).order_by(CourseComponent.name).all()

    if not course_count:
        return abort(404)
    
    result = OrderedDict()

    for _, component, count in course_count:
        result[component] = [count, 0, "never", "not taken"]

    for _, component, count in course_count_tier4:
        result[component][1] = count
    
    for _, component, date in attendance_last:
        result[component][2] = date.strftime("%a, %x")
    
    for _, component, date in attendance_last_week:
        result[component][3] = date.strftime("%a, %x")

    return render_template("course_view.html", name=course_count[0][0], components=result)
