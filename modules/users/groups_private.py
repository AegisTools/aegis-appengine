import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

from users import build_user_key
from permissions import permission_check, permission_is_root

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *


log = logging.getLogger("groups")


def create(actor, group_key=None, group_id=None, active=True, **kwargs):
    if not permission_check(actor, "group", "create") and not permission_is_root(actor):
        raise NotAllowedError()

    group_key = group_key or key(group_id)
    group = Group(key=group_key)
    group.group = users.User(group_key.id())
    group.created_by = user_key(actor)

    return set(actor, group, active=True, **kwargs)


def update(actor, group_id=None, group_key=None, group=None,
                first_name=undefined, last_name=undefined, active=undefined, notes=undefined,
                **ignored):
    if not permission_check(actor, "group", "update") and not permission_is_root(actor):
        raise NotAllowedError()

    return set(actor, get(actor, group_id, group_key, group), **kwargs)


def deactivate(actor, group_id=None, group_key=None, group=None, **ignored):
    if not permission_check(actor, "group", "update") and not permission_is_root(actor):
        raise NotAllowedError()

    return set(get(actor, group_id, group_key, group), active=False)


def set(actor, group=None, name=undefined, active=undefined, notes=undefined, **ignored):
    if is_defined(name):
        group.name = name

    if is_defined(active):
        group.active = active

    if is_defined(notes):
        group.notes = notes

    group.updated_by = user_key(actor)
    group.put()

    return group


def get(actor, group_id=None, group_key=None, group=None, silent=False):
    if not permission_check(actor, "group", "read") and not permission_is_root(actor):
        raise NotAllowedError()

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
    if not permission_check(actor, "group", "read") and not permission_is_root(actor):
        raise NotAllowedError()

    return Group.query().filter(Group.active == True)


def key(group):
    if not group:
        return None
    elif isinstance(group, Group):
        return ndb.Key('Group', group.key)
    elif isinstance(group, ndb.Key):
        return group
    else:
        return ndb.Key('Group', group)


class Group(ndb.Model):
    group = ndb.UserProperty()
    name = ndb.StringProperty()
    notes = ndb.TextProperty()
    active = ndb.BooleanProperty(default=True, required=True)
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated_by = ndb.KeyProperty(kind='User')
    updated = ndb.DateTimeProperty(auto_now=True)


