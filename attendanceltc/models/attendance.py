import datetime

from .shared import db
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class Attendance(db.Model):
    __tablename__ = 'attendance'
    __table_args__ = (UniqueConstraint('student_id', 'coursecomponent_id', 'timestamp'), )
    
    id = Column(Integer, primary_key=True, auto_increment=True)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    coursecomponent_id = Column(Integer, ForeignKey('coursecomponent.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now, nullable=False)

    student = relationship("Student", back_populates="attendance")
    component = relationship("CourseComponent", back_populates="attendance")

    def __str__(self):
        return "(Attendance of {} for component {}, recorded at {})".format(self.student, self.component, self.date)
    
    def __repr__(self):
        return "<Attendance {}, {}, {}>".format(self.student, self.component, self.date)

