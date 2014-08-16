from users import *
from permissions import *


dependencies = []

templates = { "{user}"             : "user_view",
              "{user}/edit"        : "user_edit",
              "{user}/permissions" : "permission_list" }


types = { "user"            : load_user,
          "user_list"       : load_user_list,
          "permission_list" : permission_list }


actions = { "PUT"    : { "{user}"                                  : create_user,
                         "{user}/permissions/{type}/{action}"      : permission_grant,
                         "{user}/permissions/{type}/{action}/{id}" : permission_grant },
            "DELETE" : { "{user}"                                  : delete_user,
                         "{user}/permissions/{type}/{action}"      : permission_revoke,
                         "{user}/permissions/{type}/{action}/{id}" : permission_revoke } }



