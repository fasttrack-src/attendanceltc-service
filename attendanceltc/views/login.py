import re
import ldap
import hashlib
import binascii
import urllib.parse
import json

from flask import current_app as app
from flask import Blueprint, request, abort, redirect, render_template
from flask_login import LoginManager, login_user, logout_user, login_required

from attendanceltc.models.user import User

from .shared import APIResponseMaker

from attendanceltc.models.shared import db

from attendanceltc.models.administrative_staff_user import AdministrativeStaffUser

login = Blueprint('login', __name__)

login_manager = LoginManager()
login_manager.login_view = "login.handle_login"

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
        # Check if admin user:
        #   check password, with config file, log in
        # Check if non_ad user:
        #   check password in the db, log in
        # Check if administrative staff user
        #   check in the db. If it's there, pull newest data from AD, fix up the record if necessary, log in.
        # Check if tutor in the db:
        #   pull newest data from AD, fix up the record if necessary, log in.
        # Check if student in the db:
        #   pull newest data from AD, fix up the record if necessary, log in.
        # Give up
    if username == "admin":
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(
            "utf-8"), b'attendance.gla.ac.uk', 1000)
        hashed_password = binascii.hexlify(dk).decode()
        
        if hashed_password == app.config["ADMIN_PASSWORD"]:
            return True, ""
        else:
            return False, "Invalid administrator credentials."


    elif re.match("^[a-zA-z]*$", username) and len(username) < 32:
        no_admin_users = len(list(db.session.query(AdministrativeStaffUser).filter(AdministrativeStaffUser.username == username)))

        if no_admin_users > 1:
            return False, "Internal error, too many users named {}".format(username)

        is_admin_user = no_admin_users == 1

        if is_admin_user:
            # TODO would be nice to update the database record if any changes in ldap
            return authenticate_with_ldap(username, password)
    
    return False, "Inavlid username"
        
        
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
