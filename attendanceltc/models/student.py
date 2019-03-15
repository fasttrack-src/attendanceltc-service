from .shared import db

from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

class Enrollment(db.Model):
	__tablename__ = 'enrollment'

	__table_args__ = (
		PrimaryKeyConstraint('student_id', 'coursecomponent_id'),
	)

	student_id = db.Column(db.String(150), db.ForeignKey('student.id'))
	coursecomponent_id = db.Column(db.Integer, db.ForeignKey('coursecomponent.id'))

	student = relationship("Student", back_populates="components")
	component = relationship("CourseComponent", back_populates="students")

class Student(db.Model):
	__tablename__ = 'student'

	id = db.Column(db.String(150), primary_key=True)
	firstname = db.Column(db.String(150), nullable=False)
	lastname = db.Column(db.String(150), nullable=False)
	email = db.Column(db.String(150), nullable=False)
	barcode = db.Column(db.String(150), nullable=False, unique=True)
	year = db.Column(db.String(15), nullable=False)
	tier4 = db.Column(db.Boolean, default=0)

	components = relationship("Enrollment", back_populates="student")

	def __str__(self):
		return self.lastname + ", " + self.firstname + " (" + self.id + ")"