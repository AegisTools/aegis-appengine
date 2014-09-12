import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *
from users.permissions import permission_check, permission_is_root
from users.users import build_user_key


log = logging.getLogger("tags")


def tag_key(tag_ids):
    log.debug(tag_ids)
    key = None
    if not tag_ids:
        return None

    for segment in tag_ids:
        key = ndb.Key("Tag", segment, parent=key)

    return key


def tag_http_put(actor, tag_ids, **kwargs):
    key = tag_key(tag_ids)
    tag = key.get()
    if tag:
        if permission_check(actor, "tag", "update") or permission_is_root(actor):
            tag_update(actor, tag=tag, **kwargs)
        else:
            raise NotAllowedError()
    else:
        tag_http_post(actor, key=key, tag_ids=tag_ids, **kwargs)


def tag_http_post(actor, **kwargs):
    if permission_check(actor, "tag", "create") or permission_is_root(actor):
        tag_create(actor, **kwargs)
    else:
        raise NotAllowedError()


def tag_http_delete(actor, tag_ids, **ignored):
    if permission_check(actor, "tag", "delete") or permission_is_root(actor):
        tag_deactivate(actor, tag_ids=tag_ids)
    else:
        raise NotAllowedError()


def tag_create(actor, key=None, tag_ids=None, name=undefined, active=True, **kwargs):
    key = key or tag_key(tag_ids or name)
    tag = Tag(key=key)
    tag.name = tag_ids[-1]
    tag.parent = key.parent()
    tag.created_by = build_user_key(actor)
    return tag_update(actor, tag=tag, active=True, name=name, **kwargs)


def tag_update(actor, tag_ids=None, key=None, tag=None, name=undefined, active=undefined, **ignored):
    tag = tag or (key or tag_key(tag_ids)).get()

    if is_defined(name):
        tag.name = name

    if is_defined(active):
        tag.active = active

    tag.updated_by = build_user_key(actor)
    tag.put()

    return to_model(tag)


def tag_deactivate(actor, tag_ids=None, key=None, tag=None, **ignored):
    tag = tag_get(tag_ids, key, tag)
    tag.updated_by = build_user_key(actor)
    tag.active = False
    tag.put()


def tag_get(tag_ids=None, key=None, tag=None):
    result = tag or (key or tag_key(tag_ids)).get()
    if result:
        return result
    else:
        raise NotFoundError()


def tag_load(viewer, tag_ids=None):
    if permission_check(viewer, "tag", "read") or permission_is_root(viewer):
        key = tag_key(tag_ids)
        parent = None
        children = []
        for child in Tag.query(Tag.parent == key, ancestor=key):
            if child.active:
                children.append(to_model(child))

        if tag_ids:
            tag = to_model(key.get())
            if tag:
                if key.parent():
                    parent = to_model(key.parent().get())
                tag["parent"] = parent
                tag["children"] = children
            return tag
        else:
            return children
    else:
        log.debug("Not allowed")


def tag_apply(viewer, target, tag, **ignored):
    if permission_check(viewer, "tag", "apply") or permission_is_root(viewer):
        key = tag_key(tag)
        if not AppliedTag.query(AppliedTag.tag == key, AppliedTag.target == target, ancestor=target).get():
            new_tag = AppliedTag(parent=target)
            new_tag.applied_by = build_user_key(viewer)
            new_tag.tag = key
            new_tag.target = target
            new_tag.put()
            log.debug("Tag %s applied" % key)
            return "/tags/%s" % "/".join(tag)
        else:
            log.debug("Tag already applied")
    else:
        log.debug("Not allowed")


def tag_remove(viewer, target, tag, **ignored):
    if permission_check(viewer, "tag", "remove") or permission_is_root(viewer):
        key = tag_key(tag)
        applied = AppliedTag.query(AppliedTag.tag == key, AppliedTag.target == target, ancestor=target).get(keys_only=True)
        if applied:
            applied.delete()
            log.debug("Tag removed")
        else:
            log.debug("Tag not applied")
    else:
        log.debug("Not allowed")


def tag_list(viewer, target):
    log.debug("Listing tags for %s" % target)

    if permission_check(viewer, "tag", "view") or permission_is_root(viewer):
        log.debug("Listing tags for %s" % target)
        result = []
        for applied in AppliedTag.query(AppliedTag.target == target, ancestor=target).filter():
            result.append(tag_key_to_path(applied.tag))
        return result
    else:
        log.debug("Not allowed")


def to_model(tag):
    if not tag:
        return None

    path = []
    key = tag.key
    while key:
        path.insert(0, key.id())
        key = key.parent()

    log.debug(tag)
    log.debug(tag.active)

    return { 'key'        : path,
             'path'       : "/".join(path),
             'name'       : tag.name,
             'created_by' : tag.created_by.id(),
             'created'    : tag.created,
             'active'     : tag.active }


def tag_key_to_path(key):
    path = key.id()
    while True:
        key = key.parent()
        if not key:
            return path
        path = key.id() + "/" + path


class Tag(ndb.Model):
    parent = ndb.KeyProperty(kind='Tag')
    name = ndb.StringProperty(required=True)
    active = ndb.BooleanProperty(default=True, required=True)
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated_by = ndb.KeyProperty(kind='User')
    updated = ndb.DateTimeProperty(auto_now=True)


class AppliedTag(ndb.Model):
    target = ndb.KeyProperty()
    applied_by = ndb.KeyProperty(kind='User')
    applied = ndb.DateTimeProperty(auto_now_add=True)
    tag = ndb.KeyProperty(kind=Tag)


