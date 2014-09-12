import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

from users import build_user_key
from groups import build_group_key
from permissions import permission_check, permission_is_root

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *


log = logging.getLogger("aliases")


def create(actor, alias_key=None, alias_id=None, user_id=None, user_key=None, user=None, 
           group_id=None, group_key=None, group=None, **kwargs):
    if not permission_check(actor, "alias", "create") and not permission_is_root(actor):
        raise NotAllowedError()

    user_key = user_key or build_user_key(user or user_id)
    group_key = group_key or build_group_key(group or group_id)

    if not user_key and not group_key:
        raise IllegalError("Aliases must specify either a user or a group")
    if user_key and group_key:
        raise IllegalError("Aliases must specify either a user or a group")

    alias_key = alias_key or key(alias_id)
    alias = Alias(key=alias_key)
    alias.alias = users.User(alias_key.id())
    alias.user = user_key
    alias.group = group_key
    alias.created_by = build_user_key(actor)
    alias.put()

    return alias


def delete(actor, alias_id=None, alias_key=None, alias=None, **ignored):
    if not permission_check(actor, "alias", "update") and not permission_is_root(actor):
        raise NotAllowedError()

    return get(alias_id, alias_key, alias).delete()


def get(alias_id=None, alias_key=None, alias=None):
    if not permission_check(actor, "alias", "read") and not permission_is_root(actor):
        raise NotAllowedError()

    result = alias or (alias_key or key(alias_id)).get()
    if result:
        return result
    else:
        raise NotFoundError()


def list(actor):
    if not permission_check(actor, "alias", "read") and not permission_is_root(actor):
        raise NotAllowedError()

    return Alias.query().get()


def key(alias_id):
    return ndb.Key(Alias, alias_id)


class Alias(ndb.Model):
    alias = ndb.UserProperty()
    user = ndb.KeyProperty(kind='User')
    group = ndb.KeyProperty(kind='Group')
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)


