import sys
import os
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common import wipe
from users.permissions import permission_check, permission_is_root
from users.users import user_key


log = logging.getLogger("projects")


def project_key(project_names):
    key = None
    if not project_names:
        return None

    for name in project_names:
        key = ndb.Key("Project", name, parent=key)

    return key


def project_create(viewer, project, name=None, **ignored):
    if permission_check(viewer, "project", "create") or permission_is_root(viewer):
        key = project_key(project)
        if not key.get():
            new = Project(key=key)
            new.parent = key.parent()
            new.name = name or key.id()
            new.created_by = user_key(viewer)
            new.put()
        else:
            log.debug("Project exists")
    else:
        log.debug("Not allowed")

    return None


def project_delete(viewer, project, **ignored):
    if permission_check(viewer, "project", "delete") or permission_is_root(viewer):
        wipe(project_key(project))
    else:
        log.debug("Not allowed")

    return "/projects"


def load_project(viewer, id):
    if permission_check(viewer, "project", "read") or permission_is_root(viewer):
        key = project_key(id)
        parent = None
        children = []
        for child in Project.query(Project.parent == key, ancestor=key):
            children.append(project_to_model(child))

        if id:
            project = project_to_model(key.get())
            if project:
                if key.parent():
                    parent = project_to_model(key.parent().get())
                project["parent"] = parent
                project["children"] = children
            return project
        else:
            return children
    else:
        log.debug("Not allowed")


def project_to_model(project):
    if not project:
        return None

    path = []
    key = project.key
    while key:
        path.insert(0, key.id())
        key = key.parent()

    return { 'key'        : path,
             'path'       : "/".join(path),
             'name'       : project.name,
             'created_by' : project.created_by.id(),
             'created'    : project.created }


def project_key_to_path(key):
    path = key.id()
    while True:
        key = key.parent()
        if not key:
            return path
        path = key.id() + "/" + path


class Project(ndb.Model):
    parent = ndb.KeyProperty(kind='Project')
    name = ndb.StringProperty()
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)


