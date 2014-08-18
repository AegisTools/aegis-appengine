from users import *
from permissions import *


dependencies = []

templates = { "{user}"             : "user_view",
              "{user}/edit"        : "user_edit" }


types = { "user"            : load_user,
          "user_list"       : load_user_list }


actions = { "PUT"    : { "{user}" : create_user },
            "DELETE" : { "{user}" : delete_user } }



