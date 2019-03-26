from attendanceltc import app
from attendanceltc.models.shared import db

from attendanceltc.models.subject import Subject
from attendanceltc.models.department import Department

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

with app.app_context():
    print("="*80)
    print("Running population script...")
    
    db.create_all()

    create_mock_departments()
    db.session.commit()

    print("Population script run.")
    print("="*80)