import os
from datetime import timedelta

__basedir__ = os.path.abspath(os.path.dirname(__file__))

PROJECT_NAME = 'attendanceltc'

# Environment
ENV = 'development'
TESTING = True
DEBUG = True

# database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(__basedir__, '%s.sqlite'%
                                                      PROJECT_NAME)
SQLALCHEMY_ECHO = False

# security
CSRF_ENABLED = True
SECRET_KEY = os.urandom(24)
LOGGER_NAME = "%s_log" % PROJECT_NAME
PERMANENT_SESSION_LIFETIME = timedelta(days=1)

SEND_FILE_MAX_AGE_DEFAULT = 0

ADMIN_PASSWORD = "05a58397e0acdcc134046c673b3f074c20af49d71c79b350dd8764771122c7b2"

LDAP_URL = "ldap://localhost"
LDAP_USER_STRING = "uid={username},ou=PeopleOU,dc=ad,dc=dcs,dc=gla,dc=ac,dc=uk"
LDAP_PERSON_BASE = "ou=PeopleOU,dc=ad,dc=dcs,dc=gla,dc=ac,dc=uk"