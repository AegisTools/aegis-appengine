import sys
import os
import logging


from google.appengine.ext import ndb
from google.appengine.api import memcache

from users.users import user_create
from users.permissions import permission_check, permission_grant, permission_revoke
from tags.tags import tag_apply, tag_remove, tag_list
from remarks.remarks import remark_create, remark_list

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import wipe


log = logging.getLogger("test_harness")


if not os.environ.get('SERVER_SOFTWARE','').startswith('Development'):
    log.debug("Production environment detected; test harness disabled")
else:
    log.warn("Development environment detected; test harness enabled")


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
    ISSUE STUBS
    """

    def issue_permission(viewer, user=None, **ignored):
        permission_grant(viewer, "issue", "read", user=user or viewer)
        permission_grant(viewer, "issue", "create", user=user or viewer)
        permission_grant(viewer, "issue", "update", user=user or viewer)
        permission_grant(viewer, "user", "read", user=user or viewer)

    """
    PERMISSION STUBS
    """

    def grant_permission(viewer, user, kind, action, thing=[], **ignored):
        key = build_thing_key(kind, thing)
        permission_grant(viewer, kind, action, key, user=user)


    def revoke_permission(viewer, user, kind, action, thing=[], **ignored):
        key = build_thing_key(kind, thing)
        permission_revoke(viewer, kind, action, key, user=user)


    def check_permission(viewer, keys, **ignored):
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


    def get_tags(viewer, thing, **ignored):
        return tag_list(viewer, ndb.Key('Thing', thing))

    """
    REMARK STUBS
    """

    def remark(viewer, thing, **ignored):
        remark_create(viewer, ndb.Key('Thing', thing), "This is a dummy remark")


    def get_remarks(viewer, thing, **ignored):
        return remark_list(viewer, ndb.Key('Thing', thing))

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
                  "permissions/{user}/{action}/{kind}/{thing}/*" : "permission_view",
                  "remarks/{thing}"                              : "remarks_view" }


    types = { "permission" : check_permission,
              "tags"       : get_tags,
              "remarks"    : get_remarks }


    actions = { "wipe"                                         : { "POST"   : { "method"   : wipe,
                                                                                "redirect" : "/200" } },
                "tag/{thing}/{tag}/*"                          : { "PUT"    : { "method"   : apply_tag,
                                                                                "redirect" : "/200" },
                                                                   "DELETE" : { "method"   : remove_tag,
                                                                                "redirect" : "/200" } },
                "permissions/{user}/{action}/{kind}"           : { "PUT"    : { "method"   : grant_permission,
                                                                                "redirect" : "/200" },
                                                                   "DELETE" : { "method"   : revoke_permission,
                                                                                "redirect" : "/200" } },
                "permissions/{user}/{action}/{kind}/{thing}/*" : { "PUT"    : { "method"   : grant_permission,
                                                                                "redirect" : "/200" } },
                "remarks/{thing}"                              : { "POST"   : { "method"   : remark,
                                                                                "redirect" : "/200" } },
                "issues/permission"                            : { "PUT"    : { "method"   : issue_permission,
                                                                                "redirect" : "/200" } } }



