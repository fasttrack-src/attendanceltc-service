from .shared import db
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

class Tutor(db.Model):
    __tablename__ = 'tutor'

    id = Column(String(150), primary_key=True)
    firstname = Column(String(150), nullable=False)
    lastname = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    barcode = Column(String(150), nullable=False, unique=True)
    year = Column(String(15), nullable=False)
    tier4 = Column(Boolean, default=0)

    # TODO: update details from ldap automatically
    # TODO: make this work with course assignments
    
    enrollment = relationship("Enrollment", back_populates="student")
    attendance = relationship("Attendance", back_populates="student")

    def __str__(self):
        return self.lastname + ", " + self.firstname + " (" + self.id + ")"
