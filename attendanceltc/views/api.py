from flask import Blueprint, jsonify, request
import io
import csv
import time

from attendanceltc.models.shared import db
from attendanceltc.models.course import Course, CourseComponent, Enrollment
from attendanceltc.models.student import Student

api = Blueprint('api', __name__)

def add_student(row):
	uid = row["ID"]
	firstname = row["First Name"]
	lastname = row["Last"]
	year = row["Year"]

	# TODO: change these values when feed updates
	email = uid + lastname[0].capitalize() + "@student.gla.ac.uk"
	
	barcode = row["Barcode"]
	tier4 = (row["CAS Number"] != "")

	student = Student(id=uid, firstname=firstname, lastname=lastname,
		year=year, email=email, barcode=barcode, tier4=tier4)
	db.session.add(student)

	return student

def add_course(courseid, name):
	course = Course(id=courseid, name=name)
	db.session.add(course)

	return course

def add_course_component(course, component):
	component = CourseComponent(name=component, course=course)
	db.session.add(component)

	return component

def add_student_course_enrollment(student, component):
	e = Enrollment()
	e.component = component
	student.components.append(e)

def import_mycampus_feed():
	try:
		students = request.get_data().decode("utf-8")
	except:
		return 400, {"message": "Request must contain a valid UTF-8 encoded CSV file."}

	buf = io.StringIO(students)
	reader = csv.DictReader(buf)
	
	students = {}
	courses = {}
	components = {}
	student_enrollment = set()

	for row in reader:
		guid = row["ID"]

		courseid = row["Subject"] + row["Catalog"]
		coursename = row["Long Title"]

		component = row["Component"]
		compid = row["Lecture"]

		if courseid not in courses:
			course = add_course(courseid, coursename)
			courses[courseid] = course

		if component != "LEC" and (courseid, compid) not in components:
			component = add_course_component(courses[courseid], compid)
			components[(courseid, compid)] = component
		
		if guid not in students:
			student = add_student(row)
			students[guid] = student

		if component != "LEC" and (guid, courseid, compid) not in student_enrollment:
			student = students[guid]
			component = components[(courseid, compid)]

			add_student_course_enrollment(student, component)

			student_enrollment.add((guid, courseid, compid))

	try:
		db.session.commit()
	except:
		return 400, {"message": "There has been an error importing the data."}

	print(students)
	
	obj = {"message": "Import successful.", "data": {
		"students": len(students), "courses": len(courses),
		"course_components": len(components),
		"enrollments": len(student_enrollment)
	}}

	return 200, obj

@api.route('/students', methods=["POST"])
def add_students():
	method = request.args.get('uploadType')

	if method == "bulk" and request.mimetype == "text/csv":
		status, message = import_mycampus_feed()
		return jsonify(message), status

	return jsonify({"message": "Invalid request."}), 400

@api.route('/test', methods=["GET"])
def benchmark():
	q = db.session.query(Student).with_entities(Student.firstname, Student.lastname).join(Student.components, Enrollment.component, CourseComponent.course).filter(Course.name == "MATHEMATICS 2P: GRAPHS AND NETWORKS").all()
	return jsonify(q), 200