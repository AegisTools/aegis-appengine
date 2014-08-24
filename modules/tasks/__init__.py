from tasks import *


dependencies = [ "users", "tags" ]

templates = { "{task_ids}/*" : "task_view" }


types = { "task" : task_load }


actions = { None           : { "POST"   : { "method"   : task_http_post,
                                            "redirect" : "/task/{id}" } },
            "{task_ids}/*" : { "PUT"    : { "method"   : task_http_put },
                               "POST"   : { "method"   : task_http_post },
                               "DELETE" : { "method"   : task_http_delete } } }


