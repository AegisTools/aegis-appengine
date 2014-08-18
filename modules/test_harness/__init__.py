import sys
import os
import logging


from google.appengine.ext import ndb
from google.appengine.api import memcache

from users.permissions import permission_check, permission_grant, permission_revoke

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import wipe


log = logging.getLogger("test_harness")


dependencies = ["users"]


def wipe(viewer, keys, data):
    log.error("Wiping entire database")
    ndb.delete_multi(ndb.Query().iter(keys_only = True))
    # db.delete(db.Query(keys_only=True))
    memcache.flush_all()


def grant_permission(viewer, keys, data):
    key = build_thing_key(keys)
    permission_grant(viewer, keys["user"], keys["kind"], keys["action"], key)


def revoke_permission(viewer, keys, data):
    key = build_thing_key(keys)
    permission_revoke(viewer, keys["user"], keys["kind"], keys["action"], key)


def check_permission(viewer, keys):
    key = build_thing_key(keys)
    if permission_check(keys["user"], keys["kind"], keys["action"], key):
        return { "allowed": True }
    else:
        return { "allowed": False }


def build_thing_key(keys):
    key = None
    if ("thing" in keys):
        for chunk in keys["thing"]:
            key = ndb.Key(keys["kind"], chunk, parent=key)
            log.debug(key)
    return key


templates = { "permission/{user}/{action}/{kind}"           : "permission_view",
              "permission/{user}/{action}/{kind}/{thing}/*" : "permission_view" }


types = { "permission" : check_permission }


actions = { "POST"   : { "wipe"                                        : wipe },
            "PUT"    : { "permission/{user}/{action}/{kind}"           : grant_permission,
                         "permission/{user}/{action}/{kind}/{thing}/*" : grant_permission },
            "DELETE" : { "permission/{user}/{action}/{kind}"           : revoke_permission,
                         "permission/{user}/{action}/{kind}/{thing}/*" : revoke_permission } }


log.warn("Test harness is enabled")

