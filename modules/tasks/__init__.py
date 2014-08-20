from tasks import *


dependencies = [ "users" ]


templates = { "{task}/*" : "task_view" }


types = { "task" : load_task }


actions = { "PUT"    : { "{task}/*" : task_create },
            "DELETE" : { "{task}/*" : task_delete } }


