from issues import *


dependencies = [ "users", "tags", "remarks" ]

templates = { "{issue_id}"      : "view",
              "{issue_id}/edit" : "edit",
              "edit/{issue_id}" : "edit" }


types = { "issue"        : issue_load,
          "issue_search" : issue_search }


actions = { None         : { "POST"   : { "method"   : issue_http_post,
                                          "redirect" : "/issue/{id}" } },
            "{issue_id}" : { "PUT"    : { "method"   : issue_http_put },
                             "POST"   : { "method"   : issue_http_post } } }



