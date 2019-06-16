import re
import ldap
import hashlib
import binascii
import urllib.parse
import json

from flask import current_app as app
from flask import Blueprint, request, abort, redirect, render_template
from flask_login import LoginManager, login_user, logout_user, login_required

from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from attendanceltc.models import db, User

from .shared import APIResponseMaker

login = Blueprint('login', __name__)

login_manager = LoginManager()
login_manager.login_view = "login.handle_login"

def hash_password(password):
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(
            "utf-8"), b'attendance.gla.ac.uk', 1000)
        hashed_password = binascii.hexlify(dk).decode()

        return hashed_password

def authenticate_with_ldap(username, password):
    try:
        auth_string = app.config["LDAP_USER_STRING"].format(
            username=username)
        l = ldap.initialize(app.config["LDAP_URL"])
        l.simple_bind_s(auth_string, password)
        return True, ""
    except ldap.SERVER_DOWN as e:
        return False, "Could not reach LDAP server: {}".format(e)
    except ldap.INVALID_CREDENTIALS:
        return False, "Couldn't authenticate username '{username}' with ldap user string '{auth_string}'.".format(username=username, auth_string=auth_string)
    except ldap.UNWILLING_TO_PERFORM as e:
        return False, "Empty password provided or other error {}".format(e)

def authenticate(username, password):

    # For polymorphism to work, we must import all possible polymorphic variants of UserIdentity.
    # This is so that the mapper can update and we can resolve individual instances from the query.
    from attendanceltc.models.user_identity import UserIdentity
    from attendanceltc.models.administrative_staff_user import AdministrativeStaffUser
    from attendanceltc.models.non_ad_user import NonADUser
    from attendanceltc.models.tutor import Tutor
    
    # First, we assert that the username must be alphanumeric and less than 32 characters.
    if not re.match("^[a-zA-Z0-9]*$", username) and len(username) < 32:
        return False, "Invalid username format (must be alphanumeric characters only and at most 31 chars)."
    
    # Debug account, we need to check against our config to see if the password matches.
    if username == "admin":
        password = hash_password(password)
        
        if password == app.config["ADMIN_PASSWORD"]:
            return True, ""
        else:
            return False, "Invalid debug account credentials."
    
    # Try fetching an identity with the correct username. If there are too many, this is definitely an error
    # and it should be reported. If there are none, we can try just authenticating with LDAP and assign
    # the least amount of permission (i.e. student) if it succeeds.
    try:
        identity = db.session.query(UserIdentity).filter(UserIdentity.username == username).one()
    except MultipleResultsFound:
        return False, "There are more than one users named {}".format(username)
    except NoResultFound:

        success, _ = authenticate_with_ldap(username, password)

        if success:
            return True, ""
        else:
            return False, "No user named {}".format(username)

    # If the identity has a password component, we will hash the password given and match it up to the password
    # stored in the database. If not, we will authenticate with LDAP, fix the record, and log in.
    if hasattr(identity, "password"):
        password = hash_password(password)

        if identity.password == password:
            return identity, ""
        else:
            return False, "Invalid password given for username {}".format(username)
    else:
        # TODO: would be nice to update the database record if any changes to ldap
        success, message = authenticate_with_ldap(username, password)

        if success:
            return identity, ""
        else:
            return success, message
    
    return False, "Unspecified error"
        
        
def is_safe_url(target):
    ref_url = urllib.parse.urlparse(request.host_url)
    test_url = urllib.parse.urlparse(urllib.parse.urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc

@login_manager.user_loader
def load_user(user_id):
	return User(user_id)

@login.route('/login', methods=['GET', 'POST'])
def handle_login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']

        user = User(username)

        result, error = authenticate(username, password)
        
        # If we are running in production, we will mask the error message
        # presented to the user for security.
        if not app.debug:
            error = "Wrong username or password."
        
        if not result:
            return render_template("login.html", error=error), 401
        
        login_user(user)

        n = request.args.get("next")
        
        if not is_safe_url(n):
            return abort(400)

        if not n:
            n = "/"
          
        return redirect(n)
            
    if request.method == 'GET':
        return render_template("login.html")

@login.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")
