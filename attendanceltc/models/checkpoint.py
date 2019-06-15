from .shared import db
from sqlalchemy import Column, String, Integer, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Checkpoint(db.Model):
    __tablename__ = 'checkpoint'

    id = Column(Integer, primary_key=True)
    
    session_id = Column(Integer, ForeignKey('session.id'), nullable=False)
    date = Column(Date, nullable=False)

    session = relationship("Session", back_populates="checkpoints")        