import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

from users import build_user_key
from permissions import permission_verify

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *


log = logging.getLogger("groups")


def create(actor, group_id=None, group_key=None, active=True, **kwargs):
    permission_verify(actor, "group", "create")

    group_key = group_key or key(group_id)
    group = Group(key=group_key)
    group.group = users.User(group_key.id())
    group.created_by = build_user_key(actor)

    return set(actor, group, active=True, **kwargs)


def update(actor, group_id=None, group_key=None, group=None, **kwargs):
    permission_verify(actor, "group", "update")
    return set(actor, get(actor, group_id, group_key, group), **kwargs)


def deactivate(actor, group_id=None, group_key=None, group=None, **ignored):
    permission_verify(actor, "group", "update")
    return set(actor, get(actor, group_id, group_key, group), active=False)


def set(actor, group, name=undefined, active=undefined, notes=undefined, **ignored):
    if is_defined(name):
        group.name = name

    if is_defined(active):
        group.active = active

    if is_defined(notes):
        group.notes = notes

    group.updated_by = build_user_key(actor)
    group.put()

    return group


def get(actor, group_id=None, group_key=None, group=None, silent=False):
    permission_verify(actor, "group", "read")

    if group:
        return group

    group_key = group_key or key(group_id)
    if group_key:
        result = group_key.get()
        if result:
            return result

    if silent:
        return None
    else:
        raise NotFoundError()


def list(actor):
    permission_verify(actor, "group", "read")
    return Group.query().filter(Group.active == True)


def key(group):
    if not group:
        return None
    elif isinstance(group, ndb.Model):
        return group.key
    elif isinstance(group, ndb.Key):
        return group
    else:
        return ndb.Key('Group', group)


class Group(ndb.Model):
    group = ndb.UserProperty()
    name = ndb.StringProperty()
    notes = ndb.TextProperty()
    users = ndb.KeyProperty(kind='User', repeated=True)
    active = ndb.BooleanProperty(default=True, required=True)
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated_by = ndb.KeyProperty(kind='User')
    updated = ndb.DateTimeProperty(auto_now=True)


