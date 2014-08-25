from issues import *


dependencies = [ "users", "tags", "remarks" ]

templates = { "{issue_id}"      : "issue_view",
              "{issue_id}/edit" : "issue_edit" }


types = { "issue"      : issue_load,
          "issue_list" : issue_list }


actions = { None         : { "POST"   : { "method"   : issue_http_post,
                                          "redirect" : "/issue/{id}" } },
            "{issue_id}" : { "PUT"    : { "method"   : issue_http_put },
                             "POST"   : { "method"   : issue_http_post } } }



