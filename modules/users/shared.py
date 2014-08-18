from google.appengine.ext import ndb
from google.appengine.api import users


def user_key(user):
    if isinstance(user, users.User):
        return ndb.Key("User", user.email())
    else:
        return ndb.Key("User", user)


