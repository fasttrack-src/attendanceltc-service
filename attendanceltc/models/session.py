from datetime import datetime, timedelta, time

from .shared import db
from sqlalchemy import Column, String, Integer, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Session(db.Model):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey('department.id'), nullable=False)
    start = Column(Date, nullable=False)
    end = Column(Date, nullable=False)

    department = relationship("Department", back_populates="sessions")
    checkpoints = relationship("Checkpoint", back_populates="session")

    """
    Gets starting days of individual weeks within a session. For example, for a month like
    the following:

         June 2019
    Su Mo Tu We Th Fr Sa
                       1
     2  3  4  5  6  7  8
     9 10 11 12 13 14 15
    16 17 18 19 20 21 22
    23 24 25 26 27 28 29
    30

    and an interval of 1 June - 30 June, we get the following dates:
        May 27, Jun 3, Jun 10, Jun 17, Jun 24.
    """
    def get_weeks(self):
        start = datetime.combine(self.start, time.min)
        end = datetime.combine(self.end, time.min) + timedelta(microseconds=-1)

        week_start = start
        week_end = start - timedelta(days=start.weekday()) + timedelta(days=7, microseconds=-1)
        weeks = [(week_start, week_end)]

        week_start = start - timedelta(days=start.weekday())
        
        while True:
            week_start = week_start + timedelta(days=7) - timedelta(days=week_start.weekday())
            week_end = week_start + timedelta(days=7, microseconds=-1)

            if week_end <= end:
                weeks.append((week_start, week_end))
            else:
                weeks.append((week_start, end))
                break

        return weeks
    
    def get_weeks_and_labels(self):
        raw_weeks = self.get_weeks()
        week_labels = []

        for i, (week_start, week_end) in enumerate(raw_weeks):
            week_no = i + 1

            start = week_start.strftime("%d %b, %Y")
            end = week_end.strftime("%d %b, %Y")

            week_labels.append(["Week {}".format(week_no), "{} - {}".format(start, end)])
        
        return raw_weeks, week_labels