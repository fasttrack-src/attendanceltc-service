from .shared import db
from sqlalchemy import Column, String, Integer
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

class CourseComponent(db.Model):
    __tablename__ = 'coursecomponent'
    __table_args__ = (UniqueConstraint("name", "course_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    course_id = Column(String(100), ForeignKey('course.id'), nullable=False)

    students = relationship("Enrollment", back_populates="component")
    attendance = relationship("Attendance", back_populates="component")
    course = relationship("Course", back_populates="components")

    def __str__(self):
        return "{} ({})".format(self.name, self.course.name)