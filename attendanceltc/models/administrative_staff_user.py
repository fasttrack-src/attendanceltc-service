from .shared import db
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class AdministrativeStaffUser(db.Model):
    __tablename__ = 'admininstrative_staff_user'
    username = Column(String(150), primary_key=True)
    department_id = Column(String(100), ForeignKey('department.id'), nullable=False)
    department = relationship("Department", back_populates="administrative_staff")

    def __str__(self):
        return self.username