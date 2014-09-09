import sys
import os
import types

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api import users

from modules.users.permissions import permission_check, permission_is_root


def system_settings_key():
    return ndb.Key("SystemSettings", "root")


def get_system_settings():
    settings = memcache.get("system.settings")
    if not settings:
        settings = system_settings_key().get()
        if settings:
            settings = { key: str(getattr(settings, key)) for key in settings._properties
                    if not key.startswith("_") and \
                       not isinstance(getattr(settings, key), types.FunctionType) }
        else:
            settings = {}
        memcache.add("system.settings", settings)
    return settings


def save_system_settings(actor, settings):
    if permission_check(actor, "system", "update") or permission_is_root(actor):
        old_settings = system_settings_key().get()
        if not old_settings:
            old_settings = SystemSettings(key=system_settings_key())

        for key in settings:
            setattr(old_settings, key, settings[key])

        old_settings.updated_by = actor
        old_settings.put()

        memcache.delete("system.settings")
    else:
        raise NotAllowedError()


class SystemSettings(ndb.Expando):
    updated = ndb.DateTimeProperty(auto_now=True)
    updated_by = ndb.UserProperty()


