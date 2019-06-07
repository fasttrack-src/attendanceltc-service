from .shared import db
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

class Department(db.Model):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)

    subjects = relationship("Subject", back_populates="department")
    administrative_staff = relationship("AdministrativeStaffUser", back_populates="department")

    def __str__(self):
        return self.name