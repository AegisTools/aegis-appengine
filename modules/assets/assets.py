import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.common import *
from users.permissions import permission_verify
from users.users import user_load


def build_asset_key(asset_id):
    return assets_private.key(asset_id)


def build_asset_keys(list):
    return build_keys(build_asset_key, list)


def asset_create(actor, *args, **kwargs):
    permission_verify(actor, "assets", "create")
    return asset_to_model(actor, assets_private.create(actor, *args, **kwargs))


def asset_create_or_update(actor, asset_id=None, asset_key=None, **kwargs):
    asset = assets_private.get(asset_id=asset_id, asset_key=asset_key)
    if asset:
        permission_verify(actor, "assets", "update")
        return asset_to_model(actor, assets_private.update(actor, asset=asset, **kwargs))
    else:
        permission_verify(actor, "assets", "create")
        return asset_to_model(actor, assets_private.create(actor, asset_id=asset_id, asset_key=asset_key, **kwargs))


def asset_update(actor, asset_id=None, asset_key=None, **kwargs):
    permission_verify(actor, "assets", "update")
    return asset_to_model(actor, assets_private.update(actor, asset_id=asset_id, asset_key=asset_key, **kwargs))


def asset_delete(actor, asset_id=None, asset_key=None, **kwargs):
    permission_verify(actor, "assets", "delete")
    return assets_private.delete(actor, asset_id=asset_id, asset_key=asset_key)


def asset_check_out(actor, asset_id=None, asset_key=None, **kwargs):
    permission_verify(actor, "assets", "check_in_out")
    return checkout_to_model(actor, assets_private.check_out(actor, asset_id=asset_id, asset_key=asset_key, **kwargs))


def asset_check_in(actor, asset_id=None, asset_key=None, **kwargs):
    permission_verify(actor, "assets", "check_in_out")
    return checkout_to_model(actor, assets_private.check_in(actor, asset_id=asset_id, asset_key=asset_key, **kwargs))


def asset_load(actor, asset_id=None, asset_key=None):
    permission_verify(actor, "assets", "read")
    return asset_to_model(actor, assets_private.get(actor, asset_id=asset_id, asset_key=asset_key))


def asset_list(actor):
    permission_verify(actor, "assets", "read")
    return [asset_to_model(actor, asset) for asset in assets_private.list(actor)]


def asset_search(actor, **kwargs):
    permission_verify(actor, "assets", "read")
    return [asset_to_model(actor, asset) for asset in assets_private.search(actor, **kwargs)]


def asset_to_model(viewer, asset):
    if not asset:
        return None

    checkout_data = None
    if asset.checkout:
        checkout_data = asset.checkout.get()

    history = assets_private.AssetCheckout.query(ancestor=asset.key).order(-assets_private.AssetCheckout.checked_out)

    return { 'id'             : asset.key.id(),
             'asset_id'       : asset.key.id(),
             'name'           : asset.name,
             'serial'         : asset.serial,
             'url'            : asset.url,
             'condition'      : asset.condition,
             'cost'           : asset.cost,
             'value'          : asset.value,
             'description'    : asset.description,
             'creator'        : user_load(viewer, user_key=asset.created_by, silent=True),
             'history'        : [checkout_to_model(viewer, checkout) for checkout in history],
             'checkout'       : checkout_to_model(viewer, checkout_data) }


def checkout_to_model(viewer, checkout):
    if not checkout:
        return None

    return { 'asset_id'             : checkout.key.parent().id(),
             'checked_out_to_email' : checkout.checked_out_to,
             'checked_out_to'       : user_load(viewer, user_key=checkout.checked_out_to, silent=True),
             'project'              : checkout.project,
             'checked_out'          : checkout.checked_out,
             'checked_out_by_email' : checkout.checked_out_by,
             'checked_out_by'       : user_load(viewer, user_key=checkout.checked_out_by, silent=True),
             'condition_out'        : checkout.condition_out,
             'expected'             : checkout.expected,
             'checked_in'           : checkout.checked_in,
             'checked_in_by_email'  : checkout.checked_in_by,
             'checked_in_by'        : user_load(viewer, user_key=checkout.checked_in_by, silent=True),
             'condition_in'         : checkout.condition_in }


import assets_private

