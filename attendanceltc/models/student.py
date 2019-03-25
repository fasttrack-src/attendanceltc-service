from .shared import db
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

class Student(db.Model):
    __tablename__ = 'student'

    id = Column(String(150), primary_key=True)
    firstname = Column(String(150), nullable=False)
    lastname = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    barcode = Column(String(150), nullable=False, unique=True)
    year = Column(String(15), nullable=False)
    tier4 = Column(Boolean, default=0)

    components = relationship("Enrollment", back_populates="student")
    attendance = relationship("Attendance", back_populates="student")

    def __str__(self):
        return self.lastname + ", " + self.firstname + " (" + self.id + ")"
