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

def wipe(viewer, **ignored):
    log.error("Wiping entire database")
    ndb.delete_multi(ndb.Query().iter(keys_only = True))
    # db.delete(db.Query(keys_only=True))
    memcache.flush_all()

"""
PERMISSION STUBS
"""

def grant_permission(viewer, user, kind, action, thing=[], **ignored):
    key = build_thing_key(kind, thing)
    permission_grant(viewer, user, kind, action, key)


def revoke_permission(viewer, user, kind, action, thing=[], **ignored):
    key = build_thing_key(kind, thing)
    permission_revoke(viewer, user, kind, action, key)


def check_permission(viewer, keys):
    log.debug(keys)
    if "thing" in keys:
        key = build_thing_key(keys["kind"], keys["thing"])
    else:
        key = build_thing_key(keys["kind"], [])

    if permission_check(keys["user"], keys["kind"], keys["action"], key):
        return { "allowed": True }
    else:
        return { "allowed": False }

"""
TAG STUBS
"""

def apply_tag(viewer, thing, tag, **ignored):
    tag_apply(viewer, ndb.Key('Thing', thing), tag)


def remove_tag(viewer, thing, tag, **ignored):
    tag_remove(viewer, ndb.Key('Thing', thing), tag)


def get_tags(viewer, thing):
    return tag_list(viewer, ndb.Key('Thing', thing))


"""
HELPER METHODS
"""

def build_thing_key(kind, id):
    key = None
    for chunk in id:
        key = ndb.Key(kind, chunk, parent=key)
        log.debug(key)
    return key




templates = { "tag/{thing}"                                  : "tag_list",
              "permissions/{user}/{action}/{kind}"           : "permission_view",
              "permissions/{user}/{action}/{kind}/{thing}/*" : "permission_view" }


types = { "permission" : check_permission,
          "tags"       : get_tags }


actions = { "wipe"                                         : { "POST"   : { "method" : wipe } },
            "tag/{thing}/{tag}/*"                          : { "PUT"    : { "method" : apply_tag },
                                                               "DELETE" : { "method" : remove_tag } },
            "permissions/{user}/{action}/{kind}"           : { "PUT"    : { "method" : grant_permission },
                                                               "DELETE" : { "method" : revoke_permission } },
            "permissions/{user}/{action}/{kind}/{thing}/*" : { "PUT"    : { "method" : grant_permission } } }


log.warn("Test harness is enabled")

