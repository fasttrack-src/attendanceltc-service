import sys
import time
import datetime
import requests
import os
import os.path


class PopulationScript:
    def check_database_exists():
        if not os.path.isfile("attendanceltc.sqlite"):
            return True

        print("An SQLite database already exists in this project.")
        print("For the population script to run, the SQLite")
        print("database needs to be in a clean state, otherwise data may be lost or")
        print("an exception may be thrown. Choose among the following:")
        print("")
        print(
            "[d]elete the current database, create a clean database and run the script")
        print(
            "[b]ackup the current database, create a clean database and run the script")
        print('[k]eep the current database and run the population script')
        print("select one of these options (d/B/k), ctrl+c to quit:")

        try:
            option = input("> ")
        except KeyboardInterrupt:
            print("\nQuitting....")
            return False

        if option == "d" or option == "delete":
            try:
                os.remove("./attendanceltc.sqlite")
            except:
                return False

            return True
        elif option == "k" or option == "keep":
            return True
        else:
            path = "./attendanceltc-{}.sqlite.bk".format(int(time.time()))
            print("Backing up old database as", path)

            try:
                os.rename("./attendanceltc.sqlite", path)
            except:
                print("Could not back up file.")
                return False

            return True

    def create_database(self):
        import attendanceltc.models

        self.db.create_all()

        print("Created database with all relevant models.")

    def create_departments(self):
        from attendanceltc.models.department import Department

        self.departments = {
            "mathsstats": Department(name="School of Mathematics and Statistics"),
            "compsci": Department(name="School of Computing Science")
        }

        print("Created", len(self.departments),
              "mock departments, adding to database session...")
        self.db.session.add_all(self.departments.values())
        self.db.session.commit()

    def create_sessions(self):
        from attendanceltc.models.session import Session
        from attendanceltc.models.checkpoint import Checkpoint

        self.sessions = {
            "summer": Session(name="Summer School 2018-2019",
                              department=self.departments["mathsstats"],
                              start=datetime.datetime(2019, 6, 1),
                              end=datetime.datetime(2019, 8, 31))
        }

        self.checkpoints = {
            "june": Checkpoint(session=self.sessions["summer"], date=datetime.datetime(2019, 7, 1)),
            "july": Checkpoint(session=self.sessions["summer"], date=datetime.datetime(2019, 8, 1))
        }

        print("Created sample session and checkpoints, adding to database...")

        self.db.session.add_all(self.sessions.values())
        self.db.session.add_all(self.checkpoints.values())
        self.db.session.commit()


    def create_subjects(self):
        from attendanceltc.models.subject import Subject

        self.subjects = {
            "maths": Subject(id="MATHS", name="Mathematics", department=self.departments["mathsstats"]),
            "stats": Subject(id="STATS", name="Statistics", department=self.departments["mathsstats"]),
            "compsci": Subject(id="COMPSCI", name="Computing Science", department=self.departments["compsci"])
        }

        print("Created", len(self.subjects),
              "mock subjects, adding to database session...")
        self.db.session.add_all(self.subjects.values())
        self.db.session.commit()

    def create_users(self):
        from attendanceltc.models.administrative_staff_user import AdministrativeStaffUser
        from attendanceltc.models.non_ad_user import NonADUser
        from attendanceltc.models.tutor import Tutor

        DEFAULT_PASSWORD = "05a58397e0acdcc134046c673b3f074c20af49d71c79b350dd8764771122c7b2"

        self.users = {
            "adminstaff": AdministrativeStaffUser(username="adminstaff", department=self.departments["mathsstats"]),
            "adminaccount": NonADUser(username="adminaccount", password=DEFAULT_PASSWORD, admin_account=True),
            "serviceaccount": NonADUser(username="serviceaccount", password=DEFAULT_PASSWORD, service_account=True),
            "tutor": Tutor(username="adamk", firstname="Adam", lastname="Kurkiewicz", email="adam.kurkiewicz@research.gla.ac.uk")
        }

        print("Created", len(self.users),
              "mock users, adding to database session...")
        self.db.session.add_all(self.users.values())
        self.db.session.commit()

    def populate_with_anonymized(self):
        from attendanceltc.views.import_db import import_mycampus_feed
        from attendanceltc.views.shared import APIResponseMaker

        print("Importing anonymized MyCampus data, this may take a while...")

        with open('anonymize/anonymized-short.csv', 'rb') as f, self.app.test_request_context('/student', data=f) as c:
            c.g.resp = APIResponseMaker()
            import_mycampus_feed()

        print("MyCampus data imported.")

    def create_attendance(self):
        from attendanceltc.models.user_identity import UserIdentity
        from attendanceltc.models.course import Course
        from attendanceltc.models.coursecomponent import CourseComponent
        from attendanceltc.models.student import Student
        from attendanceltc.models.enrollment import Enrollment
        from attendanceltc.models.attendance import Attendance

        cc = self.db.session.query(CourseComponent).filter(CourseComponent.name == "LB01").filter(
            CourseComponent.course.has(Course.name == "Mathematics 1R")).first()
        st = self.db.session.query(Student).filter(
            Student.enrollment.any(Enrollment.component == cc)).first()

        t = self.users["tutor"]

        print("Adding attendance to student", st,
              "for course component", cc, " marked by user", t)

        att = Attendance(student=st, component=cc, marker=t)
        self.db.session.add(att)

        today = datetime.date.today()
        start_of_last_weekday = datetime.timedelta(
            days=today.weekday(), weeks=1)
        start_of_last_weekday = today - start_of_last_weekday

        att = Attendance(student=st, component=cc, marker=t,
                         timestamp=start_of_last_weekday)
        self.db.session.add(att)

        print("Attendance data added, committing to database...")
        self.db.session.commit()

    def __init__(self):
        res = PopulationScript.check_database_exists()

        if not res:
            return

        # Now do the basic app imports
        from attendanceltc import app
        from attendanceltc.models import db

        self.db = db
        self.app = app

        with self.app.app_context():
            print("="*80)

            self.create_database()
            self.create_departments()
            self.create_sessions()
            self.create_subjects()
            self.create_users()
            self.populate_with_anonymized()
            self.create_attendance()

            print("="*80)


p = PopulationScript()
