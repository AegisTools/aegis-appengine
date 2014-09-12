import sys
import os
import logging

from google.appengine.ext import ndb

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.errors import *
from common.arguments import *
from users.permissions import permission_check, permission_is_root
from users.users import build_user_key


log = logging.getLogger("clients")


def client_key(client_id):
    return ndb.Key("Client", client_id)


def client_http_put(actor, client_id, **kwargs):
    key = client_key(client_id)
    client = key.get()
    if client:
        if permission_check(actor, "client", "update") or permission_is_root(actor):
            client_update(actor, client=client, **kwargs)
        else:
            raise NotAllowedError()
    else:
        client_http_post(actor, key=key, client_id=client_id, **kwargs)


def client_http_post(actor, **kwargs):
    if permission_check(actor, "client", "create") or permission_is_root(actor):
        client_create(actor, **kwargs)
    else:
        raise NotAllowedError()


def client_http_delete(actor, client_id, **ignored):
    if permission_check(actor, "client", "delete") or permission_is_root(actor):
        client_deactivate(actor, client_id=client_id)
    else:
        raise NotAllowedError()


def client_create(actor, key=None, client_id=None, name=undefined, active=True, **kwargs):
    key = key or client_key(client_id or name)
    client = Client(key=key)
    client.name = client_id
    client.created_by = build_user_key(actor)
    return client_update(actor, client=client, active=True, name=name, **kwargs)


def client_update(actor, client_id=None, key=None, client=None, name=undefined, active=undefined, **ignored):
    client = client or (key or client_key(client_id)).get()

    if is_defined(name):
        client.name = name

    if is_defined(active):
        client.active = active

    client.updated_by = build_user_key(actor)
    client.put()

    return to_model(client)


def client_deactivate(actor, client_id=None, key=None, client=None, **ignored):
    client = client_get(client_id, key, client)
    client.updated_by = build_user_key(actor)
    client.active = False
    client.put()


def client_get(client_id=None, key=None, client=None):
    result = client or (key or client_key(client_id)).get()
    if result:
        return result
    else:
        raise NotFoundError()


def client_load(viewer, client_id=None, key=None):
    if permission_check(viewer, "client", "read") or permission_is_root(viewer):
        return to_model((key or client_key(client_id)).get())
    else:
        raise NotAllowedError()


def client_list(viewer):
    if permission_check(viewer, "client", "read") or permission_is_root(viewer):
        result = []
        for client in Client.query().filter(Client.active == True):
            result.append(to_model(client))

        return result
    else:
        raise NotAllowedError()


def to_model(client):
    if not client:
        return None

    return { 'key'        : client.key.id(),
             'name'       : client.name,
             'active'     : client.active,
             'created_by' : client.created_by.id(),
             'created'    : client.created,
             'updated_by' : client.updated_by.id(),
             'updated'    : client.updated }


class Client(ndb.Model):
    name = ndb.StringProperty(required=True)
    active = ndb.BooleanProperty(default=True, required=True)
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated_by = ndb.KeyProperty(kind='User')
    updated = ndb.DateTimeProperty(auto_now=True)



