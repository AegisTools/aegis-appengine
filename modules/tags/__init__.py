from tags import *


dependencies = [ "users", "tags" ]

templates = { "{tag_ids}/*" : "tag_view" }


types = { "tag" : tag_load }


actions = { None          : { "POST"   : { "method"   : tag_http_post,
                                           "redirect" : "/tag/{id}" } },
            "{tag_ids}/*" : { "PUT"    : { "method"   : tag_http_put },
                              "POST"   : { "method"   : tag_http_post },
                              "DELETE" : { "method"   : tag_http_delete } } }


