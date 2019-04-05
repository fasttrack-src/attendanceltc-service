import sys
import datetime
import requests

from attendanceltc import app
from attendanceltc.models.shared import db

from attendanceltc.models.subject import Subject
from attendanceltc.models.department import Department
from attendanceltc.models.course import Course
from attendanceltc.models.coursecomponent import CourseComponent
from attendanceltc.models.student import Student
from attendanceltc.models.enrollment import Enrollment
from attendanceltc.models.attendance import Attendance

db.init_app(app)

def create_mock_departments():
    departments = {
        "mathsstats" : Department(name="School of Mathematics and Statistics"),
        "compsci" : Department(name = "School of Computing Science")
    }

    subjects = {
        "maths" : Subject(id="MATHS", name="Mathematics", department=departments["mathsstats"]),
        "stats" : Subject(id="STATS", name="Statistics", department=departments["mathsstats"]),
        "compsci" : Subject(id="COMPSCI", name="Computing Science", department=departments["compsci"])
    }

    db.session.add_all(departments.values())
    db.session.add_all(subjects.values())

def create_mock_school():
    # Create session for cookie persistency.
    s = requests.Session()

    # Try logging in with admin credentials.
    r = s.post("http://localhost/phone-api/login", json={"guid": "admin", "password": "p"})
    print(r.text)

    # Open file and try importing.
    with open('anonymize/anonymized.csv', 'rb') as f:

        headers = {'Content-Type': 'text/csv'}
        params = {"uploadType": "MATHS_STATS_CSV_1"}
        r = s.post("http://localhost/students", data=f, headers=headers, params=params)
        print(r.text)

def create_mock_attendance():
    cc = db.session.query(CourseComponent).filter(CourseComponent.name == "LB01").filter(CourseComponent.course.has(Course.name == "Mathematics 1R")).first()
    st = db.session.query(Student).filter(Student.enrollment.any(Enrollment.component == cc)).first()
    
    att = Attendance(student=st, component=cc)
    db.session.add(att)

    today = datetime.date.today()
    start_of_last_weekday = datetime.timedelta(days=today.weekday(), weeks=1)
    start_of_last_weekday = today - start_of_last_weekday

    att2 = Attendance(student=st, component=cc, timestamp=start_of_last_weekday)
    db.session.add(att2)

with app.app_context():
    print("="*80)
    print("Running population script...")
    
    db.create_all()

    create_mock_departments()
    db.session.commit()

    create_mock_school()
    
    create_mock_attendance()
    db.session.commit()

    print("Population script run.")
    print("="*80)