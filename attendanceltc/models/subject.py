from .shared import db
from sqlalchemy import Column, String, Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Subject(db.Model):
    __tablename__ = 'subject'

    id = Column(String(150), primary_key=True)
    name = Column(String(150), nullable=False)
    department_id = Column(Integer, ForeignKey('department.id'), nullable=False)

    department = relationship("Department", back_populates="subjects")
    courses = relationship("Course", back_populates="subject")

    def __str__(self):
        return self.name + " (" + self.id + ")"