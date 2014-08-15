import logging
import sys
import os

from google.appengine.ext import ndb
from google.appengine.api import users

from public import *
from private import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from users.public import *


log = logging.getLogger("permissions")

dependencies = ["users"]

templates = { "{user}" : "list" }


def permission_key(user, id):
    return ndb.Key("Permissions", parent=user_key(user))


def permission_grant(viewer, keys, data):
    if (permission_check(viewer, "permissions", "grant")
            or permission_is_root(viewer)):
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


def permission_list(viewer, user):
    if permission_check(viewer, "permissions", "view"):
        result = []
        for permission in Permission.query(ancestor=user_key(user)).fetch():
            result.append({ 'user' : permission.key.parent().id(),
                            'type' : permission.type,
                            'id' : permission.id,
                            'action' : permission.action })
        return result


types = { 'permission_list'      : permission_list }

actions = { "PUT"    : { "{user}/{type}/{action}"      : permission_grant,
                         "{user}/{type}/{action}/{id}" : permission_grant },
            "DELETE" : { "{user}/{type}/{action}"      : permission_revoke,
                         "{user}/{type}/{action}/{id}" : permission_revoke } }





