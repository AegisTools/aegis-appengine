def build_group_key(group_id):
    groups_private.key(group_id)


def group_create_or_update(actor, group_key=None, group_id=None, **kwargs):
    group = groups_private.get(actor, group_id, group_key, silent=True)
    if group:
        return group_update(actor, group=group, **kwargs)
    else:
        return group_create(actor, key=group_key, **kwargs)


def group_create(*args, **kwargs):
    return group_to_model(groups_private.create(*args, **kwargs))


def group_update(*args, **kwargs):
    return group_to_model(groups_private.update(*args, **kwargs))


def group_deactivate(*args, **kwargs):
    return group_to_model(groups_private.deactivate(*args, **kwargs))


def group_load(actor, group_id=None, group_key=None, silent=False):
    return group_to_model(groups_private.get(actor, group_id, group_key, silent=silent))


def group_list(actor):
    return [group_to_model(group) for group in groups_private.list(actor)]


def group_to_model(group):
    if not group:
        return None

    return { 'address'       : group.group.email(),
             'local_address' : group.group.email().split("@")[0],
             'name'          : group.name,
             'notes'         : group.notes,
             'active'        : group.active,
             'created_by'    : group.created_by.id(),
             'created'       : group.created,
             'updated_by'    : group.updated_by.id(),
             'updated'       : group.updated }


import groups_private

