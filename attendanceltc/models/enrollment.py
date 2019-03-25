from .shared import db
from sqlalchemy import Column, String, Integer
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    __table_args__ = (UniqueConstraint('student_id', 'coursecomponent_id'),)
    
    id = Column(Integer, primary_key=True, auto_increment=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    coursecomponent_id = Column(Integer, ForeignKey('coursecomponent.id'), nullable=False)

    student = relationship("Student", back_populates="components")
    component = relationship("CourseComponent", back_populates="students")