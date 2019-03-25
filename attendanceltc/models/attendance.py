import datetime

from .shared import db
from sqlalchemy import Column, String, Integer, Date
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class Attendance(db.Model):
    __tablename__ = 'attendance'
    __table_args__ = (UniqueConstraint('student_id', 'coursecomponent_id' 'date'), )
    
    id = Column(Integer, primary_key=True, auto_increment=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    coursecomponent_id = Column(Integer, ForeignKey('coursecomponent.id'), nullable=False)
    date = Column(Date, default=datetime.datetime.now)

    student = relationship("Student", back_populates="components")
    component = relationship("CourseComponent", back_populates="students")