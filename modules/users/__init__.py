import users


def user_http_put(actor, user_id, **kwargs):
    if "user" in kwargs:
        del kwargs["user"]

    users.user_create_or_update(actor=actor, user_id=user_id, **kwargs)


def user_http_post(actor, **kwargs):
    if "user" in kwargs:
        del kwargs["user"]

    users.user_create(actor=actor, **kwargs)


def user_http_delete(actor, user_id, **ignored):
    users.user_deactivate(actor=actor, user_id=user_id)


dependencies = [ ]

templates = { "{user_id}"      : "user_view",
              "{user_id}/edit" : "user_edit" }


types = { "user"      : users.user_load,
          "user_list" : users.user_list }


actions = { None        : { "POST"   : { "method"   : user_http_post,
                                         "redirect" : "/users/{email}" } },
            "{user_id}" : { "PUT"    : { "method"   : user_http_put },
                            "DELETE" : { "method"   : user_http_delete } } }



