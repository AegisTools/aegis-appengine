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


def project_create(viewer, project, name=None, active=True, **ignored):
    if permission_check(viewer, "project", "create") or permission_is_root(viewer):
        project_obj = project_key(project).get()
        if not project_obj:
            project_obj = Project(key=project_key(project))
            project_obj.parent = project_obj.key.parent()
            project_obj.name = name or project_obj.key.id()
            project_obj.created_by = user_key(viewer)
        if active:
            project_obj.active = active
        if name:
            project_obj.name = name
        project_obj.put()
    else:
        log.debug("Not allowed")

    return None


def project_delete(viewer, project, **ignored):
    if permission_check(viewer, "project", "delete") or permission_is_root(viewer):
        project = project_key(project).get()
        if project:
            project.active = False
            project.put()
        else:
            log.debug("Project not found")
    else:
        log.debug("Not allowed")

    return "/projects"


def load_project(viewer, id=None):
    if permission_check(viewer, "project", "read") or permission_is_root(viewer):
        key = project_key(id)
        parent = None
        children = []
        for child in Project.query(Project.parent == key, ancestor=key):
            if child.active:
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
             'created'    : project.created,
             'active'     : project.active }


def project_key_to_path(key):
    path = key.id()
    while True:
        key = key.parent()
        if not key:
            return path
        path = key.id() + "/" + path


class Project(ndb.Model):
    parent = ndb.KeyProperty(kind='Project')
    name = ndb.StringProperty(required=True)
    created_by = ndb.KeyProperty(kind='User', required=True)
    created = ndb.DateTimeProperty(auto_now_add=True, required=True)
    active = ndb.BooleanProperty(default=True, required=True)


