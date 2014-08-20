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


def task_create(viewer, task, name=None, **ignored):
    if permission_check(viewer, "task", "create") or permission_is_root(viewer):
        key = task_key(task)
        if not key.get():
            new = Task(key=key)
            new.parent = key.parent()
            new.name = name or key.id()
            new.created_by = user_key(viewer)
            new.put()
        else:
            log.debug("Task exists")
    else:
        log.debug("Not allowed")

    return None


def task_delete(viewer, task, **ignored):
    if permission_check(viewer, "task", "delete") or permission_is_root(viewer):
        wipe(task_key(task))
    else:
        log.debug("Not allowed")

    return "/tasks"


def load_task(viewer, id):
    if permission_check(viewer, "task", "read") or permission_is_root(viewer):
        key = task_key(id)
        parent = None
        children = []
        for child in Task.query(Task.parent == key, ancestor=key):
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
             'created'    : task.created }


def task_key_to_path(key):
    path = key.id()
    while True:
        key = key.parent()
        if not key:
            return path
        path = key.id() + "/" + path


class Task(ndb.Model):
    parent = ndb.KeyProperty(kind='Task')
    name = ndb.StringProperty()
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)

