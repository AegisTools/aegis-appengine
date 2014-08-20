from tags import *


dependencies = [ "users" ]

templates = { "{tag}/*"      : "tag_view" }


types = { "tag"         : load_tag }


actions = { "PUT"    : { "{tag}/*" : tag_create },
            "DELETE" : { "{tag}/*" : tag_delete } }


