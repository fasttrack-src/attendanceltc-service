from attendanceltc import app

from attendanceltc.models.shared import db

from attendanceltc.models.administrative_staff_user import AdministrativeStaffUser

db.init_app(app)

def test_users():
    with app.app_context():
        results = db.session.query(AdministrativeStaffUser).filter(AdministrativeStaffUser.username == "adamk")
        assert len(list(results)) == 1

if __name__ == "__main__":
    test_users()