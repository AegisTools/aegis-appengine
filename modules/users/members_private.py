import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

from users import build_user_key
from permissions import permission_verify
from groups import build_group_key

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *


log = logging.getLogger("members")


def members_add(actor, group_id=None, group_key=None, group=None, user_id=None, user_key=None, user=None):
    permission_verify(actor, "member", "update")

    user_key  = user_key  or build_user_key( user_id ) or user.key
    group_key = group_key or build_group_key(group_id) or group.key

    user  = user  or user_key.get()
    group = group or group_key.get()

    if not group.users:
        group.users = [ user_key ]
    else:
        users = set(group.users)
        users.add(user_key)
        group.users = users

    group.put()

    if user:
        if not user.groups:
            user.groups = [ group.key ]
        else:
            groups = set(user.groups)
            groups.add(group.key)
            user.groups = groups

        user.put()


def members_remove(actor, group_id=None, group_key=None, group=None, user_id=None, user_key=None, user=None):
    permission_verify(actor, "member", "update")

    user_key  = user_key  or build_user_key( user_id ) or user.key
    group_key = group_key or build_group_key(group_id) or group.key

    user  = user  or user_key.get()
    group = group or group_key.get()

    if group.users: group.users.remove(user_key)
    if user and user.groups: user.groups.remove(group_key)

    group.put()
    user.put()



def members_clear(actor, group_id=None, group_key=None, group=None):
    permission_verify(actor, "member", "update")

    group = group or (group_key or build_group_key(group_id)).get()
    for user_key in group.users:
        user = user_key.get()
        if user and user.groups:
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
        
        



