import sys
import os
import logging

from google.appengine.ext import ndb

from common import *


log = logging.getLogger("permissions")


def permission_key(user, type, action, id=None):
    type_key = ndb.Key("Permission_Type", type, parent=user_key(user))
    key = ndb.Key("Permission_Action", action, parent=ndb.Key("Permission_Type", type, parent=user_key(user)))
    if id:
        return ndb.Key("Permission", id, parent=ndb.Key("Permission_Action", action, parent=type_key))
    else:
        return ndb.Key("Permission", action, parent=type_key)


def permission_check(user, type, action, id=None):
    result = permission_get(user, type, action, id)

    id_str = ""
    if id: id_str = ":" + str(id)

    if result:
        log.debug("Permission: %s %s%s (%s) - Allowed" % (user, type, id_str, action))
    else:
        log.debug("Permission: %s %s%s (%s) - Not Allowed" % (user, type, id_str, action))

    return result


def permission_is_root(user):
    if permission_check(user, "root", "root") or users.is_current_user_admin() or True:
        log.debug("Root User Allowed")
        return True
    else:
        return False


def permission_get(user, type, action, id=None):
    return permission_key(user, type, action, id).get()


def permission_grant(viewer, keys, data):
    if permission_check(viewer, "permissions", "grant") or permission_is_root(viewer):
        id = None
        if "id" in keys:
            id = keys["id"]

        key = permission_key(keys["user"], keys["type"], keys["action"], id)
        if not key.get():
            permission = Permission(key=key)
            permission.user = users.User(keys["user"])
            permission.type = keys["type"]
            permission.id = id
            permission.action = keys["action"]
            permission.put()

            log.debug("Permission granted")
        else:
            log.warn("Permission already granted")
    else:
        log.debug("Not allowed")

    return "/users/%s/permissions/" % keys["user"]


def permission_revoke(viewer, keys, data):
    if permission_check(viewer, "permissions", "revoke") or permission_is_root(viewer):
        id = None
        if "id" in keys:
            id = keys["id"]

        key = permission_key(keys["user"], keys["type"], keys["action"], id)
        key.delete()
        log.debug("Permission revoked")
    else:
        log.debug("Not allowed")

    return "/users/%s/permissions/" % keys["user"]


def permission_list(viewer, user):
    if permission_check(viewer, "permissions", "view") or permission_is_root(viewer):
        result = []
        for permission in Permission.query(ancestor=user_key(user)).fetch():
            result.append({ 'user'   : permission.user.email(),
                            'type'   : permission.type,
                            'id'     : permission.id,
                            'action' : permission.action })
        return result


class Permission(ndb.Model):
    user = ndb.UserProperty()
    type = ndb.StringProperty()
    id = ndb.StringProperty()
    action = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)



