from .shared import db
from sqlalchemy import Column, String, Integer
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class Course(db.Model):
    __tablename__ = 'course'

    __table_args__ = (UniqueConstraint('subject_id', 'catalog_id'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(String(100), ForeignKey('subject.id'), nullable=False)
    catalog_id = Column(String(150), nullable=False)
    name = Column(String(150), nullable=False)

    components = relationship("CourseComponent", back_populates="course")
    subject = relationship("Subject", back_populates="courses")

    def __str__(self):
        return self.name + " (" + self.id + ")"