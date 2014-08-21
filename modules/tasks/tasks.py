import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import wipe
from users.permissions import permission_check, permission_is_root
from users.users import user_key


log = logging.getLogger("tasks")


def task_key(task_names):
    key = None
    if not task_names:
        return None

    for name in task_names:
        key = ndb.Key("Task", name, parent=key)

    return key


def task_create(viewer, task, name=None, active=True, **ignored):
    if permission_check(viewer, "task", "create") or permission_is_root(viewer):
        task_obj = task_key(task).get()
        if not task_obj:
            task_obj = Task(key=task_key(task))
            task_obj.parent = task_obj.key.parent()
            task_obj.name = name or task_obj.key.id()
            task_obj.created_by = user_key(viewer)
        if active:
            task_obj.active = active
        if name:
            task_obj.name = name
        task_obj.put()
    else:
        log.debug("Not allowed")

    return None


def task_delete(viewer, task, **ignored):
    if permission_check(viewer, "task", "delete") or permission_is_root(viewer):
        task = task_key(task).get()
        if task:
            task.active = False
            task.put()
        else:
            log.debug("Task not found")
    else:
        log.debug("Not allowed")

    return "/tasks"


def load_task(viewer, id):
    if permission_check(viewer, "task", "read") or permission_is_root(viewer):
        key = task_key(id)
        parent = None
        children = []
        for child in Task.query(Task.parent == key, ancestor=key):
            if child.active:
                children.append(task_to_model(child))

        if id:
            task = task_to_model(key.get())
            if task:
                if key.parent():
                    parent = task_to_model(key.parent().get())
                task["parent"] = parent
                task["children"] = children
            return task
        else:
            return children
    else:
        log.debug("Not allowed")


def task_to_model(task):
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
    created_by = ndb.KeyProperty(kind='User', required=True)
    created = ndb.DateTimeProperty(auto_now_add=True, required=True)
    active = ndb.BooleanProperty(default=True, required=True)


