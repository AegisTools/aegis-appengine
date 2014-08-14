import logging

from google.appengine.ext import ndb
from google.appengine.api import users


log = logging.getLogger("users")


templates = { "{id}" : "view",
              "{id}/edit" : None }


def user_key(user):
    if isinstance(user, users.User):
        return ndb.Key("User", user.email())
    else:
        return ndb.Key("User", user)


def load_user(viewer, id):
    key = user_key(id)
    user = key.get()

    if not user:
        log.warn("Creating user");
        key, user = create_user(viewer, viewer)

    return {
        'id' : key.id(),
        'email' : user.user.email(),
        'created_by' : user.created_by.id(),
        'active' : user.active,
        'notes' : user.notes
        }


def load_user_list(user, ignored):
    return { 'user' : user.email() }


def create_user(user, creator):
    new_user = User(key=user_key(user))
    new_user.user = user
    new_user.created_by = user_key(creator)
    new_user.active = True
    new_user.notes = "Created automatically for testing."

    return new_user.put(), new_user


types = { 'user' : load_user,
          'user_list' : load_user_list }

class User(ndb.Model):
    user = ndb.UserProperty()
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    active = ndb.BooleanProperty()
    notes = ndb.TextProperty()
