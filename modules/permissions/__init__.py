import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from users import user_key

from google.appengine.ext import ndb
from google.appengine.api import users


log = logging.getLogger("permissions")

dependencies = ["users"]

templates = { "{user}" : "list" }


def permission_key(user, id):
    return ndb.Key("Permissions", parent=user_key(user))


def permission_grant(viewer, keys, data):
    if (permission_check(viewer, "permissions", "grant")
            or permission_is_root(viewer)
            or viewer.is_current_user_admin()):
        id = None
        if "id" in keys:
            id = keys["id"]

        if not permission_get(keys["user"], keys["type"], keys["action"], id):
            permission = Permission(parent=user_key(keys["user"]))
            permission.type = keys["type"]
            permission.id = id
            permission.action = keys["action"]
            permission.put()

            log.debug("Permission granted")
        else:
            log.warn("Permission already granted")
    else:
        log.debug("Not allowed")

    return "/permissions/%s" % keys["user"]


def permission_revoke(viewer, keys, data):
    if permission_check(viewer, "permissions", "revoke"):
        id = None
        if "id" in keys:
            id = keys["id"]

        permission = permission_get(keys["user"], keys["type"], keys["action"], id)
        if (permission):
            permission.key.delete()
            log.debug("Permission revoked")
        else:
            log.debug("Permission not granted")
    else:
        log.debug("Not allowed")

    return "/permissions/%s" % keys["user"]


def permission_is_root(user):
    return permission_check(user, "root", "root")


def permission_check(user, type, action, id=None):
    result = permission_get(user, type, action, id)

    if result:
        log.debug("Permission: %s %s:%s (%s) - Allowed" % (user, type, id, action))
    else:
        log.debug("Permission: %s %s:%s (%s) - Not Allowed" % (user, type, id, action))

    return result


def permission_get(user, type, action, id=None):
    return Permission.query(
        Permission.type == type,
        Permission.id == id,
        Permission.action == action,
        ancestor=user_key(user)).get()


def permission_list(viewer, user):
    if permission_check(viewer, "permissions", "view"):
        result = []
        for permission in Permission.query(ancestor=user_key(user)).fetch():
            result.append({ 'user' : permission.key.parent().id(),
                            'type' : permission.type,
                            'id' : permission.id,
                            'action' : permission.action })
        return result


class Permission(ndb.Model):
    type = ndb.StringProperty()
    id = ndb.StringProperty()
    action = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)


types = { 'permission_list'      : permission_list }

actions = { "PUT"    : { "{user}/{type}/{action}"      : permission_grant,
                         "{user}/{type}/{action}/{id}" : permission_grant },
            "DELETE" : { "{user}/{type}/{action}"      : permission_revoke,
                         "{user}/{type}/{action}/{id}" : permission_revoke } }





