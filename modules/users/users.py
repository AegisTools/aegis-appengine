import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

from shared import *
from permissions import permission_check, permission_is_root

log = logging.getLogger("users")


def create_user(viewer, user, active=None, notes=None, **ignored):
    if permission_check(viewer, "user", "create") or permission_is_root(viewer):
        user_obj = user_key(user).get()
        if not user_obj:
            user_obj = User(key=user_key(user))
            user_obj.user = users.User(user)
            user_obj.created_by = user_key(viewer)
        if active:
            user_obj.active = active
        if notes:
            user_obj.notes = notes
        user_obj.put()
    else:
        log.debug("Not allowed")

    return None


def delete_user(viewer, user, **ignored):
    if permission_check(viewer, "user", "create") or permission_is_root(viewer):
        user = user_key(user).get()
        if user:
            user.active = False
            user.put()
        else:
            log.debug("User not found")
    else:
        log.debug("Not allowed")

    return "/users"


def load_user(viewer, id):
    if permission_check(viewer, "user", "read") or permission_is_root(viewer):
        return user_to_model(user_key(id).get())
    else:
        log.debug("Not allowed")


def load_user_list(viewer, ignored):
    if permission_check(viewer, "user", "read") or permission_is_root(viewer):
        result = []
        for user in User.query(User.active == True).fetch():
            result.append(user_to_model(user))
        return result


def user_to_model(user):
    if not user:
        return None

    return { 'user'       : user.user.email(),
             'created_by' : user.created_by.id(),
             'created'    : user.created,
             'updated'    : user.updated,
             'active'     : user.active,
             'notes'      : user.notes }


class User(ndb.Model):
    user = ndb.UserProperty(required=True)
    created_by = ndb.KeyProperty(kind='User', required=True)
    created = ndb.DateTimeProperty(auto_now_add=True, required=True)
    updated = ndb.DateTimeProperty(auto_now=True, required=True)
    notes = ndb.TextProperty()
    active = ndb.BooleanProperty(default=True, required=True)





