from .shared import db
from .user_identity import UserIdentity
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Tutor(UserIdentity):
    __tablename__ = 'tutor'
    __mapper_args__ = {'polymorphic_identity': 'Tutor'}

    username = Column(String, ForeignKey(
        'user_identity.username'), primary_key=True)
    firstname = Column(String(150), nullable=False)
    lastname = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    
    # TODO: update details from ldap automatically
    # TODO: make this work with course assignments
    # TODO: this relationship is fucked, attendance can be captured by all identities.
    # we need some relationship across user_identity somehow, look at sqlalchemy docs for that
    #attendance = relationship("Attendance", back_populates="student")

    def __str__(self):
        return self.lastname + ", " + self.firstname + " (" + self.username + ")"
