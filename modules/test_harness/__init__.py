import sys
import os
import logging


from google.appengine.ext import ndb
from google.appengine.api import memcache

from users.permissions import permission_check, permission_grant, permission_revoke
from tags.tags import tag_apply, tag_remove, tag_list

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import wipe


log = logging.getLogger("test_harness")


dependencies = ["users"]

"""
GENERAL PURPOSE STUBS
"""

def wipe(viewer, keys, data):
    log.error("Wiping entire database")
    ndb.delete_multi(ndb.Query().iter(keys_only = True))
    # db.delete(db.Query(keys_only=True))
    memcache.flush_all()

"""
PERMISSION STUBS
"""

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

"""
TAG STUBS
"""

def apply_tag(viewer, keys, data):
    tag_apply(viewer, ndb.Key('Thing', keys["thing"]), keys["tag"])


def remove_tag(viewer, keys, data):
    tag_remove(viewer, ndb.Key('Thing', keys["thing"]), keys["tag"])


def get_tags(viewer, target):
    log.debug("get_tags(%s)" % target)
    return tag_list(viewer, ndb.Key('Thing', target))


"""
HELPER METHODS
"""

def build_thing_key(keys):
    key = None
    if ("thing" in keys):
        for chunk in keys["thing"]:
            key = ndb.Key(keys["kind"], chunk, parent=key)
            log.debug(key)
    return key




templates = { "tag/{thing}"                                  : "tag_list",
              "permissions/{user}/{action}/{kind}"           : "permission_view",
              "permissions/{user}/{action}/{kind}/{thing}/*" : "permission_view" }


types = { "permission" : check_permission,
          "tags"       : get_tags }


actions = { "POST"   : { "wipe"                                         : wipe },
            "PUT"    : { "tag/{thing}/{tag}/*"                          : apply_tag,
                         "permissions/{user}/{action}/{kind}"           : grant_permission,
                         "permissions/{user}/{action}/{kind}/{thing}/*" : grant_permission },
            "DELETE" : { "tag/{thing}/{tag}/*"                          : remove_tag,
                         "permissions/{user}/{action}/{kind}"           : revoke_permission,
                         "permissions/{user}/{action}/{kind}/{thing}/*" : revoke_permission } }


log.warn("Test harness is enabled")

