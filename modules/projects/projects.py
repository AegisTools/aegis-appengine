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
from clients.clients import client_key


log = logging.getLogger("projects")


def project_key(client_id, project_ids):
    key = client_key(client_id)
    if not project_ids:
        return key

    for segment in project_ids:
        key = ndb.Key("Project", segment, parent=key)

    return key


def project_http_put(actor, client_id, project_ids, **kwargs):
    key = project_key(client_id, project_ids)
    project = key.get()
    if project:
        if permission_check(actor, "project", "update") or permission_is_root(actor):
            project_update(actor, project=project, **kwargs)
        else:
            raise NotAllowedError()
    else:
        project_http_post(actor, key=key, project_ids=project_ids, **kwargs)


def project_http_post(actor, **kwargs):
    if permission_check(actor, "project", "create") or permission_is_root(actor):
        project_create(actor, **kwargs)
    else:
        raise NotAllowedError()


def project_http_delete(actor, client_id, project_ids, **ignored):
    if permission_check(actor, "project", "delete") or permission_is_root(actor):
        project_deactivate(actor, client_id, project_ids=project_ids)
    else:
        raise NotAllowedError()


def project_create(actor, key=None, client_id=None, project_ids=None, name=undefined, active=True, **kwargs):
    key = key or project_key(client_id, project_ids or name)
    project = Project(key=key)
    project.name = project_ids[-1]
    project.parent = key.parent()
    project.created_by = build_user_key(actor)
    return project_update(actor, project=project, active=True, name=name, **kwargs)


def project_update(actor, client_id=None, project_ids=None, key=None, project=None, name=undefined, active=undefined, **ignored):
    project = project or (key or project_key(client_id, project_ids)).get()

    if is_defined(name):
        project.name = name

    if is_defined(active):
        project.active = active

    project.updated_by = build_user_key(actor)
    project.put()

    return to_model(project)


def project_deactivate(actor, client_id=None, project_ids=None, key=None, project=None, **ignored):
    project = project_get(client_id, project_ids, key, project)
    project.updated_by = build_user_key(actor)
    project.active = False
    project.put()


def project_get(client_id=None, project_ids=None, key=None, project=None):
    result = project or (key or project_key(client_id, project_ids)).get()
    if result:
        return result
    else:
        raise NotFoundError()


def project_load(viewer, client_id, project_ids=None):
    if permission_check(viewer, "project", "read") or permission_is_root(viewer):
        key = project_key(client_id, project_ids)
        parent = None
        children = []
        for child in Project.query(Project.parent == key, ancestor=key):
            if child.active:
                children.append(to_model(child))

        if project_ids:
            project = to_model(key.get())
            if project:
                if key.parent():
                    parent = to_model(key.parent().get())
                project["parent"] = parent
                project["children"] = children
            return project
        else:
            return children
    else:
        log.debug("Not allowed")


def to_model(project):
    if not project:
        return None

    path = []
    key = project.key
    while key:
        path.insert(0, key.id())
        key = key.parent()

    return { 'key'        : path[1:],
             'client'     : path[0],
             'path'       : "/".join(path[1:]),
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
    parent = ndb.KeyProperty()
    name = ndb.StringProperty(required=True)
    active = ndb.BooleanProperty(default=True)
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated_by = ndb.KeyProperty(kind='User')
    updated = ndb.DateTimeProperty(auto_now=True)


