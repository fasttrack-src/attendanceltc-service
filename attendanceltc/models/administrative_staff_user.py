from .shared import db
from .user_identity import UserIdentity
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class AdministrativeStaffUser(UserIdentity):
    __tablename__ = 'admininstrative_staff_user'
    __mapper_args__ = {'polymorphic_identity': 'AdministrativeStaffUser'}

    username = Column(String, ForeignKey(
        'user_identity.username'), primary_key=True)
    department_id = Column(String(100), ForeignKey(
        'department.id'), nullable=False)
    department = relationship(
        "Department", back_populates="administrative_staff")

    def __str__(self):
        return self.username
