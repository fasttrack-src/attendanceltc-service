from .shared import db
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

from .student import Student, Enrollment


class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    components = relationship("CourseComponent", back_populates="course")

    def __str__(self):
        return self.name + " (" + self.id + ")"


class CourseComponent(db.Model):
    __tablename__ = 'coursecomponent'
    __table_args__ = (UniqueConstraint("name", "course_id"),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    course_id = db.Column(db.String(100), ForeignKey('course.id'))

    students = relationship("Enrollment", back_populates="component")
    course = relationship("Course", back_populates="components")

    def __str__(self):
        return self.course.name + " - " + self.name

    def __repr__(self):
        return "<CourseComponent " + self.course.id + " " + self.name + ">"
