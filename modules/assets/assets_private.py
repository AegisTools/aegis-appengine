import sys
import os
import logging
import urllib

from datetime import datetime, timedelta

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.arguments import *
from common.errors import *
from users.users import build_user_key

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import lib.parsedatetime


log = logging.getLogger("assets")


def key(asset_id):
    return ndb.Key(Asset, int(asset_id))


def create(actor, asset_id=None, asset_key=None, **kwargs):
    asset = Asset(key=asset_key or key(asset_id))
    asset.created_by = build_user_key(actor)
    asset.condition = "new"
    return update(actor, asset=asset, **kwargs)


def update(actor, asset_id=None, asset_key=None, asset=None, name=undefined,
           description=undefined, serial=undefined, condition=undefined, 
           cost=undefined, value=undefined, url=undefined, **ignored):
    asset = asset or (asset_key or key(asset_id)).get()

    # Update fields
    if is_defined(name):            asset.name = name
    if is_defined(url):             asset.url = url
    if is_defined(description):     asset.description = description
    if is_defined(serial):          asset.serial = serial
    if is_defined(condition):       asset.condition = condition
    if is_defined(cost) and cost:   asset.cost = float(cost)
    if is_defined(value) and value: asset.value = float(value)

    # Fix missing fields
    if not asset.name: asset.name = str(asset.key.id())

    asset.put()
    return asset


def delete(actor, asset_id=None, asset_key=None, asset=None):
    asset = asset or get(actor, asset_id, asset_key)
    asset.delete()


def get(actor, asset_id=None, asset_key=None, silent=False):
    result = (asset_key or key(asset_id)).get()

    if result:
        return result
    elif silent:
        return None
    else:
        raise NotFoundError()


def list(actor):
    return Asset.query()


def search(**ignored):
    pass


def check_out(actor, asset=None, asset_key=None, asset_id=None, checked_out_to=undefined,
              project=undefined, expected=undefined, timezoneoffset=None, **ignored):
    asset = asset or get(actor, asset_key=asset_key, asset_id=asset_id)
    if asset.checkout:
        raise IllegalError("Asset is already checked out")

    checkout = AssetCheckout(parent=asset.key)
    checkout.checked_out_by = build_user_key(actor)
    checkout.checked_out_to = build_user_key(actor)
    checkout.condition_out = asset.condition

    if is_defined(expected):
        if expected == "":
            expected = None
        else:
            if timezoneoffset:
                offset = timedelta(minutes=int(timezoneoffset))
                client_time = datetime.utcnow() - offset
                parsed_time = lib.parsedatetime.Calendar().parse(expected, client_time)
            else:
                offset = datetime.timedelta(0)
                parsed_time = lib.parsedatetime.Calendar().parse(expected)

            if parsed_time[1] == 1:
                checkout.expected = datetime(*parsed_time[0][:3]) + offset
            else:
                checkout.expected = datetime(*parsed_time[0][:6]) + offset

    if is_defined(checked_out_to) and checked_out_to: checkout.checked_out_to = build_user_key(checked_out_to)
    if is_defined(project) and project:               checkout.project = project
    checkout.put()

    asset.checkout = checkout.key
    asset.put()

    return checkout


def check_in(actor, asset=None, asset_key=None, asset_id=None, condition=undefined, **ignored):
    asset = asset or get(actor, asset_key=asset_key, asset_id=asset_id)
    if not asset.checkout:
        raise IllegalError("Asset is not checked out")

    checkout = asset.checkout.get()
    checkout.checked_in_by = build_user_key(actor)
    checkout.checked_in = datetime.now()
    checkout.condition_in = asset.condition

    if is_defined(condition): checkout.condition_in = condition
    checkout.put()

    asset.checkout = None
    asset.condition = checkout.condition_in
    asset.put()

    return checkout


valid_conditions = ["new", "excellent", "good", "poor", "unusable", "gone"]


class Asset(ndb.Model):
    name = ndb.StringProperty(required=True)
    url = ndb.StringProperty()
    description = ndb.StringProperty()
    serial = ndb.StringProperty()
    condition = ndb.StringProperty(required=True, default="new", choices=valid_conditions)
    cost = ndb.FloatProperty()
    value = ndb.FloatProperty()
    checkout = ndb.KeyProperty(kind='AssetCheckout')
    created_by = ndb.KeyProperty(kind='User')
    created = ndb.DateTimeProperty(auto_now_add=True)


class AssetCheckout(ndb.Model):
    # Check out fields
    checked_out_to = ndb.KeyProperty(kind='User', required=True)
    project = ndb.KeyProperty(kind='Project')
    checked_out = ndb.DateTimeProperty(auto_now_add=True)
    checked_out_by = ndb.KeyProperty(kind='User', required=True)
    condition_out = ndb.StringProperty(required=True, choices=valid_conditions)
    expected = ndb.DateTimeProperty()
    # Check in fields
    checked_in = ndb.DateTimeProperty()
    checked_in_by = ndb.KeyProperty(kind='User')
    condition_in = ndb.StringProperty(choices=valid_conditions)





