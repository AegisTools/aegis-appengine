from projects import *


dependencies = [ "users", "tags" ]

templates = { "{client_id}"                 : "project_view",
              "{client_id}/{project_ids}/*" : "project_view" }


types = { "project" : project_load }


actions = { "{client_id}"                 : { "POST"   : { "method"   : project_http_post,
                                                           "redirect" : "/project/{id}" } },
            "{client_id}/{project_ids}/*" : { "PUT"    : { "method"   : project_http_put },
                                              "POST"   : { "method"   : project_http_post },
                                              "DELETE" : { "method"   : project_http_delete } } }


