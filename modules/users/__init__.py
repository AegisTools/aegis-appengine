import logging

from google.appengine.ext import ndb
from google.appengine.api import users


log = logging.getLogger("users")


dependencies = ["permissions"]

templates = { "{id}"      : "view",
              "{id}/edit" : None }


def user_key(user):
    if isinstance(user, users.User):
        return ndb.Key("User", user.email())
    else:
        return ndb.Key("User", user)


class UserActions:
    @staticmethod
    def create_user(viewer, keys, data):
        new_user = User(key=user_key(keys["id"]))
        new_user.user = users.User(keys["id"])
        new_user.created_by = user_key(viewer)
        new_user.active = True
        new_user.put()

        return None

    @staticmethod
    def delete_user(viewer, keys, data):
        user_key(keys["id"]).delete()

        return "/users"


class UserLookups:
    @staticmethod
    def load_user(viewer, id):
        key = user_key(id)
        user = key.get()

        if not user:
            return None

        return { 'id' : key.id(),
                 'email' : user.user.email(),
                 'created_by' : user.created_by.id(),
                 'active' : user.active,
                 'notes' : user.notes
               }

    @staticmethod
    def load_user_list(user, ignored):
        return { 'user' : user.email() }


class User(ndb.Model):
    user = ndb.UserProperty()
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    active = ndb.BooleanProperty()
    notes = ndb.TextProperty()


types = { 'user'      : UserLookups.load_user,
          'user_list' : UserLookups.load_user_list }

actions = { "PUT"    : { "{id}" : UserActions.create_user },
            "DELETE" : { "{id}" : UserActions.delete_user } }





