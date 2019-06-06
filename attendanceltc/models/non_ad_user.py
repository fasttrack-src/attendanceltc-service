from .shared import db
from sqlalchemy import Column, String, Boolean

class NonADUser(db.Model):
    __tablename__ = 'non_ad_user'

    username = Column(String(150), primary_key=True)
    service_account = Column(Boolean, default=0)
    admin_account = Column(Boolean, default=0)

    def __str__(self):
        return self.username