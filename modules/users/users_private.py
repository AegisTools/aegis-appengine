import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

from permissions import permission_check, permission_is_root

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *


log = logging.getLogger("users")


def create(actor, user_key=None, user_id=None, active=True, **kwargs):
    if not permission_check(actor, "user", "create") and not permission_is_root(actor):
        raise NotAllowedError()

    user_key = user_key or key(user_id)
    user = User(key=user_key)
    user.user = users.User(user_key.id())
    user.created_by = key(actor)

    return set(actor, user, active=True, **kwargs)


def update(actor, user_id=None, user_key=None, user=None, **kwargs):
    if not permission_check(actor, "user", "update") and not permission_is_root(actor):
        raise NotAllowedError()

    return set(actor, get(actor, user_id, user_key, user), **kwargs)


def deactivate(actor, user_id=None, user_key=None, user=None, **ignored):
    if not permission_check(actor, "user", "update") and not permission_is_root(actor):
        raise NotAllowedError()

    return set(get(actor, user_id, user_key, user), active=False)


def set(actor, user=None, first_name=undefined, last_name=undefined, active=undefined, 
        notes=undefined, **ignored):
    if is_defined(first_name):
        user.first_name = first_name

    if is_defined(last_name):
        user.last_name = last_name

    if is_defined(active):
        user.active = active

    if is_defined(notes):
        user.notes = notes

    user.updated_by = key(actor)
    user.put()

    return user


def get(actor, user_id=None, user_key=None, user=None, silent=False):
    if not permission_check(actor, "user", "read") and not permission_is_root(actor):
        raise NotAllowedError()

    if user:
        return user

    user_key = user_key or key(user_id)
    if user_key:
        result = user_key.get()
        if result:
            return result
    
    if silent:
        return None
    else:
        raise NotFoundError()


def list(actor):
    if not permission_check(actor, "user", "read") and not permission_is_root(actor):
        raise NotAllowedError()

    return User.query().filter(User.active == True)


def key(user):
    if not user:
        return None
    elif isinstance(user, User):
        return user.key
    elif isinstance(user, users.User):
        return ndb.Key("User", user.email())
    elif isinstance(user, ndb.Key):
        return user
    else:
        return ndb.Key("User", user)


class User(ndb.Model):
    user = ndb.UserProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    notes = ndb.TextProperty()
    active = ndb.BooleanProperty(default=True, required=True)
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated_by = ndb.KeyProperty(kind='User')
    updated = ndb.DateTimeProperty(auto_now=True)

