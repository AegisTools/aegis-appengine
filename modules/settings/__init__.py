from settings import *


dependencies = [ "users" ]


types = { "settings"             : settings_load,
          "oauth_token_exchange" : settings_oauth_token_exchange,
          "oauth2_google_url"    : settings_oauth2_google_url }


actions = { "site"      : { "POST" : { "method"   : settings_update_site,
                                       "redirect" : "/settings/site" } },
            "oauth"     : { "POST" : { "method"   : settings_update_oauth,
                                       "redirect" : "/settings/oauth" } },
            "directory" : { "POST" : { "method"   : settings_update_directory,
                                       "redirect" : "/settings/directory" } } }



