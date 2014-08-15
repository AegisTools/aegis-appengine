import logging
from private import *

from google.appengine.ext import ndb

log = logging.getLogger("permissions")


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
    return permission_check(user, "root", "root") or users.is_current_user_admin()


