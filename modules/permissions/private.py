import sys
import os
import logging

from google.appengine.ext import ndb

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from users.public import *

log = logging.getLogger("permissions")


def permission_get(user, type, action, id=None):
    query = Permission.query(
        Permission.type == type,
        Permission.action == action,
        ancestor=user_key(user))
    if id:
        query.filter(Permission.id == id)
    return query.get()


class Permission(ndb.Model):
    type = ndb.StringProperty()
    id = ndb.StringProperty()
    action = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

