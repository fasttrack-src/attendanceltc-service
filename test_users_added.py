from attendanceltc import app

from attendanceltc.models.shared import db

from attendanceltc.models.user_identity import UserIdentity

def test_users():
    with app.app_context():
        db.session.query(UserIdentity).filter(UserIdentity.username == "adamk").one()

if __name__ == "__main__":
    test_users()