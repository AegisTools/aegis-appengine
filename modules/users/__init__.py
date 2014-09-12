from users import *


def user_http_put(actor, user_id, **kwargs):
    if "user" in kwargs:
        del kwargs["user"]

    users.create_or_update(actor=actor, user_id=user_id, **kwargs)


def user_http_post(actor, **kwargs):
    if "user" in kwargs:
        del kwargs["user"]

    users.create(actor=actor, **kwargs)


def user_http_delete(actor, user_id, **ignored):
    users.delete(actor=actor, user_id=user_id)


dependencies = [ ]

templates = { "{user_id}"      : "user_view",
              "{user_id}/edit" : "user_edit" }


types = { "user"      : user_load,
          "user_list" : user_list }


actions = { None        : { "POST"   : { "method"   : user_http_post,
                                         "redirect" : "/users/{email}" } },
            "{user_id}" : { "PUT"    : { "method"   : user_http_put },
                            "DELETE" : { "method"   : user_http_delete } } }



