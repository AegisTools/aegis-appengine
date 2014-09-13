from users import user_to_model
from groups import group_to_model


def group_members_add(*args, **kwargs):
    members_private.members_add(*args, **kwargs)


def group_members_remove(*args, **kwargs):
    members_private.members_remove(*args, **kwargs)


def group_members_clear(*args, **kwargs):
    members_private.members_clear(*args, **kwargs)


def group_members_list_users(actor, *args, **kwargs):
    return [user_to_model(actor, user, silent=True) for user in members_private.members_user_list(actor, *args, **kwargs)]


def group_members_list_groups(actor, *args, **kwargs):
    return [group_to_model(actor, group, silent=True) for group in members_private.members_group_list(actor, *args, **kwargs)]



import members_private

