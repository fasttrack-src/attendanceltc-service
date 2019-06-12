from .shared import db
from .user_identity import UserIdentity
from sqlalchemy import Column, String, Boolean, ForeignKey


class NonADUser(UserIdentity):
    __tablename__ = 'non_ad_user'
    __mapper_args__ = {'polymorphic_identity': 'NonADUser'}

    username = Column(String, ForeignKey(
        'user_identity.username'), primary_key=True)
    password = Column(String, nullable=False)
    service_account = Column(Boolean, default=0, nullable=False)
    admin_account = Column(Boolean, default=0, nullable=False)

    def __str__(self):
        return self.username
