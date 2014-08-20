from projects import *


dependencies = [ "users" ]


templates = { "{project}/*" : "project_view" }


types = { "project" : load_project }


actions = { "PUT"    : { "{project}/*" : project_create },
            "DELETE" : { "{project}/*" : project_delete } }


