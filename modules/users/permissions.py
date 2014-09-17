import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import memcache

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *

log = logging.getLogger("permissions")
log.setLevel(logging.DEBUG)


def permission_lookup(user, type, action, target=None, keys_only=True):
    if not isinstance(user, ndb.Model):
        user = build_user_key(user).get()

    if not user:
        return None

    return permission_get(type, action, target, user, user.groups, keys_only=keys_only)


def permission_verify(user, type, action, target=None, root_ok=True):
    original_user = user
    user_key = build_user_key(user)
    if not isinstance(user, ndb.Model):
        user = user_key.get()

    tuple = (type, action, target)
    cached = memcache.get(user_key.id(), namespace="permissions") or []

    if not user:
        log.warn("User not recognized")
    else:
        if tuple in cached:
            log.debug("Permission Allowed (Cache): %s - %s.%s (%s)" % (user.user.email(), type, action, target))
            return

        if permission_lookup(user, type, action, target):
            log.debug("Permission Allowed:         %s - %s.%s (%s)" % (user.user.email(), type, action, target))
            cached.append(tuple)
            memcache.set(user_key.id(), cached, namespace="permissions")
            return
        else:
            log.debug("Permission Not Allowed:     %s - %s.%s (%s)" % (user.user.email(), type, action, target))

        if target:
            if permission_lookup(user, type, action):
                log.debug("Permission Allowed:         %s - %s.%s (%s)" % (user.user.email(), type, action, None))
                cached.append(tuple)
                memcache.set(user_key.id(), cached, namespace="permissions")
                return
            else: 
                log.debug("Permission Not Allowed:     %s - %s.%s (%s)" % (user.user.email(), type, action, None))

    if root_ok and permission_is_root(original_user):
        cached.append(tuple)
        memcache.set(user_key.id(), cached, namespace="permissions")
        log.debug("Permission Allowed (Root):  %s" % user_key.id())
        return

    log.error("Permission Denied:       %s" % user_key.id())
    raise NotAllowedError()


def permission_check(user, type, action, key=None):
    if not type:
        type = key.kind()

    user_key = build_user_key(user)
    result = permission_lookup(user_key, type, action, key)

    key_str = ""
    if key: key_str = ":" + key.urlsafe()

    if result:
        log.debug("Permission: %s %s%s (%s) - Allowed" % (user_key, type, key_str, action))
    else:
        log.debug("Permission: %s %s%s (%s) - Not Allowed" % (user_key, type, key_str, action))
        if key:
            return permission_check(user_key, type, action, key.parent())

    return result


def permission_is_root(user):
    if build_user_key(user).id() == "cron":
        return True
    if users.is_current_user_admin():
        return True
    if permission_lookup(user, "root", "root"):
        return True
    else:
        return False


def permission_get(type, action, target, user, groups, keys_only=True):
    if user and groups:
        return Permission.query().filter( \
            ndb.AND(Permission.type == type,
                    Permission.action == action,
                    Permission.target == target,
                    ndb.OR(Permission.user == build_user_key(user),
                           Permission.group.IN([build_group_key(group) for group in groups])))).get(keys_only=keys_only)
    elif user:
        return Permission.query(ancestor=build_user_key(user)).filter( \
            ndb.AND(Permission.type == type,
                    Permission.action == action,
                    Permission.target == target)).get(keys_only=keys_only)
    elif groups:
        return Permission.query().filter( \
            ndb.AND(Permission.type == type,
                    Permission.action == action,
                    Permission.target == target,
                    Permission.group.IN([build_group_key(group) for group in groups]))).get(keys_only=keys_only)


def permission_grant(viewer, type, action, target=None, user=None, group=None):
    permission_verify(viewer, "permissions", "grant")

    if not permission_get(type, action, target, user, [group] if group else None):
        user = build_user_key(user)
        group = build_group_key(group)

        permission = Permission(parent=user or group)
        permission.user = user
        permission.group = group
        permission.type = type or target.kind()
        permission.action = action
        permission.target = target
        permission.granted_by = build_user_key(viewer)
        permission.put()

        log.debug("Permission Granted: %s - %s.%s (%s)" % (user or group, type, action, target))
    else:
        log.warn("Permission already granted")


def permission_revoke(viewer, type, action, target=None, user=None, group=None):
    permission_verify(viewer, "permissions", "revoke")

    key = permission_get(type, action, target, user, [group] if group else None)
    if key:
        key.delete()
        log.debug("Permission Revoked: %s - %s.%s (%s)" % (build_user_key(user) or build_group_key(group), type, action, target))
        if user:
            memcache.delete(build_user_key(user).id())
        else:
            memcache.flush_all()
    else:
        log.debug("Permission wasn't granted")


def permission_list(viewer, user):
    permission_verify(viewer, "permissions", "view")

    result = []
    for permission in Permission.query(ancestor=build_user_key(user)).fetch():
        result.append({ 'user'   : permission.user.email(),
                        'type'   : permission.type,
                        'id'     : permission.id,
                        'action' : permission.action,
                        'target' : permission.target })
    return result


class Permission(ndb.Model):
    user = ndb.KeyProperty(kind='User')
    group = ndb.KeyProperty(kind='Group')
    type = ndb.StringProperty()
    action = ndb.StringProperty()
    target = ndb.KeyProperty()
    granted = ndb.DateTimeProperty(auto_now_add=True)
    granted_by = ndb.KeyProperty(kind='User')


from users import build_user_key
from groups import build_group_key


