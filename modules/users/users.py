import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

from shared import *
from permissions import permission_check, permission_is_root

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *


log = logging.getLogger("users")


def user_http_put(actor, user_id, **kwargs):
    if "user" in kwargs:
        del kwargs["user"]

    key = user_key(user_id)
    user = key.get()
    if user:
        if permission_check(actor, "user", "update") or permission_is_root(actor):
            user_update(actor, user=user, **kwargs)
        else:
            raise NotAllowedError()
    else:
        user_http_post(actor, key=key, user_id=user_id, **kwargs)


def user_http_post(actor, **kwargs):
    if "user" in kwargs:
        del kwargs["user"]
    
    if permission_check(actor, "user", "create") or permission_is_root(actor):
        user_create(actor, **kwargs)
    else:
        raise NotAllowedError()


def user_http_delete(actor, user_id, **ignored):
    if permission_check(actor, "user", "delete") or permission_is_root(actor):
        user_deactivate(actor, user_id=user_id)
    else:
        raise NotAllowedError()


def user_create_or_update(actor, key=None, user_id=None, **kwargs):
    key = key or user_key(user_id)
    user = key.get()
    if user:
        user_update(actor, user=user, **kwargs)
    else:
        user_create(actor, key=key, **kwargs)


def user_create(actor, key=None, user_id=None, active=True, **kwargs):
    key = key or user_key(user_id)
    user = User(key=key)
    user.user = users.User(user.key.id())
    user.created_by = user_key(actor)

    return user_update(actor, user=user, active=True, **kwargs)


def user_update(actor, user_id=None, key=None, user=None,
                first_name=undefined, last_name=undefined, active=undefined, notes=undefined,
                **ignored):
    user = user or (key or user_key(user_id)).get()

    if is_defined(first_name):
        user.first_name = first_name

    if is_defined(last_name):
        user.last_name = last_name

    if is_defined(active):
        user.active = active

    if is_defined(notes):
        user.notes = notes

    user.updated_by = user_key(actor)
    user.put()

    return to_model(user)


def user_deactivate(actor, user_id=None, key=None, user=None, **ignored):
    user = user_get(user_id, key, user)
    user.updated_by = user_key(actor)
    user.active = False
    user.put()


def user_get(user_id=None, key=None, user=None):
    result = user or (key or user_key(user_id)).get()
    if result:
        return result
    else:
        raise NotFoundError()


def user_load(viewer, user_id=None, key=None):
    if permission_check(viewer, "user", "read") or permission_is_root(viewer):
        return to_model((key or user_key(user_id)).get())
    else:
        raise NotAllowedError()


def user_list(viewer):
    if permission_check(viewer, "user", "read") or permission_is_root(viewer):
        result = []
        for user in User.query().filter(User.active == True):
            result.append(to_model(user))

        return result
    else:
        raise NotAllowedError()


def user_alias_create(actor, key=None, user_id=None, alias_key=None, alias_id=None):
    alias_key = alias_key or ndb.Key("UserAlias", alias_id)
    key = key or user_key(user_id)

    alias = UserAlias(key=alias_key)
    alias.user = key
    alias.put()

    return { 'alias': alias_key.id(),
             'user':  key.id() }

def user_alias_delete(actor, alias_key=None, alias_id=None):
    alias_key = alias_key or ndb.Key("UserAlias", alias_id)
    alias_key.delete()


def to_model(user):
    if not user:
        return None

    return { 'key'          : user.key.id(),
             'first_name'   : user.first_name,
             'last_name'    : user.last_name,
             'display_name' : (user.last_name or "Unknown") + ", " + (user.first_name or "Unknown"),
             'active'       : user.active,
             'created_by'   : user.created_by.id(),
             'created'      : user.created,
             'updated_by'   : user.updated_by.id(),
             'updated'      : user.updated }


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


class UserAlias(ndb.Model):
    user = ndb.KeyProperty(kind=User)




