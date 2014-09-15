import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *

log = logging.getLogger("permissions")


def permission_key(user, type, action, key=None):
    if not type:
        type = key.kind()

    type_key = ndb.Key("Permission_Type", type, parent=build_user_key(user))
    if key:
        return ndb.Key("Permission", key.urlsafe(), 
                       parent=ndb.Key("Permission_Action", action, parent=type_key))
    else:
        return ndb.Key("Permission", action, parent=type_key)


def permission_verify(user, *permission_sets, **kwargs):
    root_ok = not "root_ok" in kwargs or kwargs["root_ok"]

    for permission_set in permission_sets:
        if len(permission_set) == 2:
            permission_set = permission_set + (None,)

        type, action, key = permission_set
        if permission_key(user, *permission_set).get():
            return

        if permission_set[2] and permission_key(user *permission_set[:2]).get():
            return

    if root_ok and permission_is_root(user):
        return

    log.error("Permission denied.  Requires one of %s", permission_sets)
    raise NotAllowedError()


def permission_check(user, type, action, key=None):
    if not type:
        type = key.kind()

    result = permission_key(user, type, action, key).get()

    key_str = ""
    if key: key_str = ":" + key.urlsafe()

    if result:
        log.debug("Permission: %s %s%s (%s) - Allowed" % (user, type, key_str, action))
    else:
        log.debug("Permission: %s %s%s (%s) - Not Allowed" % (user, type, key_str, action))
        if key:
            return permission_check(user, type, action, key.parent())

    return result


def permission_is_root(user):
    if user.email() == "cron":
        return True
    if users.is_current_user_admin():
        return True
    if permission_check(user, "root", "root"):
        return True
    else:
        return False


def permission_grant(viewer, user, type, action, target=None):
    if permission_check(viewer, "permissions", "grant") or permission_is_root(viewer):
        if not permission_key(user, type, action, target).get():
            permission = Permission(key=permission_key(user, type, action, target))
            permission.user = build_user_key(user)
            permission.type = type or target.kind()
            permission.action = action
            permission.target = target
            permission.granted_by = build_user_key(viewer)
            permission.put()

            log.debug("Permission granted")
        else:
            log.warn("Permission already granted")
    else:
        raise NotAllowedError()


def permission_revoke(viewer, user, type, action, target=None):
    if permission_check(viewer, "permissions", "revoke") or permission_is_root(viewer):
        permission_key(user, type, action, target).delete()
        log.debug("Permission revoked")
    else:
        log.debug("Not allowed")


def permission_list(viewer, user):
    if permission_check(viewer, "permissions", "view") or permission_is_root(viewer):
        result = []
        for permission in Permission.query(ancestor=build_user_key(user)).fetch():
            result.append({ 'user'   : permission.user.email(),
                            'type'   : permission.type,
                            'id'     : permission.id,
                            'action' : permission.action })
        return result


class Permission(ndb.Model):
    user = ndb.KeyProperty(kind='User')
    type = ndb.StringProperty()
    action = ndb.StringProperty()
    target = ndb.KeyProperty()
    granted = ndb.DateTimeProperty(auto_now_add=True)
    granted_by = ndb.KeyProperty(kind='User')


from users import build_user_key

