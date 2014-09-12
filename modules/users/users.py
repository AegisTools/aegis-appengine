def build_user_key(user_id):
    return users_private.key(user_id)


def user_create_or_update(actor, user_id=None, user_key=None, **kwargs):
    user = users_private.get(actor, user_id, user_key, silent=True)
    if user:
        return user_update(actor, user=user, **kwargs)
    else:
        return user_create(actor, user_key=user_key, **kwargs)


def user_create(actor, *args, **kwargs):
    return user_to_model(actor, users_private.create(actor, *args, **kwargs))


def user_update(actor, *args, **kwargs):
    return user_to_model(actor, users_private.update(actor, *args, **kwargs))


def user_deactivate(actor, *args, **kwargs):
    return user_to_model(actor, users_private.deactivate(actor, *args, **kwargs))


def user_load(actor, user_id=None, user_key=None, silent=False):
    return user_to_model(actor, users_private.get(actor, user_id, user_key, silent=silent))


def user_list(actor):
    return [user_to_model(actor, user) for user in users_private.list(actor)]


def user_to_model(actor, user):
    if not user:
        return None

    return { 'key'          : user.key.id(),
             'first_name'   : user.first_name,
             'last_name'    : user.last_name,
             'display_name' : (user.last_name or "Unknown") + ", " + (user.first_name or "Unknown"),
             'active'       : user.active,
             'created_by'   : user.created_by.id(),
             'created'      : user.created,
             'updated_by'   : user.updated_by.id(),
             'updated'      : user.updated }


import users_private

