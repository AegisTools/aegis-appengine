import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import wipe
from users.permissions import permission_check, permission_is_root
from users.users import user_key


log = logging.getLogger("tags")


def tag_key(tag_names):
    key = None
    if not tag_names:
        return None

    for name in tag_names:
        key = ndb.Key("Tag", name, parent=key)

    return key


def tag_create(viewer, tag):
    if permission_check(viewer, "tag", "create") or permission_is_root(viewer):
        key = tag_key(tag)
        if not key.get():
            new_tag = Tag(key=key)
            new_tag.name = key.id()
            new_tag.created_by = user_key(viewer)
            new_tag.put()
        else:
            log.debug("Tag exists")
    else:
        log.debug("Not allowed")

    return None


def tag_delete(viewer, tag):
    if permission_check(viewer, "tag", "delete") or permission_is_root(viewer):
        wipe(tag_key(tag))
    else:
        log.debug("Not allowed")

    return "/tags"


def load_tag(viewer, id):
    if permission_check(viewer, "tag", "read") or permission_is_root(viewer):
        children = []
        for child in Tag.query(ancestor=tag_key(id)):
            children.append(tag_to_model(child))

        if id:
            tag = tag_to_model(tag_key(id).get())
            if tag:
                tag["children"] = children
            return tag
        else:
            return children
    else:
        log.debug("Not allowed")


def tag_apply(viewer, target, tag):
    if permission_check(viewer, "tag", "apply") or permission_is_root(viewer):
        key = tag_key(tag)
        if not AppliedTag.query(AppliedTag.tag == key, AppliedTag.target == target, ancestor=target).get():
            new_tag = AppliedTag(parent=target)
            new_tag.applied_by = user_key(viewer)
            new_tag.tag = key
            new_tag.target = target
            new_tag.put()
            log.debug("Tag %s applied" % key)
            return "/tags/%s" % "/".join(tag)
        else:
            log.debug("Tag already applied")
    else:
        log.debug("Not allowed")


def tag_remove(viewer, target, tag):
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


def tag_to_model(tag):
    if not tag:
        return None

    path = []
    key = tag.key
    while key:
        path.insert(0, key.id())
        key = key.parent()

    return { 'path'       : path,
             'name'       : tag.name,
             'created_by' : tag.created_by.id(),
             'created'    : tag.created }


def tag_key_to_path(key):
    path = key.id()
    while True:
        key = key.parent()
        if not key:
            return path
        path = key.id() + "/" + path


class Tag(ndb.Model):
    name = ndb.StringProperty()
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)


class AppliedTag(ndb.Model):
    target = ndb.KeyProperty()
    applied_by = ndb.KeyProperty(kind='User')
    applied = ndb.DateTimeProperty(auto_now_add=True)
    tag = ndb.KeyProperty(kind=Tag)

