from clients import *


dependencies = [ "users", "tags" ]

templates = { "{client_id}"      : "client_view",
              "{client_id}/edit" : "client_edit" }


types = { "client"      : client_load,
          "client_list" : client_list }


actions = { None          : { "POST"   : { "method"   : client_http_post,
                                           "redirect" : "/client/{id}" } },
            "{client_id}" : { "PUT"    : { "method"   : client_http_put },
                              "POST"   : { "method"   : client_http_post },
                              "DELETE" : { "method"   : client_http_delete } } }



