import re
import ldap
import hashlib
import binascii
import urllib.parse

from flask import current_app as app
from flask import Blueprint, request, abort, redirect, render_template
from flask_login import LoginManager, login_user, logout_user, login_required

from attendanceltc.models.user import User

from .shared import APIResponseMaker

login = Blueprint('login', __name__)

login_manager = LoginManager()
login_manager.login_view = "login.handle_login"

def authenticate(username, password):
    # If the username is admin, we do not query the server at all.
    if username == "admin":
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(
            "utf-8"), b'attendance.gla.ac.uk', 1000)
        hashed_password = binascii.hexlify(dk).decode()
        
        if hashed_password == app.config["ADMIN_PASSWORD"]:
            return True, ""
        else:
            return False, "Invalid administrator credentials."
    
    elif re.match("^[a-zA-z]*$", username) and len(username) < 32:
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

def is_safe_url(target):
    ref_url = urllib.parse.urlparse(request.host_url)
    test_url = urllib.parse.urlparse(urllib.parse.urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc

@login_manager.user_loader
def load_user(user_id):
	print(user_id)
	return User(user_id)

@login.route('/login', methods=['GET', 'POST'])
def handle_login():
    if request.method == 'POST':
        print(request.form)
        username = request.form['username']
        password = request.form['password']

        result, error = authenticate(username, password)
        
        if not app.debug:
            error = "Wrong username or password."
        
        if not result:
                return render_template("login.html", error=error), 401
        
        user = User(username)
        login_user(user)

        n = request.args.get("next")
        
        if not is_safe_url(n):
            return abort(400)

        if not n:
            n = "/"
          
        return redirect(n)
            
    if request.method == 'GET':
        return render_template("login.html")


@login.route("/rest-login", methods=["PUT"])
def rest_login():
    login_data = json.loads(request.get_data().decode("utf-8"))
    username = login_data["username"]
    password = login_data["password"]
    auth_result, error = authenticate_with_ldap(username, password)
    if auth_result:
        l = login_user(User(username))
        return "", 200
    return "Couldn't authenticate: {error}".format(error=error), 401

@login.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")
