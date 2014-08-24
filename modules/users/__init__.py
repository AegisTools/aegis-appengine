from users import *
from permissions import *


dependencies = [ ]

templates = { "{user_id}"      : "user_view",
              "{user_id}/edit" : "user_edit" }


types = { "user"      : user_load,
          "user_list" : user_list }


actions = { None        : { "POST"   : { "method"   : user_http_post,
                                         "redirect" : "/users/{email}" } },
            "{user_id}" : { "PUT"    : { "method"   : user_http_put },
                            "DELETE" : { "method"   : user_http_delete } } }



