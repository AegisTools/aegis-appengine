import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *
from users.permissions import permission_check, permission_is_root
from users.users import user_key


log = logging.getLogger("tasks")


def task_key(task_ids):
    key = None
    if not task_ids:
        return None

    for segment in task_ids:
        key = ndb.Key("Task", segment, parent=key)

    return key


def task_http_put(actor, task_ids, **kwargs):
    key = task_key(task_ids)
    task = key.get()
    if task:
        if permission_check(actor, "task", "update") or permission_is_root(actor):
            task_update(actor, task=task, **kwargs)
        else:
            raise NotAllowedError()
    else:
        task_http_post(actor, key=key, task_ids=task_ids, **kwargs)


def task_http_post(actor, **kwargs):
    if permission_check(actor, "task", "create") or permission_is_root(actor):
        task_create(actor, **kwargs)
    else:
        raise NotAllowedError()


def task_http_delete(actor, task_ids, **ignored):
    if permission_check(actor, "task", "delete") or permission_is_root(actor):
        task_deactivate(actor, task_ids=task_ids)
    else:
        raise NotAllowedError()


def task_create(actor, key=None, task_ids=None, name=undefined, active=True, **kwargs):
    key = key or task_key(task_ids or name)
    task = Task(key=key)
    task.name = task_ids[-1]
    task.parent = key.parent()
    task.created_by = user_key(actor)
    return task_update(actor, task=task, active=True, name=name, **kwargs)


def task_update(actor, task_ids=None, key=None, task=None, name=undefined, active=undefined, **ignored):
    task = task or (key or task_key(task_ids)).get()

    if is_defined(name):
        task.name = name

    if is_defined(active):
        task.active = active

    task.updated_by = user_key(actor)
    task.put()

    return to_model(task)


def task_deactivate(actor, task_ids=None, key=None, task=None, **ignored):
    task = task_get(task_ids, key, task)
    task.updated_by = user_key(actor)
    task.active = False
    task.put()


def task_get(task_ids=None, key=None, task=None):
    result = task or (key or task_key(task_ids)).get()
    if result:
        return result
    else:
        raise NotFoundError()


def task_load(viewer, task_ids=None):
    if permission_check(viewer, "task", "read") or permission_is_root(viewer):
        key = task_key(task_ids)
        parent = None
        children = []
        for child in Task.query(Task.parent == key, ancestor=key):
            if child.active:
                children.append(to_model(child))

        if task_ids:
            task = to_model(key.get())
            if task:
                if key.parent():
                    parent = to_model(key.parent().get())
                task["parent"] = parent
                task["children"] = children
            return task
        else:
            return children
    else:
        log.debug("Not allowed")


def to_model(task):
    if not task:
        return None

    path = []
    key = task.key
    while key:
        path.insert(0, key.id())
        key = key.parent()

    return { 'key'        : path,
             'path'       : "/".join(path),
             'name'       : task.name,
             'created_by' : task.created_by.id(),
             'created'    : task.created,
             'active'     : task.active }


def task_key_to_path(key):
    path = key.id()
    while True:
        key = key.parent()
        if not key:
            return path
        path = key.id() + "/" + path


class Task(ndb.Model):
    parent = ndb.KeyProperty(kind='Task')
    name = ndb.StringProperty(required=True)
    active = ndb.BooleanProperty(default=True)
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated_by = ndb.KeyProperty(kind='User')
    updated = ndb.DateTimeProperty(auto_now=True)


