from collections import OrderedDict

from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import func

from attendanceltc.models.shared import db
from attendanceltc.models.course import Course, CourseComponent, Enrollment
from attendanceltc.models.student import Student

school_admin_view = Blueprint('school_admin_view', __name__)

@school_admin_view.route('/', methods=["GET"])
def view_course():
	
	students = db.session.query(Course, Student) \
			.with_entities(Course.id, Course.name, func.count(Student.id)) \
			.join(Student.components, Enrollment.component, CourseComponent.course) \
			.group_by(Course.id).order_by(Course.id).all()

	tier4_students = db.session.query(Course, Student) \
			.with_entities(Course.id, Course.name, func.count(Student.id)) \
			.join(Student.components, Enrollment.component, CourseComponent.course) \
			.filter(Student.tier4).group_by(Course.id) \
			.order_by(Course.id).all()

	result = OrderedDict()

	for student in students:
		courseid = student[0]
		coursename = student[1]
		no_students = student[2]

		result[(courseid, coursename)] = [no_students, 0]

	for student in tier4_students:
		courseid = student[0]
		coursename = student[1]
		no_tier4 = student[2]

		result[(courseid, coursename)][1] = no_tier4

	print(result)

	return render_template("course_view.html", courses=result)