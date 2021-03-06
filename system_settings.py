import sys
import os
import types

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api import users

from modules.users.users import build_user_key
from modules.users.permissions import permission_check, permission_is_root


def system_settings_key():
    return ndb.Key("SystemSettings", "root")


def get_system_settings():
    settings = memcache.get("settings", namespace="aegis")
    if not settings:
        settings = system_settings_key().get()
        if settings:
            settings = { key: str(getattr(settings, key)) for key in settings._properties
                    if not key.startswith("_") and \
                       not isinstance(getattr(settings, key), types.FunctionType) }
        else:
            settings = {}
        memcache.add("settings", settings, namespace="aegis")
    return settings


def save_system_settings(actor, settings):
    if permission_check(actor, "system", "update") or permission_is_root(actor):
        old_settings = system_settings_key().get()
        if not old_settings:
            old_settings = SystemSettings(key=system_settings_key())

        for key in settings:
            setattr(old_settings, key, settings[key])

        old_settings.updated_by = build_user_key(actor)
        old_settings.put()

        memcache.delete("settings", namespace="aegis")
    else:
        raise NotAllowedError()


class SystemSettings(ndb.Expando):
    updated = ndb.DateTimeProperty(auto_now=True)
    updated_by = ndb.KeyProperty(kind='User')


