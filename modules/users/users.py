import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

from common import *
from permissions import permission_check, permission_is_root


log = logging.getLogger("users")


def create_user(viewer, keys, data):
    if permission_check(viewer, "user", "create") or permission_is_root(viewer):
        new_user = User(key=user_key(keys["id"]))
        new_user.user = users.User(keys["id"])
        new_user.created_by = user_key(viewer)
        new_user.active = True
        new_user.put()
    else:
        log.debug("Not allowed")

    return None


def delete_user(viewer, keys, data):
    if permission_check(viewer, "user", "create") or permission_is_root(viewer):
        user_key(keys["id"]).delete()
    else:
        log.debug("Not allowed")

    return "/users"


def load_user(viewer, id):
    if permission_check(viewer, "user", "read") or permission_is_root(viewer):
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
    else:
        log.debug("Not allowed")


def load_user_list(viewer, ignored):
    if permission_check(viewer, "user", "read") or permission_is_root(viewer):
        result = []
        for user in User.query().fetch():
            result.append(user_to_model(user))
        return result


def user_to_model(user):
    return { 'user'       : user.user.email(),
             'created_by' : user.created_by.id(),
             'created'    : user.created,
             'updated'    : user.updated,
             'active'     : user.active,
             'notes'      : user.notes }


class User(ndb.Model):
    user = ndb.UserProperty()
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    active = ndb.BooleanProperty()
    notes = ndb.TextProperty()





