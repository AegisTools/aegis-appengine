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


log = logging.getLogger("members")


def members_add(actor, group_id=None, group_key=None, group=None, user_id=None, user_key=None, user=None):
    if not permission_check(actor, "member", "update") and not permission_is_root(actor):
        raise NotAllowedError()

    group = group or (group_key or build_group_key(group_id)).get()
    user  = user  or (user_key  or build_user_key( user_id )).get()

    group.users.append(user.key)
    user.groups.append(group.key)

    group.put()
    user.put()


def members_remove(actor, group_id=None, group_key=None, group=None, user_id=None, user_key=None, user=None):
    if not permission_check(actor, "member", "update") and not permission_is_root(actor):
        raise NotAllowedError()

    group = group or (group_key or build_group_key(group_id)).get()
    user  = user  or (user_key  or build_user_key( user_id )).get()

    group.users.remove(user.key)
    user.groups.remove(group.key)

    group.put()
    user.put()



def members_clear(actor, group_id=None, group_key=None, group=None):
    if not permission_check(actor, "member", "update") and not permission_is_root(actor):
        raise NotAllowedError()

    group = group or (group_key or build_group_key(group_id)).get()
    for user_key in group.users:
        user = user_key.get()
        user.groups.remove(group.key)
        user.put()

    group.users = []
    group.put()


def members_user_list(actor, group_id=None, group_key=None, group=None):
    group = group or (group_key or build_group_key(group_id)).get()
    return [key.get() for key in group.users]


def members_group_list(actor, user_id=None, user_key=None, user=None):
    user = user or (user_key or build_user_key(user_id)).get()
    return [key.get() for key in user.users]
        
        



