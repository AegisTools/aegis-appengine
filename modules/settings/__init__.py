from settings import *


dependencies = [ "users" ]


types = { "settings"             : settings_load,
          "oauth_token_exchange" : settings_oauth_token_exchange }


actions = { "site"  : { "POST" : { "method"   : settings_update_site,
                                   "redirect" : "/settings/site" } },
            "oauth" : { "POST" : { "method"   : settings_update_oauth,
                                   "redirect" : "/settings/oauth" } } }



