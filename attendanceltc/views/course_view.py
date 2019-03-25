from collections import OrderedDict

from flask import Blueprint, jsonify, request, render_template, abort
from sqlalchemy import func

from attendanceltc.models.shared import db
from attendanceltc.models.course import Course
from attendanceltc.models.coursecomponent import CourseComponent
from attendanceltc.models.student import Student
from attendanceltc.models.enrollment import Enrollment

school_course_view = Blueprint('school_course_view', __name__)


@school_course_view.route('/course/<subject>/<catalog>/', methods=["GET"])
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

    if not course_count:
        return abort(404)
    
    result = OrderedDict()

    for _, component, count in course_count:
        result[component] = [count, 0]

    for _, component, count in course_count_tier4:
        result[component][-1] = count
    
    return render_template("course_view.html", name=course_count[0][0], components=result)
