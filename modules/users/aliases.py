import users
import groups

def build_alias_key(alias_id):
    aliases_private.key(alias_id)


def alias_create(actor, *args, **kwargs):
    return alias_to_model(actor, aliases_private.create(actor, *args, **kwargs))


def alias_delete(actor, *args, **kwargs):
    return alias_to_model(actor, aliases_private.deactivate(actor, *args, **kwargs))


def alias_load(actor, alias_id=None, alias_key=None):
    return alias_to_model(actor, aliases_private.get(actor, alias_id=alias_id, alias_key=alias_key))


def alias_to_model(actor, alias):
    if not alias:
        return None

    return { 'address'       : alias.alias,
             'local_address' : alias.alias.email().split('@')[0],
             'user'          : users.user_load(actor, user_key=alias.user, silent=True),
             'group'         : groups.group_load(actor, group_key=alias.group, silent=True),
             'created_by'    : alias.created_by.id(),
             'created'       : alias.created }

import aliases_private

